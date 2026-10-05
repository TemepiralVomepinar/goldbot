//+------------------------------------------------------------------+
//| NoiseAreaMomentum_Prop.mq5                                        |
//| Intraday "Noise Area" momentum on index CFDs (NAS100/US100).      |
//| Rules: Zarattini, Aziz, Barbon - "Beat the Market" (SSRN 4824172) |
//|   - noise area = 14-day average |move from open| per time of day  |
//|   - decisions only at HH:00 / HH:30, first one 30 min after open  |
//|   - long above upper band, short below lower band                 |
//|   - exit: price crosses max(UB,VWAP) (long) / min(LB,VWAP) (short)|
//| Added for prop firms: vol-targeted + risk-capped sizing, hard SL, |
//|   daily / max loss guards, profit target lock, spread + news      |
//|   filters. NOT backtested by the author: test before use.         |
//+------------------------------------------------------------------+
#property copyright "goldbot"
#property version   "1.00"
#property strict

#include <Trade/Trade.mqh>

input group "=== Session (BROKER SERVER time; NY 09:30-16:00) ==="
input int    InpOpenHour            = 16;     // US cash open hour on server clock (NY-close servers: 16:30)
input int    InpOpenMin             = 30;
input int    InpCloseHour           = 23;     // US cash close hour on server clock (23:00)
input int    InpCloseMin            = 0;
input int    InpFlatMinBeforeClose  = 5;      // flatten this many minutes before the close
input int    InpFirstDecisionMin    = 30;     // first decision N minutes after the open
input int    InpLastDecisionMin     = 360;    // no new entries after this many minutes from the open

input group "=== Strategy (paper defaults) ==="
input int    InpLookback            = 14;     // days for the noise area and the volatility
input double InpVolMult             = 1.0;    // noise-area multiplier (paper base 1.0; best in hindsight ~1.5)
input bool   InpAllowLong           = true;
input bool   InpAllowShort          = true;

input group "=== Position sizing / risk ==="
input double InpRiskPerTradePct     = 0.50;   // max loss at the hard SL, % of equity
input double InpTargetDailyVolPct   = 0.80;   // paper-style volatility targeting (daily vol of the position)
input double InpMaxLeverage         = 3.0;    // cap on notional / equity
input double InpHardStopMult        = 1.5;    // hard SL distance = this x distance to the strategy stop
input double InpMinStopPct          = 0.15;   // minimum hard SL distance, % of price
input double InpMaxStopPct          = 1.50;   // skip the trade if the hard SL would be farther than this
input double InpMaxLots             = 5.0;
input int    InpMaxSpreadPoints     = 0;      // 0 = no spread filter

input group "=== Prop-firm guards ==="
input double InpInitialBalance      = 0;      // 0 = balance when the EA starts (LIVE: set the real starting balance)
input double InpSoftDailyLossPct    = 2.5;    // flatten + stop for the day (firm limit 4%)
input double InpSoftMaxLossPct      = 6.5;    // flatten + stop for good (firm limit 10%)
input double InpTargetPct           = 8.0;    // 0 = off; on reaching it: flatten and stop (use 8 for phase 1, 6 for phase 2)
input double InpStopDayProfitPct    = 0.0;    // 0 = off; stop for the day after this gain (helps consistency rules)
input int    InpDayResetHour        = 0;      // server hour at which the firm's daily loss resets

input group "=== News (live only: the MT5 tester has no calendar) ==="
input bool   InpUseNewsFilter       = true;
input int    InpNewsMinutes         = 2;      // block entries and flatten within +/- N minutes of high-impact USD news
input string InpNewsCurrency        = "USD";

input group "=== Execution ==="
input int    InpDeviationPoints     = 30;     // max slippage accepted on market orders
input long   InpMagic               = 880011;
input string InpComment             = "NAM";

CTrade   trade;
datetime g_lastBar = 0, g_sessDay = 0, g_openTime = 0, g_vwapUpTo = 0;
double   g_open = 0, g_prevClose = 0, g_dailyVol = 0, g_sig[16];
double   g_sumPV = 0, g_sumV = 0, g_dayRef = 0, g_initBal = 0;
bool     g_ready = false, g_haltDay = false, g_haltAll = false;
int      g_dayKey = -1;

