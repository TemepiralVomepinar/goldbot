//+------------------------------------------------------------------+
//| DriftVWAPPullback_Prop.mq5                                        |
//| "Drift VWAP Pullback" as described by Matteo Conti in the video   |
//| "Ex-Market Maker Shows the Exact VWAP Setup That Gets Traders     |
//| Funded" (youtube wm4A6qo0g3I). Rules taken from the transcript:   |
//|  - VWAP anchored at the 09:30 ET open, computed on 15-min bars    |
//|  - every 15 min: LONG trend if price > VWAP, VWAP rising vs the   |
//|    previous 15-min bar, price up >= 0.1% over the past hour;      |
//|    SHORT is the mirror                                            |
//|  - no trading 09:30-10:30 ET                                      |
//|  - trigger: first red 5-min candle (long) / green (short) after   |
//|    the trend conditions hold; market order at the next open       |
//|  - long SL 80 / TP 40 points; short SL 80 / TP 50 points          |
//|  - one position, max 4 trades/day, stop after 2 losses, no new    |
//|    trades after 15:30 ET, flat at 15:55 ET                        |
//| The video's results are NOT independently verified. Prop guards   |
//| and sizing added by me. NOT backtested by the author.             |
//+------------------------------------------------------------------+
#property copyright "goldbot"
#property version   "1.00"
#property strict

#include <Trade/Trade.mqh>

input group "=== Session (BROKER SERVER time; NY 09:30-16:00) ==="
input int    InpOpenHour            = 16;     // US cash open on the server clock (NY-close servers: 16:30)
input int    InpOpenMin             = 30;
input int    InpNoTradeMinAfterOpen = 60;     // video: no trades 09:30-10:30 ET
input int    InpLastEntryHour       = 22;     // no new trades after 15:30 ET = 22:30 on a NY-close server
input int    InpLastEntryMin        = 30;
input int    InpFlatHour            = 22;     // close everything at 15:55 ET = 22:55
input int    InpFlatMin             = 55;

input group "=== Strategy (as in the video) ==="
input double InpMinMovePct          = 0.10;   // price move over the past hour (4 x 15-min bars), in %
input double InpStopPoints          = 80.0;   // index points
input double InpTpLongPoints        = 40.0;
input double InpTpShortPoints       = 50.0;
input int    InpMaxTradesPerDay     = 4;
input int    InpMaxLossesPerDay     = 2;
input bool   InpLossesConsecutive   = true;   // video: "two consecutive losing trades" (set false = two losses in total)
input bool   InpRearmEveryEval      = true;   // true: each 15-min check that still holds re-arms one trigger
input bool   InpAllowLong           = true;
input bool   InpAllowShort          = true;

enum ENUM_RISK_MODE { MODE_CUSTOM = 0, MODE_SAFE = 1, MODE_FAST = 2 };
input group "=== Risk preset ==="
input ENUM_RISK_MODE InpMode        = MODE_SAFE;   // SAFE 0.5% / FAST 1.0% of equity risked per trade at the 80-point stop

input group "=== Sizing (used when mode = CUSTOM) ==="
input double InpRiskPerTradePct     = 0.50;   // loss at the stop, % of equity (the video uses 1 NQ contract = ~3% on a 50k account)
input double InpFixedLots           = 0.0;    // >0 overrides the risk-based size
input double InpMaxLots             = 5.0;
input int    InpMaxSpreadPoints     = 0;      // 0 = no spread filter

input group "=== Prop-firm guards ==="
input double InpInitialBalance      = 0;      // 0 = balance when the EA starts (LIVE: set the real starting balance)
input double InpSoftDailyLossPct    = 2.5;    // firm limit 4%
input double InpSoftMaxLossPct      = 6.5;    // firm limit 10%
input double InpTargetPct           = 8.0;    // 0 = off; flatten and stop on reaching it (8 phase 1, 6 phase 2)
input double InpStopDayProfitPct    = 0.0;
input int    InpDayResetHour        = 0;

input group "=== News (live only) ==="
input bool   InpUseNewsFilter       = true;
input int    InpNewsMinutes         = 2;
input string InpNewsCurrency        = "USD";

input group "=== Execution ==="
input int    InpDeviationPoints     = 30;
input long   InpMagic               = 880033;
input string InpComment             = "DVP";

