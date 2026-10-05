//+------------------------------------------------------------------+
//| LastHalfHourMomentum_Prop.mq5                                     |
//| "Market intraday momentum": the return from the previous close    |
//| to 30 minutes before today's close predicts the last half hour.   |
//| Baltussen, Da, Lammers, Martens, "Hedging demand and market       |
//| intraday momentum" (SSRN 3760365): 60+ futures, 1974-2020, equity |
//| index futures out-of-sample R2 ~2.9%, gross Sharpe 0.87-1.73;     |
//| Gao, Han, Li, Zhou (SSRN 2440866). One trade per day.             |
//| Rule: at close-30min go long if rROD>0, short if rROD<0, exit at  |
//| the cash close (the paper finds NO predictability after 16:00 ET).|
//| Prop-firm guards as in NoiseAreaMomentum_Prop. NOT backtested.    |
//+------------------------------------------------------------------+
#property copyright "goldbot"
#property version   "1.00"
#property strict

#include <Trade/Trade.mqh>

input group "=== Session (BROKER SERVER time; US cash close 16:00 New York) ==="
input int    InpCloseHour           = 23;     // US cash close on the server clock (NY-close servers: 23:00)
input int    InpCloseMin            = 0;
input int    InpEntryMinBeforeClose = 30;     // paper: last 30 minutes
input int    InpExitMinBeforeClose  = 2;      // leave before the close (no predictability after 16:00 ET)

input group "=== Signal ==="
input double InpMinSignalPct        = 0.0;    // ignore |rROD| below this %, 0 = pure paper rule (sign only)
input int    InpLookbackDays        = 20;     // days used to measure the typical last-30-minute move
input bool   InpAllowLong           = true;
input bool   InpAllowShort          = true;

enum ENUM_RISK_MODE { MODE_CUSTOM = 0, MODE_SAFE = 1, MODE_FAST = 2 };
input group "=== Risk preset ==="
input ENUM_RISK_MODE InpMode        = MODE_SAFE;   // SAFE / FAST override the risk inputs below; CUSTOM uses them as typed

input group "=== Position sizing / risk (used when mode = CUSTOM) ==="
input double InpRiskPerTradePct     = 0.50;   // loss at the hard SL, % of equity
input double InpStopMult            = 2.0;    // hard SL distance = this x typical last-30-minute move
input double InpMinStopPct          = 0.10;   // minimum hard SL distance, % of price
input double InpMaxStopPct          = 1.00;   // skip the trade if the SL would be farther
input double InpMaxLots             = 5.0;
input int    InpMaxSpreadPoints     = 0;      // 0 = no spread filter

input group "=== Prop-firm guards ==="
input double InpInitialBalance      = 0;      // 0 = balance when the EA starts (LIVE: set the real starting balance)
input double InpSoftDailyLossPct    = 2.5;
input double InpSoftMaxLossPct      = 6.5;
input double InpTargetPct           = 8.0;    // 0 = off; flatten and stop on reaching it (8 phase 1, 6 phase 2)
input double InpStopDayProfitPct    = 0.0;
input int    InpDayResetHour        = 0;

input group "=== News (live only) ==="
input bool   InpUseNewsFilter       = true;
input int    InpNewsMinutes         = 2;
input string InpNewsCurrency        = "USD";

input group "=== Execution ==="
input int    InpDeviationPoints     = 30;
input long   InpMagic               = 880022;
input string InpComment             = "LH30";

CTrade   trade;
datetime g_lastBar = 0, g_sessDay = 0;
bool     g_tradedToday = false, g_haltDay = false, g_haltAll = false;
int      g_dayKey = -1;
double   g_dayRef = 0, g_initBal = 0, g_risk, g_softDaily, g_softMax;
double   g_lastROD = 0, g_lastLH = 0;