//+------------------------------------------------------------------+
int OnInit()
{
   if(!SymbolSelect(_Symbol, true)) return INIT_FAILED;
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(InpDeviationPoints);
   trade.SetTypeFillingBySymbol(_Symbol);
   g_initBal = (InpInitialBalance > 0) ? InpInitialBalance : AccountInfoDouble(ACCOUNT_BALANCE);
   ArrayInitialize(g_sig, 0.0);
   Print("NAM started on ", _Symbol, " initial balance ", DoubleToString(g_initBal, 2),
         ". Session on server clock ", InpOpenHour, ":", InpOpenMin, " - ", InpCloseHour, ":", InpCloseMin);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) { Comment(""); }

//+------------------------------------------------------------------+
void OnTick()
{
   Guards();
   datetime bt = iTime(_Symbol, PERIOD_M1, 0);
   if(bt == 0 || bt == g_lastBar) return;
   g_lastBar = bt;
   OnNewBar(bt);
}

//+------------------------------------------------------------------+
//| account-level protection, checked on every tick                  |
//+------------------------------------------------------------------+
void Guards()
{
   double eq = AccountInfoDouble(ACCOUNT_EQUITY), bal = AccountInfoDouble(ACCOUNT_BALANCE);
   int key = (int)((TimeCurrent() - (datetime)(InpDayResetHour * 3600)) / 86400);
   if(key != g_dayKey) { g_dayKey = key; g_dayRef = MathMax(eq, bal); g_haltDay = false; }
   if(g_haltAll) return;

   if(!g_haltDay && eq <= g_dayRef * (1.0 - InpSoftDailyLossPct / 100.0))
   { CloseAll("daily soft loss limit"); g_haltDay = true; }
   if(eq <= g_initBal * (1.0 - InpSoftMaxLossPct / 100.0))
   { CloseAll("max soft loss limit"); g_haltAll = true; }
   if(InpTargetPct > 0 && eq >= g_initBal * (1.0 + InpTargetPct / 100.0))
   { CloseAll("profit target reached"); g_haltAll = true; }
   if(!g_haltDay && InpStopDayProfitPct > 0 && eq >= g_dayRef * (1.0 + InpStopDayProfitPct / 100.0))
   { CloseAll("daily profit cap"); g_haltDay = true; }
}

//+------------------------------------------------------------------+
void OnNewBar(datetime bt)
{
   int tod = (int)(bt % 86400);
   datetime day = bt - (datetime)tod;
   int openSec = InpOpenHour * 3600 + InpOpenMin * 60;
   int closeSec = InpCloseHour * 3600 + InpCloseMin * 60;

   if(day != g_sessDay) { g_sessDay = day; g_ready = false; g_open = 0; g_sumPV = 0; g_sumV = 0; g_vwapUpTo = 0; }

   if(tod < openSec || tod >= closeSec)
   {
      if(HasPos()) CloseAll("outside session");
      return;
   }
   g_openTime = day + (datetime)openSec;

   if(g_open == 0.0)                                   // first bar we see in this session
   {
      int sho = iBarShift(_Symbol, PERIOD_M1, g_openTime, true);
      if(sho < 0) return;
      g_open = iOpen(_Symbol, PERIOD_M1, sho);
      g_ready = ComputeStats(day, openSec, closeSec);
      g_sumPV = 0; g_sumV = 0;
      for(int i = sho; i >= 1; i--) AddBarToVwap(i);   // mid-session attach: rebuild VWAP from history
      g_vwapUpTo = bt - 60;
   }
   else if(g_vwapUpTo < bt - 60)
   {
      AddBarToVwap(1);
      g_vwapUpTo = bt - 60;
   }

   if(InpUseNewsFilter && HasPos() && NewsBlocked(bt)) CloseAll("news window");

   if(tod >= closeSec - InpFlatMinBeforeClose * 60)
   {
      if(HasPos()) CloseAll("end of day");
      return;
   }
   if(!g_ready || g_haltDay || g_haltAll) { ShowState(0, 0, 0); return; }

   int off = tod - openSec;
   if(off < InpFirstDecisionMin * 60 || off % 1800 != 0) return;
   Decide(bt, off / 1800, off);
}

void AddBarToVwap(int shift)
{
   double tp = (iHigh(_Symbol, PERIOD_M1, shift) + iLow(_Symbol, PERIOD_M1, shift) + iClose(_Symbol, PERIOD_M1, shift)) / 3.0;
   double v = (double)iTickVolume(_Symbol, PERIOD_M1, shift);
   if(v <= 0) v = 1;
   g_sumPV += tp * v;
   g_sumV += v;
}