CTrade   trade;
datetime g_lastM5 = 0;
bool     g_haltDay = false, g_haltAll = false;
int      g_dayKey = -1, g_dir = 0;
bool     g_armed = false;
double   g_dayRef = 0, g_initBal = 0, g_risk, g_softDaily, g_softMax;
double   g_lastVwap = 0, g_lastMove = 0;

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
   if(InpMode == MODE_FAST) { g_risk = 1.00; g_softDaily = 3.2; g_softMax = 7.5; }
   Print("DVP started on ", _Symbol, ", mode ", EnumToString(InpMode), ", risk/trade ", g_risk, "%, stop ", InpStopPoints,
         " pts, initial balance ", DoubleToString(g_initBal, 2), ", open on server clock ", InpOpenHour, ":", InpOpenMin);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) { Comment(""); }

void OnTick()
{
   Guards();
   datetime t5 = iTime(_Symbol, PERIOD_M5, 0);
   if(t5 == 0 || t5 == g_lastM5) return;
   g_lastM5 = t5;
   OnNewM5(t5);
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
//| runs on every new 5-minute bar (bar 1 = the candle that just closed)
//+------------------------------------------------------------------+
void OnNewM5(datetime t5)
{
   int tod = (int)(t5 % 86400);
   datetime day = t5 - (datetime)tod;
   int openSec = InpOpenHour * 3600 + InpOpenMin * 60;
   int lastEntrySec = InpLastEntryHour * 3600 + InpLastEntryMin * 60;
   int flatSec = InpFlatHour * 3600 + InpFlatMin * 60;

   if(tod < openSec) { g_dir = 0; g_armed = false; return; }        // before the cash open (and resets the state each day)
   if(tod >= flatSec) { if(HasPos()) CloseAll("end of day"); g_dir = 0; g_armed = false; return; }

   if(InpUseNewsFilter && HasPos() && NewsBlocked(t5)) CloseAll("news window");

   // 15-minute evaluation, exactly when a 15-minute bar has just closed
   if(tod % 900 == 0 && tod - openSec >= InpNoTradeMinAfterOpen * 60) EvaluateTrend(day + (datetime)openSec);

   if(g_haltDay || g_haltAll || !g_armed || g_dir == 0) { ShowState(); return; }
   if(tod > lastEntrySec) return;
   if(HasPos()) return;

   // pullback trigger on the 5-minute candle that just closed
   double o = iOpen(_Symbol, PERIOD_M5, 1), c = iClose(_Symbol, PERIOD_M5, 1);
   bool red = (c < o), green = (c > o);
   if(g_dir > 0 && !red) return;
   if(g_dir < 0 && !green) return;

   int trades, losses, consec;
   DayStats(day, trades, losses, consec);
   if(trades >= InpMaxTradesPerDay) return;
   if((InpLossesConsecutive ? consec : losses) >= InpMaxLossesPerDay) { Print("DVP: daily loss rule reached, no more trades today"); g_haltDay = true; return; }
   if(InpUseNewsFilter && NewsBlocked(t5)) return;
   if(InpMaxSpreadPoints > 0 && SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) > InpMaxSpreadPoints) return;

   if(g_dir > 0 && InpAllowLong)        { if(Enter(true))  g_armed = false; }
   else if(g_dir < 0 && InpAllowShort)  { if(Enter(false)) g_armed = false; }
}

//+------------------------------------------------------------------+
//| trend state from the last completed 15-minute bar                |
//+------------------------------------------------------------------+
void EvaluateTrend(datetime openTime)
{
   int shOpen = iBarShift(_Symbol, PERIOD_M15, openTime, true);
   if(shOpen < 2) { g_dir = 0; g_armed = false; return; }

   double vNow = Vwap15(shOpen, 1);                       // anchored at the open, through the bar that just closed
   double vPrev = Vwap15(shOpen, 2);                      // one 15-minute bar earlier
   double cNow = iClose(_Symbol, PERIOD_M15, 1);
   double cHour = iClose(_Symbol, PERIOD_M15, 5);         // 4 bars (1 hour) earlier
   if(vNow <= 0 || vPrev <= 0 || cNow <= 0 || cHour <= 0) { g_dir = 0; g_armed = false; return; }

   double move = (cNow / cHour - 1.0) * 100.0;
   g_lastVwap = vNow; g_lastMove = move;

   int dir = 0;
   if(cNow > vNow && vNow > vPrev && move >= InpMinMovePct)  dir = 1;
   if(cNow < vNow && vNow < vPrev && move <= -InpMinMovePct) dir = -1;

   if(dir == 0) { g_dir = 0; g_armed = false; return; }
   if(InpRearmEveryEval || dir != g_dir) g_armed = true;
   g_dir = dir;
}