//+------------------------------------------------------------------+
int OnInit()
{
   if(!SymbolSelect(_Symbol, true)) return INIT_FAILED;
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(InpDeviationPoints);
   trade.SetTypeFillingBySymbol(_Symbol);
   g_initBal = (InpInitialBalance > 0) ? InpInitialBalance : AccountInfoDouble(ACCOUNT_BALANCE);
   g_risk = InpRiskPerTradePct; g_softDaily = InpSoftDailyLossPct; g_softMax = InpSoftMaxLossPct;
   if(InpMode == MODE_SAFE) { g_risk = 0.50; g_softDaily = 2.5; g_softMax = 6.5; }
   if(InpMode == MODE_FAST) { g_risk = 1.50; g_softDaily = 3.2; g_softMax = 7.5; }
   Print("LH30 started on ", _Symbol, ", mode ", EnumToString(InpMode), ", risk/trade ", g_risk, "%, initial balance ",
         DoubleToString(g_initBal, 2), ", cash close on server clock ", InpCloseHour, ":", InpCloseMin);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) { Comment(""); }

void OnTick()
{
   Guards();
   datetime bt = iTime(_Symbol, PERIOD_M1, 0);
   if(bt == 0 || bt == g_lastBar) return;
   g_lastBar = bt;
   OnNewBar(bt);
}

//+------------------------------------------------------------------+
void Guards()
{
   double eq = AccountInfoDouble(ACCOUNT_EQUITY), bal = AccountInfoDouble(ACCOUNT_BALANCE);
   int key = (int)((TimeCurrent() - (datetime)(InpDayResetHour * 3600)) / 86400);
   if(key != g_dayKey) { g_dayKey = key; g_dayRef = MathMax(eq, bal); g_haltDay = false; }
   if(g_haltAll) return;

   if(!g_haltDay && eq <= g_dayRef * (1.0 - g_softDaily / 100.0)) { CloseAll("daily soft loss limit"); g_haltDay = true; }
   if(eq <= g_initBal * (1.0 - g_softMax / 100.0))                { CloseAll("max soft loss limit");   g_haltAll = true; }
   if(InpTargetPct > 0 && eq >= g_initBal * (1.0 + InpTargetPct / 100.0)) { CloseAll("profit target reached"); g_haltAll = true; }
   if(!g_haltDay && InpStopDayProfitPct > 0 && eq >= g_dayRef * (1.0 + InpStopDayProfitPct / 100.0))
   { CloseAll("daily profit cap"); g_haltDay = true; }
}

//+------------------------------------------------------------------+
void OnNewBar(datetime bt)
{
   int tod = (int)(bt % 86400);
   datetime day = bt - (datetime)tod;
   int closeSec = InpCloseHour * 3600 + InpCloseMin * 60;
   int entrySec = closeSec - InpEntryMinBeforeClose * 60;
   int exitSec  = closeSec - InpExitMinBeforeClose * 60;

   if(day != g_sessDay) { g_sessDay = day; g_tradedToday = false; }

   if(HasPos() && (tod >= exitSec || tod < entrySec - 3600)) { CloseAll("exit before the close"); return; }

   if(g_tradedToday || g_haltDay || g_haltAll) return;
   if(tod < entrySec || tod >= entrySec + 5 * 60) return;       // first bars of the entry window only

   g_tradedToday = true;                                        // one attempt per day
   if(InpUseNewsFilter && NewsBlocked(bt)) { Print("LH30: news window, skip"); return; }
   if(InpMaxSpreadPoints > 0 && SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) > InpMaxSpreadPoints) { Print("LH30: spread too wide, skip"); return; }

   double rod, lhMove;
   if(!ComputeSignal(day, entrySec, closeSec, rod, lhMove)) return;
   g_lastROD = rod; g_lastLH = lhMove;
   ShowState();

   if(MathAbs(rod) * 100.0 < InpMinSignalPct) { Print("LH30: signal too small (", DoubleToString(rod * 100, 3), "%)"); return; }
   if(rod > 0 && InpAllowLong)       Enter(true, lhMove);
   else if(rod < 0 && InpAllowShort) Enter(false, lhMove);
}