//+------------------------------------------------------------------+
//| noise area per time-of-day and daily volatility from M1 history   |
//+------------------------------------------------------------------+
bool ComputeStats(datetime day, int openSec, int closeSec)
{
   int slots = (closeSec - openSec) / 1800;
   if(slots > 15) slots = 15;
   double sumMove[16];
   ArrayInitialize(sumMove, 0.0);
   double closes[];
   ArrayResize(closes, 0);
   int cnt = 0;

   for(int k = 1; k <= 70 && cnt < InpLookback + 1; k++)
   {
      datetime ot = day - (datetime)(k * 86400) + (datetime)openSec;
      int sho = iBarShift(_Symbol, PERIOD_M1, ot, true);
      if(sho < 0) continue;
      double opx = iOpen(_Symbol, PERIOD_M1, sho);
      if(opx <= 0) continue;

      double mv[16];
      ArrayInitialize(mv, 0.0);
      bool ok = true;
      double cl = 0;
      for(int j = 1; j <= slots; j++)
      {
         int sh = iBarShift(_Symbol, PERIOD_M1, ot + (datetime)(j * 1800 - 60), true);   // bar that ends at slot time
         if(sh < 0) { ok = false; break; }
         double px = iClose(_Symbol, PERIOD_M1, sh);
         mv[j] = MathAbs(px / opx - 1.0);
         if(j == slots) cl = px;
      }
      if(!ok || cl <= 0) continue;

      int n = ArraySize(closes);
      ArrayResize(closes, n + 1);
      closes[n] = cl;
      if(cnt < InpLookback) for(int j = 1; j <= slots; j++) sumMove[j] += mv[j];
      cnt++;
   }

   int used = MathMin(cnt, InpLookback);
   if(used < 5) { Print("NAM: not enough history days (", cnt, ")"); return false; }
   for(int j = 1; j <= slots; j++) g_sig[j] = sumMove[j] / used;
   g_prevClose = closes[0];

   int nr = MathMin(cnt - 1, InpLookback);              // close-to-close returns for the volatility
   if(nr < 4) return false;
   double m = 0;
   double r[];
   ArrayResize(r, nr);
   for(int i = 0; i < nr; i++) { r[i] = closes[i] / closes[i + 1] - 1.0; m += r[i]; }
   m /= nr;
   double s2 = 0;
   for(int i = 0; i < nr; i++) s2 += (r[i] - m) * (r[i] - m);
   g_dailyVol = MathSqrt(s2 / (nr - 1));
   return (g_dailyVol > 0);
}

//+------------------------------------------------------------------+
void Decide(datetime bt, int slot, int offSec)
{
   double P = iClose(_Symbol, PERIOD_M1, 1);                     // price at the slot time
   double sig = g_sig[slot];
   if(sig <= 0 || P <= 0) return;

   double up = MathMax(g_open, g_prevClose) * (1.0 + InpVolMult * sig);
   double lo = MathMin(g_open, g_prevClose) * (1.0 - InpVolMult * sig);
   double vwap = (g_sumV > 0) ? g_sumPV / g_sumV : P;
   ShowState(up, lo, vwap);

   ulong tk; long type;
   if(GetPos(tk, type))
   {
      if(type == POSITION_TYPE_BUY)  { if(P < MathMax(up, vwap)) CloseAll("long stop (band/VWAP)"); }
      else                           { if(P > MathMin(lo, vwap)) CloseAll("short stop (band/VWAP)"); }
      if(HasPos()) return;
   }

   if(offSec > InpLastDecisionMin * 60) return;
   if(InpUseNewsFilter && NewsBlocked(bt)) return;
   if(InpMaxSpreadPoints > 0 && SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) > InpMaxSpreadPoints) return;

   if(P > up && InpAllowLong)        Enter(true, P, MathMax(up, vwap));
   else if(P < lo && InpAllowShort)  Enter(false, P, MathMin(lo, vwap));
}

