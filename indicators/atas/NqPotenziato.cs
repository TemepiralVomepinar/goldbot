// NQ Flow Zones — origin-of-impulse zones with history, grades and a measured hit-rate panel.
// Statistical reference map only: NO entry/exit logic. Spec: docs/NQ_POTENZIATO_SPEC.md
// NOT compiled against the ATAS SDK. Lines marked "VERIFY" depend on the exact SDK version.
namespace GoldBot.Atas
{
	using System;
	using System.Collections.Generic;
	using System.ComponentModel;
	using System.ComponentModel.DataAnnotations;
	using System.Drawing;
	using System.Linq;

	using ATAS.Indicators;
	using OFT.Rendering.Context;
	using OFT.Rendering.Tools;

	[DisplayName("NQ Potenziato")]
	public class NqPotenziato : Indicator
	{
		private sealed class Fz
		{
			public int Id, OriginBar, ImpulseBar, Dir, Grade, Touches, MitBar = -1;   // Dir: +1 buy zone, -1 sell zone
			public decimal Lo, Hi;
			public double Z, Disp, Score;
			public bool Armed = true, Mitigated;
			public DateTime Day;
		}

		private sealed class Pend { public Fz Z; public int Start, TouchIdx; public decimal Atr0; }
		private sealed class Tally { public int Bounce, Break, Neutral; }

		// ---- parameters ----
		[Display(Name = "Chart time UTC offset (h)", GroupName = "Session")] public int ChartTimeOffsetHours { get; set; } = 2; // VERIFY candle.Time timezone
		[Display(Name = "Only NY session (09:30-16:00 ET)", GroupName = "Session")] public bool OnlyNySession { get; set; } = true;
		[Display(Name = "Flow half-life (bars)", GroupName = "Edge")] public int HalfLife { get; set; } = 4;
		[Display(Name = "Z lookback (bars)", GroupName = "Edge")] public int ZLookback { get; set; } = 60;
		[Display(Name = "Min z (grade C)", GroupName = "Edge")] public double ZBurst { get; set; } = 1.2;
		[Display(Name = "Min displacement (xATR)", GroupName = "Edge")] public decimal MinDispAtr { get; set; } = 0.6m;
		[Display(Name = "Origin bars", GroupName = "Edge")] public int OriginBars { get; set; } = 2;
		[Display(Name = "Cooldown (bars)", GroupName = "Edge")] public int Cooldown { get; set; } = 6;
		[Display(Name = "Min grade shown (1=C,2=B,3=A)", GroupName = "Edge")] public int MinGrade { get; set; } = 1;
		[Display(Name = "Zone min height (ticks)", GroupName = "Zone")] public int MinTicks { get; set; } = 16;
		[Display(Name = "Zone max height (ticks)", GroupName = "Zone")] public int MaxTicks { get; set; } = 48;
		[Display(Name = "Zone width (bars)", GroupName = "Display")] public int WidthBars { get; set; } = 30;
		[Display(Name = "Extend until mitigated", GroupName = "Display")] public bool ExtendUntilMitigated { get; set; }
		[Display(Name = "History (sessions shown)", GroupName = "Display")] public int HistoryDays { get; set; } = 5;
		[Display(Name = "Max bars drawn (performance)", GroupName = "Display")] public int MaxDrawBars { get; set; } = 4000;
		[Display(Name = "Max zones kept", GroupName = "Display")] public int MaxZones { get; set; } = 400;
		[Display(Name = "Show moving average", GroupName = "Display")] public bool ShowMa { get; set; } = true;
		[Display(Name = "MA period", GroupName = "Display")] public int MaPeriod { get; set; } = 20;
		[Display(Name = "Show stats panel", GroupName = "Display")] public bool ShowPanel { get; set; } = true;
		[Display(Name = "Show labels", GroupName = "Display")] public bool ShowLabels { get; set; } = true;
		[Display(Name = "Label min grade (2=B,3=A)", GroupName = "Display")] public int LabelMinGrade { get; set; } = 2;
		[Display(Name = "Outcome horizon (bars)", GroupName = "Outcome")] public int HorizonBars { get; set; } = 10;
		[Display(Name = "Outcome ATR k", GroupName = "Outcome")] public decimal OutcomeAtrK { get; set; } = 0.5m;