// volume-weighted average of the typical price of the 15-minute bars from shift 'from' (the open) down to 'to'
double Vwap15(int from, int to)
{
   double pv = 0, v = 0;
   for(int i = from; i >= to; i--)
   {
      double tp = (iHigh(_Symbol, PERIOD_M15, i) + iLow(_Symbol, PERIOD_M15, i) + iClose(_Symbol, PERIOD_M15, i)) / 3.0;
      double vol = (double)iTickVolume(_Symbol, PERIOD_M15, i);
      if(vol <= 0) vol = 1;
      pv += tp * vol;
      v += vol;
   }
   return (v > 0) ? pv / v : 0;
}

//+------------------------------------------------------------------+
bool Enter(bool isBuy)
{
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double px = isBuy ? ask : bid;
   if(px <= 0) return false;

   double tp = isBuy ? InpTpLongPoints : InpTpShortPoints;
   double minLvl = (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point;
   if(InpStopPoints < minLvl || tp < minLvl) { Print("DVP: stop/target closer than the broker minimum distance"); return false; }
   double sl = NormalizeDouble(isBuy ? px - InpStopPoints : px + InpStopPoints, _Digits);
   double tpPx = NormalizeDouble(isBuy ? px + tp : px - tp, _Digits);

   double lots = InpFixedLots;
   if(lots <= 0)
   {
      double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
      double ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
      if(tv <= 0 || ts <= 0) return false;
      double pv = tv / ts;                                       // account currency per 1.0 price unit per lot
      lots = AccountInfoDouble(ACCOUNT_EQUITY) * g_risk / 100.0 / (InpStopPoints * pv);
   }
   lots = NormVol(lots);
   if(lots <= 0) { Print("DVP: skip, size below the minimum lot"); return false; }

   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   while(lots > 0)
   {
      double margin = 0;
      if(OrderCalcMargin(isBuy ? ORDER_TYPE_BUY : ORDER_TYPE_SELL, _Symbol, lots, px, margin) &&
         margin < AccountInfoDouble(ACCOUNT_MARGIN_FREE) * 0.8) break;
      lots = NormVol(lots - step);
   }
   if(lots <= 0) { Print("DVP: skip, not enough free margin"); return false; }

   bool ok = isBuy ? trade.Buy(lots, _Symbol, 0.0, sl, tpPx, InpComment) : trade.Sell(lots, _Symbol, 0.0, sl, tpPx, InpComment);
   Print("DVP ", (isBuy ? "BUY " : "SELL "), DoubleToString(lots, 2), " @", DoubleToString(px, _Digits), " SL ", DoubleToString(sl, _Digits),
         " TP ", DoubleToString(tpPx, _Digits), " VWAP15 ", DoubleToString(g_lastVwap, _Digits), " 1h move ", DoubleToString(g_lastMove, 3), "% -> ",
         (ok ? "ok" : "FAILED "), (ok ? "" : IntegerToString(trade.ResultRetcode())));
   return ok;
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
//| trades opened, losses and trailing consecutive losses today      |
//+------------------------------------------------------------------+
void DayStats(datetime dayStart, int &trades, int &losses, int &consec)
{
   trades = 0; losses = 0; consec = 0;
   if(!HistorySelect(dayStart, TimeCurrent() + 60)) return;
   int n = HistoryDealsTotal(), run = 0;
   for(int i = 0; i < n; i++)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(tk == 0) continue;
      if(HistoryDealGetInteger(tk, DEAL_MAGIC) != InpMagic) continue;
      if(HistoryDealGetString(tk, DEAL_SYMBOL) != _Symbol) continue;
      long en = HistoryDealGetInteger(tk, DEAL_ENTRY);
      if(en == DEAL_ENTRY_IN) trades++;
      else if(en == DEAL_ENTRY_OUT || en == DEAL_ENTRY_OUT_BY)
      {
         double p = HistoryDealGetDouble(tk, DEAL_PROFIT) + HistoryDealGetDouble(tk, DEAL_COMMISSION) + HistoryDealGetDouble(tk, DEAL_SWAP);
         if(p < 0) { losses++; run++; } else run = 0;
      }
   }
   consec = run;
}

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
      if(trade.PositionClose(t)) Print("DVP close (", why, ")");
      else Print("DVP close FAILED (", why, ") retcode ", trade.ResultRetcode());
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
   Comment("DVP  trend=", (g_dir > 0 ? "LONG" : (g_dir < 0 ? "SHORT" : "none")), "  armed=", g_armed,
           "  haltDay=", g_haltDay, "  haltAll=", g_haltAll,
           "\nVWAP15 ", DoubleToString(g_lastVwap, _Digits), "   1h move ", DoubleToString(g_lastMove, 3), "%",
           "\nequity ", DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY), 2), "   dayRefEquity ", DoubleToString(g_dayRef, 2));
}
//+------------------------------------------------------------------+