//+------------------------------------------------------------------+
void Enter(bool isBuy, double P, double stopLevel)
{
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double px = isBuy ? ask : bid;
   if(px <= 0) return;

   double D = MathMax(MathAbs(P - stopLevel) * InpHardStopMult, px * InpMinStopPct / 100.0);
   double minLvl = (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point + (ask - bid);
   D = MathMax(D, minLvl);
   if(D > px * InpMaxStopPct / 100.0) { Print("NAM: skip, hard stop too far (", DoubleToString(D, 1), ")"); return; }
   double sl = NormalizeDouble(isBuy ? px - D : px + D, _Digits);

   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(tv <= 0 || ts <= 0) return;
   double pv = tv / ts;                                          // account currency per 1.0 price unit per lot

   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   double lev = MathMin(InpMaxLeverage, (InpTargetDailyVolPct / 100.0) / MathMax(g_dailyVol, 1e-6));
   double lotsVol = eq * lev / (px * pv);
   double lotsRisk = eq * InpRiskPerTradePct / 100.0 / (D * pv);
   double lots = NormVol(MathMin(lotsVol, lotsRisk));
   if(lots <= 0) { Print("NAM: skip, size below the minimum lot"); return; }

   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   while(lots > 0)                                               // margin check
   {
      double margin = 0;
      if(OrderCalcMargin(isBuy ? ORDER_TYPE_BUY : ORDER_TYPE_SELL, _Symbol, lots, px, margin) &&
         margin < AccountInfoDouble(ACCOUNT_MARGIN_FREE) * 0.8) break;
      lots -= step;
      lots = NormVol(lots);
   }
   if(lots <= 0) { Print("NAM: skip, not enough free margin"); return; }

   bool ok = isBuy ? trade.Buy(lots, _Symbol, 0.0, sl, 0.0, InpComment) : trade.Sell(lots, _Symbol, 0.0, sl, 0.0, InpComment);
   Print("NAM ", (isBuy ? "BUY " : "SELL "), DoubleToString(lots, 2), " @", DoubleToString(px, _Digits), " SL ", DoubleToString(sl, _Digits),
         " lev ", DoubleToString(lev, 2), " dailyVol ", DoubleToString(g_dailyVol * 100, 2), "% -> ", (ok ? "ok" : "FAILED ") ,
         (ok ? "" : IntegerToString(trade.ResultRetcode())));
}

double NormVol(double lots)
{
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double mn = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double mx = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   if(step <= 0) return 0;
   lots = MathFloor(lots / step + 1e-9) * step;
   if(lots < mn) return 0;
   return MathMin(lots, MathMin(mx, InpMaxLots));
}

//+------------------------------------------------------------------+
bool GetPos(ulong &ticket, long &type)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t == 0 || !PositionSelectByTicket(t)) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      ticket = t;
      type = PositionGetInteger(POSITION_TYPE);
      return true;
   }
   return false;
}

bool HasPos() { ulong t; long ty; return GetPos(t, ty); }

void CloseAll(string why)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t == 0 || !PositionSelectByTicket(t)) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol || PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      if(trade.PositionClose(t)) Print("NAM close (", why, ")");
      else Print("NAM close FAILED (", why, ") retcode ", trade.ResultRetcode());
   }
}

//+------------------------------------------------------------------+
//| high-impact news around time t (live only)                       |
//+------------------------------------------------------------------+
bool NewsBlocked(datetime t)
{
   if(!InpUseNewsFilter || MQLInfoInteger(MQL_TESTER)) return false;
   MqlCalendarValue v[];
   datetime from = t - (datetime)(InpNewsMinutes * 60), to = t + (datetime)(InpNewsMinutes * 60);
   if(!CalendarValueHistory(v, from, to, NULL, InpNewsCurrency)) return false;
   for(int i = 0; i < ArraySize(v); i++)
   {
      MqlCalendarEvent ev;
      if(CalendarEventById(v[i].event_id, ev) && ev.importance == CALENDAR_IMPORTANCE_HIGH) return true;
   }
   return false;
}

void ShowState(double up, double lo, double vwap)
{
   Comment("NAM  ready=", g_ready, "  haltDay=", g_haltDay, "  haltAll=", g_haltAll,
           "\nopen ", DoubleToString(g_open, _Digits), "  prevClose ", DoubleToString(g_prevClose, _Digits),
           "\nUB ", DoubleToString(up, _Digits), "  LB ", DoubleToString(lo, _Digits), "  VWAP ", DoubleToString(vwap, _Digits),
           "\ndailyVol ", DoubleToString(g_dailyVol * 100, 2), "%   dayRefEquity ", DoubleToString(g_dayRef, 2),
           "\nequity ", DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY), 2));
}
//+------------------------------------------------------------------+