		// ---- state ----
		private readonly List<Fz> _zones = new();
		private readonly List<Pend> _pending = new();
		private readonly Dictionary<(int grade, int touch), Tally> _stats = new();
		private readonly Dictionary<int, decimal> _ma = new();
		private readonly List<double> _fvals = new();
		private double _flow;
		private decimal _atr;
		private int _lastProcessed = -1, _lastBar, _sessionFirstBar, _nextId = 1;
		private DateTime _sessionDate = DateTime.MinValue;
		private TimeZoneInfo _ny;
		private readonly Dictionary<DrawingLayouts, int> _layoutCalls = new();
		private string _lastTimes = "-";
		private int _inSessionBars;

		public NqPotenziato() : base(true)
		{
			DenyToChangePanel = true;
			Panel = IndicatorDataProvider.CandlesPanel;                                  // VERIFY: draw on the price panel
			EnableCustomDrawing = true;                                                  // without this OnRender is never called
			SubscribeToDrawingEvents(DrawingLayouts.Final);
		}

		protected override void OnCalculate(int bar, decimal value)
		{
			if (bar == 0) ResetAll();
			_lastBar = bar;
			if (bar < 1 || bar - 1 <= _lastProcessed) return;
			var b = bar - 1; _lastProcessed = b;

			var c = GetCandle(b);
			UpdateMa(b, c.Close);

			DateTime day;
			if (OnlyNySession) { if (!TryNySession(c.Time, out day)) return; } else day = c.Time.Date;
			_inSessionBars++;
			if (day != _sessionDate) NewSession(day, b);

			double delta = 0;
			foreach (var lvl in c.GetAllPriceLevels()) delta += (double)(lvl.Ask - lvl.Bid);   // VERIFY: PriceVolumeInfo.Ask/Bid

			var atrPrev = _atr;
			var tr = Math.Max(c.High - c.Low, Math.Max(Math.Abs(c.High - c.Close), Math.Abs(c.Low - c.Close)));
			_atr = _atr == 0 ? tr : _atr + (2m / 15m) * (tr - _atr);

			var lambda = Math.Pow(0.5, 1.0 / Math.Max(HalfLife, 1));
			_flow = _flow * lambda + delta;

			UpdateZones(b, c);
			ResolvePending(b, c);
			Detect(b, c, delta, atrPrev);

			_fvals.Add(_flow);
			if (_fvals.Count > ZLookback) _fvals.RemoveAt(0);
		}

		// ---------- edge: persistent one-sided flow + displacement -> zone at the origin of the move ----------
		private void Detect(int b, IndicatorCandle c, double delta, decimal atrPrev)
		{
			if (_fvals.Count < 20 || atrPrev <= 0) return;
			var med = Median(_fvals.ToArray());
			var mad = 1.4826 * Median(_fvals.Select(x => Math.Abs(x - med)).ToArray());
			if (mad <= 1e-9) return;

			var z = (_flow - med) / mad;
			var dir = Math.Sign(z);
			if (dir == 0 || Math.Abs(z) < ZBurst || Math.Sign(delta) != dir) return;

			int bestN = 0; decimal bestD = 0;                                           // best displacement over the last 1..3 bars
			for (var n = 1; n <= 3; n++)
			{
				var s = b - n + 1;
				if (s < _sessionFirstBar) break;
				var d = dir * (c.Close - GetCandle(s).Open);
				if (d > bestD) { bestD = d; bestN = n; }
			}
			if (bestN == 0 || bestD < MinDispAtr * atrPrev) return;

			var s0 = b - bestN + 1;
			var oStart = s0 - OriginBars;
			if (oStart < _sessionFirstBar) return;
			if (_zones.Any(x => x.Dir == dir && x.Day == _sessionDate && b - x.ImpulseBar <= Cooldown)) return;

			decimal lo = decimal.MaxValue, hi = decimal.MinValue;
			for (var i = oStart; i < s0; i++) { var k = GetCandle(i); lo = Math.Min(lo, k.Low); hi = Math.Max(hi, k.High); }

			var tick = InstrumentInfo.TickSize;
			var h = Math.Min(Math.Max(hi - lo, MinTicks * tick), MaxTicks * tick);
			var zLo = dir > 0 ? lo : hi - h;
			var zHi = dir > 0 ? lo + h : hi;

			if (_zones.Any(x => x.Dir == dir && x.Day == _sessionDate && !x.Mitigated &&
				Math.Min(x.Hi, zHi) - Math.Max(x.Lo, zLo) > 0.5m * h)) return;       // no stacked duplicates

			// strength score 0-100: flow persistence (60%) + displacement vs ATR (40%). Weights are design assumptions, validated only by the panel.
			var disp = (double)(bestD / atrPrev);
			var score = 100 * (0.6 * Math.Min(Math.Abs(z), 6) / 6 + 0.4 * Math.Min(disp, 3) / 3);
			var grade = score >= 60 ? 3 : score >= 35 ? 2 : 1;
			if (grade < MinGrade) return;

			_zones.Add(new Fz { Id = _nextId++, OriginBar = oStart, ImpulseBar = b, Dir = dir, Grade = grade, Z = Math.Abs(z), Disp = disp, Score = score, Lo = zLo, Hi = zHi, Day = _sessionDate });
			if (_zones.Count > MaxZones) _zones.RemoveAt(0);
		}