//+------------------------------------------------------------------+
//| rROD = P(close-30min) / previous close - 1 ; typical LH move      |
//+------------------------------------------------------------------+
bool ComputeSignal(datetime day, int entrySec, int closeSec, double &rod, double &lhMove)
{
   double P = iClose(_Symbol, PERIOD_M1, 1);                    // price at close-30min
   double prevClose = 0;
   for(int k = 1; k <= 10; k++)
   {
      int sh = iBarShift(_Symbol, PERIOD_M1, day - (datetime)(k * 86400) + (datetime)(closeSec - 60), true);
      if(sh >= 0) { prevClose = iClose(_Symbol, PERIOD_M1, sh); break; }
   }
   if(P <= 0 || prevClose <= 0) { Print("LH30: missing price history"); return false; }
   rod = P / prevClose - 1.0;

   double sum = 0; int n = 0;
   for(int k = 1; k <= 60 && n < InpLookbackDays; k++)
   {
      datetime d = day - (datetime)(k * 86400);
      int s1 = iBarShift(_Symbol, PERIOD_M1, d + (datetime)(entrySec - 60), true);
      int s2 = iBarShift(_Symbol, PERIOD_M1, d + (datetime)(closeSec - 60), true);
      if(s1 < 0 || s2 < 0) continue;
      double c1 = iClose(_Symbol, PERIOD_M1, s1), c2 = iClose(_Symbol, PERIOD_M1, s2);
      if(c1 <= 0 || c2 <= 0) continue;
      sum += MathAbs(c2 / c1 - 1.0);
      n++;
   }
   if(n < 5) { Print("LH30: not enough history days (", n, ")"); return false; }
   lhMove = sum / n;
   return true;
}

//+------------------------------------------------------------------+
void Enter(bool isBuy, double lhMove)
{
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double px = isBuy ? ask : bid;
   if(px <= 0) return;

   double D = MathMax(px * lhMove * InpStopMult, px * InpMinStopPct / 100.0);
   double minLvl = (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point + (ask - bid);
   D = MathMax(D, minLvl);
   if(D > px * InpMaxStopPct / 100.0) { Print("LH30: skip, stop too far (", DoubleToString(D, 1), ")"); return; }
   double sl = NormalizeDouble(isBuy ? px - D : px + D, _Digits);

   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(tv <= 0 || ts <= 0) return;
   double pv = tv / ts;
   double lots = NormVol(AccountInfoDouble(ACCOUNT_EQUITY) * g_risk / 100.0 / (D * pv));
   if(lots <= 0) { Print("LH30: skip, size below the minimum lot"); return; }

   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   while(lots > 0)
   {
      double margin = 0;
      if(OrderCalcMargin(isBuy ? ORDER_TYPE_BUY : ORDER_TYPE_SELL, _Symbol, lots, px, margin) &&
         margin < AccountInfoDouble(ACCOUNT_MARGIN_FREE) * 0.8) break;
      lots = NormVol(lots - step);
   }
   if(lots <= 0) { Print("LH30: skip, not enough free margin"); return; }

   bool ok = isBuy ? trade.Buy(lots, _Symbol, 0.0, sl, 0.0, InpComment) : trade.Sell(lots, _Symbol, 0.0, sl, 0.0, InpComment);
   Print("LH30 ", (isBuy ? "BUY " : "SELL "), DoubleToString(lots, 2), " @", DoubleToString(px, _Digits), " SL ", DoubleToString(sl, _Digits),
         " rROD ", DoubleToString(g_lastROD * 100, 3), "% typical LH move ", DoubleToString(lhMove * 100, 3), "% -> ",
         (ok ? "ok" : "FAILED "), (ok ? "" : IntegerToString(trade.ResultRetcode())));
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
bool HasPos()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t == 0 || !PositionSelectByTicket(t)) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == InpMagic) return true;
   }
   return false;
}

void CloseAll(string why)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t == 0 || !PositionSelectByTicket(t)) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol || PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      if(trade.PositionClose(t)) Print("LH30 close (", why, ")");
      else Print("LH30 close FAILED (", why, ") retcode ", trade.ResultRetcode());
   }
}

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

void ShowState()
{
   Comment("LH30  haltDay=", g_haltDay, "  haltAll=", g_haltAll,
           "\nrROD ", DoubleToString(g_lastROD * 100, 3), "%   typical last-30min move ", DoubleToString(g_lastLH * 100, 3), "%",
           "\nequity ", DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY), 2), "   dayRefEquity ", DoubleToString(g_dayRef, 2));
}
//+------------------------------------------------------------------+