		// ---------- touches and mitigation ----------
		private void UpdateZones(int b, IndicatorCandle c)
		{
			foreach (var z in _zones.Where(z => !z.Mitigated && z.ImpulseBar < b))
			{
				var inside = c.Low <= z.Hi && c.High >= z.Lo;
				if (!inside)
				{
					if (!z.Armed && (c.Low > z.Hi + 0.5m * _atr || c.High < z.Lo - 0.5m * _atr)) z.Armed = true;
				}
				else if (z.Armed)
				{
					z.Armed = false; z.Touches++;
					_pending.Add(new Pend { Z = z, Start = b, TouchIdx = z.Touches, Atr0 = _atr });
				}

				var through = z.Dir > 0 ? c.Close < z.Lo - 0.1m * _atr : c.Close > z.Hi + 0.1m * _atr;
				if (through) { z.Mitigated = true; z.MitBar = b; }
			}
		}

		// ---------- outcome labelling: bounce (away from zone) vs break (through it). Statistics only. ----------
		private void ResolvePending(int b, IndicatorCandle c)
		{
			for (var i = _pending.Count - 1; i >= 0; i--)
			{
				var p = _pending[i]; var k = OutcomeAtrK * p.Atr0; int? res = null;
				var bounce = p.Z.Dir > 0 ? c.Close > p.Z.Hi + k : c.Close < p.Z.Lo - k;
				var brk = p.Z.Dir > 0 ? c.Close < p.Z.Lo - k : c.Close > p.Z.Hi + k;
				if (bounce) res = 1; else if (brk) res = -1;
				if (res == null && b - p.Start < HorizonBars) continue;

				var key = (p.Z.Grade, Math.Min(p.TouchIdx, 3));
				if (!_stats.TryGetValue(key, out var t)) _stats[key] = t = new Tally();
				if (res == 1) t.Bounce++; else if (res == -1) t.Break++; else t.Neutral++;
				_pending.RemoveAt(i);
			}
		}

		// ---------- rendering ----------
		protected override void OnRender(RenderContext context, DrawingLayouts layout)   // VERIFY signature
		{
			if (ChartInfo is null || InstrumentInfo is null) return;
			_layoutCalls[layout] = _layoutCalls.TryGetValue(layout, out var n0) ? n0 + 1 : 1;
			var statusFont = new RenderFont("Arial", 9);
			context.DrawString($"NQ Potenziato | bars={_lastBar} processed={_lastProcessed} inSession={_inSessionBars} zones={_zones.Count} | {_lastTimes} | layouts: {string.Join(",", _layoutCalls.Select(k => k.Key + "=" + k.Value))}",
				statusFont, Color.Gold, 70, 20);                                         // always-on diagnostic line
			if (layout != _layoutCalls.Keys.Max()) return;                               // draw once per frame, on the highest layout seen (Final)
			var last = _lastBar;                                                         // no visible-range API: draw recent bars, skip off-screen by X
			var first = Math.Max(last - MaxDrawBars, 0);
			var font = new RenderFont("Arial", 9);

			var shown = _zones.Select(z => z.Day).Distinct().OrderByDescending(d => d).Take(Math.Max(HistoryDays, 1)).ToHashSet();
			foreach (var z in _zones)
			{
				if (!shown.Contains(z.Day)) continue;
				var end = ExtendUntilMitigated ? (z.MitBar >= 0 ? z.MitBar : _lastBar) : Math.Min(z.OriginBar + WidthBars, _lastBar);
				if (end < first || z.OriginBar > last) continue;

				var x1 = ChartInfo.GetXByBar(z.OriginBar);
				var x2 = ChartInfo.GetXByBar(end);
				if (x2 < -50 || x1 > 20000) continue;                                    // off-screen
				var yTop = ChartInfo.GetYByPrice(z.Hi);                                  // VERIFY
				var yBot = ChartInfo.GetYByPrice(z.Lo);
				var baseCol = z.Dir > 0 ? Color.FromArgb(40, 170, 80) : Color.FromArgb(110, 50, 190);   // green buy / purple sell
				var alpha = (z.Grade == 3 ? 140 : z.Grade == 2 ? 85 : 35) - 12 * Math.Min(z.Touches, 3);   // A strong, C faint, fades with each touch
				if (z.Mitigated) alpha = 20;
				var rect = new Rectangle(x1, yTop, Math.Max(x2 - x1, 3), Math.Max(yBot - yTop, 2));
				context.FillRectangle(Color.FromArgb(Math.Max(alpha, 15), baseCol), rect);
				context.DrawRectangle(new RenderPen(Color.FromArgb(Math.Min(Math.Max(alpha + 60, 50), 255), baseCol), z.Grade == 3 ? 3 : z.Grade == 2 ? 2 : 1), rect);   // VERIFY
				if (ShowLabels && z.Grade >= LabelMinGrade && !z.Mitigated)
					context.DrawString($"{"CBA"[z.Grade - 1]} {z.Score:F0}  T{z.Touches}", font, Color.White, x1 + 3, yTop + 2);
			}

			if (ShowMa)
			{
				for (var i = Math.Max(first, 1); i <= last; i++)
				{
					if (!_ma.TryGetValue(i, out var v1) || !_ma.TryGetValue(i - 1, out var v0)) continue;
					var xa = ChartInfo.GetXByBar(i - 1); var xb = ChartInfo.GetXByBar(i);
					if (xb < -50 || xa > 20000) continue;
					var col = v1 >= v0 ? Color.FromArgb(120, 230, 60) : Color.FromArgb(150, 90, 210);
					context.DrawLine(new RenderPen(col, 2), xa, ChartInfo.GetYByPrice(v0), xb, ChartInfo.GetYByPrice(v1));   // VERIFY
				}
			}

			if (ShowPanel)
			{
				var y = 40;
				context.DrawString("First-touch bounce rate (prior 0.50)", font, Color.Gainsboro, 70, y); y += 14;
				foreach (var g in new[] { 3, 2, 1 })
				{
					_stats.TryGetValue((g, 1), out var t);
					int s = t?.Bounce ?? 0, f = t?.Break ?? 0;
					double p = (5.0 + s) / (10.0 + s + f);
					context.DrawString($"Grade {"CBA"[g - 1]}: {p:P0}  (n={s + f}, neutral={t?.Neutral ?? 0})", font, Color.Gainsboro, 70, y); y += 14;
				}
			}
		}

		// ---------- helpers ----------
		private void UpdateMa(int b, decimal close)
		{
			var k = 2m / (MaPeriod + 1);
			_ma[b] = _ma.TryGetValue(b - 1, out var prev) ? prev + k * (close - prev) : close;
		}

		private void NewSession(DateTime day, int bar)
		{
			_sessionDate = day; _sessionFirstBar = bar; _flow = 0; _atr = 0;
			_fvals.Clear(); _pending.Clear();
		}

		private void ResetAll()
		{
			_zones.Clear(); _pending.Clear(); _stats.Clear(); _ma.Clear(); _fvals.Clear();
			_flow = 0; _atr = 0; _lastProcessed = -1; _sessionDate = DateTime.MinValue; _nextId = 1;
		}

		private bool TryNySession(DateTime t, out DateTime day)
		{
			_ny ??= FindNy();
			var ny = TimeZoneInfo.ConvertTimeFromUtc(DateTime.SpecifyKind(t.AddHours(-ChartTimeOffsetHours), DateTimeKind.Utc), _ny);
			_lastTimes = $"candle={t:HH:mm} -> NY={ny:HH:mm}";
			day = ny.Date;
			var tod = ny.TimeOfDay;
			return tod >= new TimeSpan(9, 30, 0) && tod < new TimeSpan(16, 0, 0);
		}

		private static TimeZoneInfo FindNy()
		{
			try { return TimeZoneInfo.FindSystemTimeZoneById("America/New_York"); }
			catch (TimeZoneNotFoundException) { return TimeZoneInfo.FindSystemTimeZoneById("Eastern Standard Time"); }
		}

		private static double Median(double[] a)
		{
			if (a.Length == 0) return 0;
			var s = (double[])a.Clone(); Array.Sort(s);
			return s.Length % 2 == 1 ? s[s.Length / 2] : 0.5 * (s[s.Length / 2 - 1] + s[s.Length / 2]);
		}
	}
}
