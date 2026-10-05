// NQ Profilo — prior-day Volume Profile + TPO (Market Profile) confluence zones, with history, grades and a hit-rate panel.
// Statistical reference map only: NO entry/exit logic. Spec: docs/NQ_PROFILO_SPEC.md
// NOT compiled against the ATAS SDK by the author. Drawing calls reuse the ones already confirmed to compile in NqPotenziato.
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

	[DisplayName("NQ Profilo (TPO + Volume Profile)")]
	public class NqProfilo : Indicator
	{
		private sealed class Feat { public string Code; public int Family; public double W; public decimal Price; }   // family: 1 = volume profile, 2 = TPO, 3 = extremes

		private sealed class Pz
		{
			public int Id, Grade, Families, StartBar, EndBar, Touches;
			public decimal Lo, Hi;
			public double Score;
			public string Codes;
			public bool Armed = true, Resistance;
			public DateTime Day;
		}

		private sealed class Pend { public Pz Z; public int Start, TouchIdx, Approach; public decimal Atr0; }   // Approach: +1 from below, -1 from above
		private sealed class Tally { public int Bounce, Break, Neutral; }

		// ---- parameters ----
		[Display(Name = "Chart time UTC offset (h)", GroupName = "Session")] public int ChartTimeOffsetHours { get; set; } = 2;
		[Display(Name = "Only NY session (09:30-16:00 ET)", GroupName = "Session")] public bool OnlyNySession { get; set; } = true;
		[Display(Name = "Arm zones after (min from open)", GroupName = "Session")] public int ArmAfterMinutes { get; set; } = 30;
		[Display(Name = "Price bracket (ticks)", GroupName = "Profile")] public int BracketTicks { get; set; } = 8;
		[Display(Name = "TPO period (min)", GroupName = "Profile")] public int TpoMinutes { get; set; } = 30;
		[Display(Name = "HVN min z", GroupName = "Profile")] public double HvnZ { get; set; } = 1.0;
		[Display(Name = "Cluster tolerance (ticks)", GroupName = "Confluence")] public int ClusterTicks { get; set; } = 8;
		[Display(Name = "Zone min height (ticks)", GroupName = "Confluence")] public int MinTicks { get; set; } = 12;
		[Display(Name = "Min grade shown (1=C,2=B,3=A)", GroupName = "Confluence")] public int MinGrade { get; set; } = 2;
		[Display(Name = "History (sessions shown)", GroupName = "Display")] public int HistoryDays { get; set; } = 5;
		[Display(Name = "Max bars drawn (performance)", GroupName = "Display")] public int MaxDrawBars { get; set; } = 4000;
		[Display(Name = "Max zones kept", GroupName = "Display")] public int MaxZones { get; set; } = 600;
		[Display(Name = "Show moving average", GroupName = "Display")] public bool ShowMa { get; set; } = true;
		[Display(Name = "MA period", GroupName = "Display")] public int MaPeriod { get; set; } = 20;
		[Display(Name = "Show stats panel", GroupName = "Display")] public bool ShowPanel { get; set; } = true;
		[Display(Name = "Show labels", GroupName = "Display")] public bool ShowLabels { get; set; } = true;
		[Display(Name = "Label min grade (2=B,3=A)", GroupName = "Display")] public int LabelMinGrade { get; set; } = 2;
		[Display(Name = "Outcome horizon (bars)", GroupName = "Outcome")] public int HorizonBars { get; set; } = 10;
		[Display(Name = "Outcome ATR k", GroupName = "Outcome")] public decimal OutcomeAtrK { get; set; } = 0.5m;

		// ---- state ----
		private readonly List<Pz> _zones = new();
		private readonly List<Pend> _pending = new();
		private readonly Dictionary<(int grade, int touch), Tally> _stats = new();
		private readonly Dictionary<int, decimal> _ma = new();
		private readonly Dictionary<int, double> _vol = new();                       // bracket index -> volume
		private readonly Dictionary<int, HashSet<int>> _tpo = new();                 // period -> bracket indexes touched
		private readonly Dictionary<DateTime, int> _dayLastBar = new();
		private readonly Dictionary<DateTime, int> _dayFirstBar = new();
		private readonly Dictionary<DateTime, int> _dayOrder = new();
		private decimal _dayHigh, _dayLow, _ibHigh, _ibLow, _atr, _prevClose;
		private bool _dayInit, _ibInit;
		private int _lastProcessed = -1, _lastBar, _nextId = 1;
		private DateTime _sessionDate = DateTime.MinValue;
		private TimeSpan _periodOrigin = new TimeSpan(9, 30, 0);
		private TimeZoneInfo _ny;
		private readonly Dictionary<DrawingLayouts, int> _layoutCalls = new();
		private string _lastTimes = "-";
		private int _inSessionBars, _sessions;

		public NqProfilo() : base(true)
		{
			DenyToChangePanel = true;
			Panel = IndicatorDataProvider.CandlesPanel;
			EnableCustomDrawing = true;
			SubscribeToDrawingEvents(DrawingLayouts.Final);
		}

		private decimal BSize => Math.Max(BracketTicks, 1) * InstrumentInfo.TickSize;
		private int Idx(decimal price) => (int)Math.Floor(price / BSize);
		private decimal PLo(int idx) => idx * BSize;
		private decimal PHi(int idx) => (idx + 1) * BSize;
		private decimal PMid(int idx) => (idx + 0.5m) * BSize;

		protected override void OnCalculate(int bar, decimal value)
		{
			if (bar == 0) ResetAll();
			_lastBar = bar;
			if (bar < 1 || bar - 1 <= _lastProcessed) return;
			var b = bar - 1; _lastProcessed = b;

			var c = GetCandle(b);
			UpdateMa(b, c.Close);

			DateTime day; TimeSpan tod;
			if (OnlyNySession) { if (!TryNySession(c.Time, out day, out tod)) return; }
			else { day = c.Time.Date; tod = c.Time.TimeOfDay; }
			_inSessionBars++;
			if (day != _sessionDate) NewSession(day, tod, b);
			_dayLastBar[day] = b;

			AccumulateProfile(c, tod);

			var atrPrev = _atr;
			var tr = Math.Max(c.High - c.Low, Math.Max(Math.Abs(c.High - c.Close), Math.Abs(c.Low - c.Close)));
			_atr = _atr == 0 ? tr : _atr + (2m / 15m) * (tr - _atr);

			var armed = tod - _periodOrigin >= TimeSpan.FromMinutes(ArmAfterMinutes);
			UpdateZones(b, c, armed);
			ResolvePending(b, c);
			_prevClose = c.Close;
		}

		// ---------- session rollover: the profile of the session that just ended becomes today's zones ----------
		private void NewSession(DateTime day, TimeSpan tod, int b)
		{
			List<Feat> feats = null;
			if (_vol.Count > 0 && _sessionDate != DateTime.MinValue)
			{
				try { feats = BuildFeatures(); } catch (Exception) { feats = null; }
			}

			_sessionDate = day;
			_sessions++;
			_dayOrder[day] = _sessions;
			_dayFirstBar[day] = b;
			_periodOrigin = OnlyNySession ? new TimeSpan(9, 30, 0) : tod;
			_vol.Clear(); _tpo.Clear(); _pending.Clear();
			_dayInit = false; _ibInit = false;

			if (feats != null && feats.Count > 0) CreateZones(feats, day, b);
		}

		private void AccumulateProfile(IndicatorCandle c, TimeSpan tod)
		{
			foreach (var lvl in c.GetAllPriceLevels())
			{
				var i = Idx(lvl.Price);
				_vol[i] = (_vol.TryGetValue(i, out var v) ? v : 0) + (double)(lvl.Ask + lvl.Bid);
			}

			var p = Math.Max((int)((tod - _periodOrigin).TotalMinutes / Math.Max(TpoMinutes, 1)), 0);
			if (!_tpo.TryGetValue(p, out var set)) _tpo[p] = set = new HashSet<int>();
			for (var i = Idx(c.Low); i <= Idx(c.High); i++) set.Add(i);

			if (!_dayInit) { _dayHigh = c.High; _dayLow = c.Low; _dayInit = true; }
			else { _dayHigh = Math.Max(_dayHigh, c.High); _dayLow = Math.Min(_dayLow, c.Low); }

			if (p < 2)   // initial balance = first 60 minutes
			{
				if (!_ibInit) { _ibHigh = c.High; _ibLow = c.Low; _ibInit = true; }
				else { _ibHigh = Math.Max(_ibHigh, c.High); _ibLow = Math.Min(_ibLow, c.Low); }
			}
		}

		// ---------- features of the finished session: volume profile + TPO + extremes ----------
		private List<Feat> BuildFeatures()
		{
			var feats = new List<Feat>();
			var lo = _vol.Keys.Min(); var hi = _vol.Keys.Max();
			var n = hi - lo + 1;
			if (n < 5 || n > 4000) return feats;

			var v = new double[n];
			foreach (var kv in _vol) v[kv.Key - lo] = kv.Value;
			var sm = new double[n];
			for (var i = 0; i < n; i++) sm[i] = (2 * v[i] + (i > 0 ? v[i - 1] : v[i]) + (i < n - 1 ? v[i + 1] : v[i])) / 4.0;

			var poc = 0;
			for (var i = 1; i < n; i++) if (sm[i] > sm[poc]) poc = i;
			Add(feats, "POC", 1, 3.0, PMid(lo + poc));
			ValueArea(v, poc, out var vl, out var vh);
			Add(feats, "VAH", 1, 2.5, PHi(lo + vh));
			Add(feats, "VAL", 1, 2.5, PLo(lo + vl));

			var nz = sm.Where(x => x > 0).ToArray();
			var med = Median(nz);
			var mad = 1.4826 * Median(nz.Select(x => Math.Abs(x - med)).ToArray());
			if (mad > 1e-9)
			{
				var hv = new List<(int i, double z)>();
				for (var i = 1; i < n - 1; i++)
				{
					if (sm[i] > sm[i - 1] && sm[i] >= sm[i + 1] && Math.Abs(i - poc) >= 3)
					{
						var z = (sm[i] - med) / mad;
						if (z >= HvnZ) hv.Add((i, z));
					}
				}
				foreach (var h in hv.OrderByDescending(x => x.z).Take(3)) Add(feats, "HVN", 1, 1.5, PMid(lo + h.i));
			}

			if (_tpo.Count > 0)
			{
				int tl = int.MaxValue, th = int.MinValue;
				foreach (var s in _tpo.Values) foreach (var i in s) { if (i < tl) tl = i; if (i > th) th = i; }
				var m = th - tl + 1;
				if (m >= 5 && m <= 4000)
				{
					var cnt = new double[m];
					foreach (var s in _tpo.Values) foreach (var i in s) cnt[i - tl] += 1;

					var mid = (m - 1) / 2;
					var tpoc = 0;
					for (var i = 1; i < m; i++)
						if (cnt[i] > cnt[tpoc] || (cnt[i] == cnt[tpoc] && Math.Abs(i - mid) < Math.Abs(tpoc - mid))) tpoc = i;
					Add(feats, "TPOC", 2, 2.5, PMid(tl + tpoc));
					ValueArea(cnt, tpoc, out var tvl, out var tvh);
					Add(feats, "TVAH", 2, 2.5, PHi(tl + tvh));
					Add(feats, "TVAL", 2, 2.5, PLo(tl + tvl));

					var runs = new List<(int s, int e)>();                          // single prints: runs of >= 3 brackets with a single TPO
					var rs = -1;
					for (var i = 0; i <= m; i++)
					{
						var single = i < m && cnt[i] == 1;
						if (single && rs < 0) rs = i;
						if (!single && rs >= 0) { if (i - rs >= 3) runs.Add((rs, i - 1)); rs = -1; }
					}
					foreach (var r in runs.OrderByDescending(x => x.e - x.s).Take(2))
					{
						Add(feats, "SPH", 2, 2.0, PHi(tl + r.e));
						Add(feats, "SPL", 2, 2.0, PLo(tl + r.s));
					}
				}
			}

			if (_dayInit) { Add(feats, "PDH", 3, 2.0, _dayHigh); Add(feats, "PDL", 3, 2.0, _dayLow); }
			if (_ibInit) { Add(feats, "IBH", 3, 1.5, _ibHigh); Add(feats, "IBL", 3, 1.5, _ibLow); }
			return feats;
		}

		private static void Add(List<Feat> l, string code, int family, double w, decimal price) => l.Add(new Feat { Code = code, Family = family, W = w, Price = price });

		private static void ValueArea(double[] w, int poc, out int l, out int h)       // standard 70% value area, expanding by two brackets
		{
			double total = w.Sum(), acc = w[poc];
			l = poc; h = poc;
			while (acc < 0.7 * total)
			{
				var up = h + 1 < w.Length ? w[h + 1] + (h + 2 < w.Length ? w[h + 2] : 0) : -1;
				var dn = l - 1 >= 0 ? w[l - 1] + (l - 2 >= 0 ? w[l - 2] : 0) : -1;
				if (up < 0 && dn < 0) break;
				if (up >= dn) { acc += up; h = Math.Min(h + 2, w.Length - 1); }
				else { acc += dn; l = Math.Max(l - 2, 0); }
			}
		}

		// ---------- confluence: features of different families that fall within a few ticks form one zone ----------
		private void CreateZones(List<Feat> feats, DateTime day, int b)
		{
			var tick = InstrumentInfo.TickSize;
			var tol = ClusterTicks * tick;
			var sorted = feats.OrderBy(f => f.Price).ToList();
			var clusters = new List<List<Feat>>();
			foreach (var f in sorted)
			{
				if (clusters.Count == 0 || f.Price - clusters[clusters.Count - 1][0].Price > tol) clusters.Add(new List<Feat>());
				clusters[clusters.Count - 1].Add(f);
			}

			foreach (var cl in clusters)
			{
				var d = cl.GroupBy(f => f.Code).Select(g => g.First()).ToList();
				var score = d.Sum(f => f.W);
				var fam = d.Select(f => f.Family).Distinct().Count();
				var grade = (fam >= 3 || score >= 8.0) ? 3 : (fam >= 2 && score >= 4.5) ? 2 : 1;
				if (grade < MinGrade) continue;

				var lo = d.Min(f => f.Price) - 2 * tick;
				var hi = d.Max(f => f.Price) + 2 * tick;
				var minH = MinTicks * tick;
				if (hi - lo < minH) { var mid = (hi + lo) / 2; lo = mid - minH / 2; hi = mid + minH / 2; }

				_zones.Add(new Pz
				{
					Id = _nextId++, Day = day, StartBar = b, EndBar = b, Lo = lo, Hi = hi, Score = score, Grade = grade, Families = fam,
					Codes = string.Join("+", d.OrderByDescending(f => f.W).Take(4).Select(f => f.Code))
				});
			}
			while (_zones.Count > MaxZones) _zones.RemoveAt(0);
		}

		// ---------- touches (only after the arming time, since value-area edges are unreliable in the first 30 minutes) ----------
		private void UpdateZones(int b, IndicatorCandle c, bool armedTime)
		{
			foreach (var z in _zones)
			{
				if (z.Day != _sessionDate) continue;
				z.EndBar = b;
				z.Resistance = (z.Lo + z.Hi) / 2 > c.Close;
				if (_atr <= 0) continue;

				var inside = c.Low <= z.Hi && c.High >= z.Lo;
				if (!inside)
				{
					if (!z.Armed && (c.Low > z.Hi + 0.5m * _atr || c.High < z.Lo - 0.5m * _atr)) z.Armed = true;
				}
				else if (z.Armed)
				{
					z.Armed = false;
					if (!armedTime) continue;                                            // early touches are not counted
					z.Touches++;
					var approach = _prevClose > z.Hi ? -1 : _prevClose < z.Lo ? 1 : (c.Open > (z.Lo + z.Hi) / 2 ? -1 : 1);
					_pending.Add(new Pend { Z = z, Start = b, TouchIdx = z.Touches, Approach = approach, Atr0 = _atr });
				}
			}
		}

		// ---------- outcome labelling: bounce (price leaves back the way it came) vs break (price goes through). Statistics only. ----------
		private void ResolvePending(int b, IndicatorCandle c)
		{
			for (var i = _pending.Count - 1; i >= 0; i--)
			{
				var p = _pending[i]; var k = OutcomeAtrK * p.Atr0; int? res = null;
				var bounce = p.Approach > 0 ? c.Close < p.Z.Lo - k : c.Close > p.Z.Hi + k;
				var brk = p.Approach > 0 ? c.Close > p.Z.Hi + k : c.Close < p.Z.Lo - k;
				if (bounce) res = 1; else if (brk) res = -1;
				if (res == null && b - p.Start < HorizonBars) continue;

				var key = (p.Z.Grade, Math.Min(p.TouchIdx, 3));
				if (!_stats.TryGetValue(key, out var t)) _stats[key] = t = new Tally();
				if (res == 1) t.Bounce++; else if (res == -1) t.Break++; else t.Neutral++;
				_pending.RemoveAt(i);
			}
		}

		// ---------- rendering ----------
		protected override void OnRender(RenderContext context, DrawingLayouts layout)
		{
			if (ChartInfo is null || InstrumentInfo is null) return;
			_layoutCalls[layout] = _layoutCalls.TryGetValue(layout, out var n0) ? n0 + 1 : 1;
			var font = new RenderFont("Arial", 9);
			context.DrawString($"NQ Profilo | bars={_lastBar} processed={_lastProcessed} inSession={_inSessionBars} sessions={_sessions} zones={_zones.Count} | {_lastTimes} | layouts: {string.Join(",", _layoutCalls.Select(k => k.Key + "=" + k.Value))}",
				font, Color.Gold, 70, 20);
			if (layout != _layoutCalls.Keys.Max()) return;

			var last = _lastBar;
			var first = Math.Max(last - MaxDrawBars, 0);

			var shown = _zones.Select(z => z.Day).Distinct().OrderByDescending(d => d).Take(Math.Max(HistoryDays, 1)).ToHashSet();
			foreach (var z in _zones)
			{
				if (!shown.Contains(z.Day)) continue;
				var end = z.Day == _sessionDate ? _lastBar : z.EndBar;
				if (end < first) continue;

				var x1 = ChartInfo.GetXByBar(z.StartBar);
				var x2 = ChartInfo.GetXByBar(end);
				if (x2 < -50 || x1 > 20000) continue;
				var yTop = ChartInfo.GetYByPrice(z.Hi);
				var yBot = ChartInfo.GetYByPrice(z.Lo);

				var baseCol = z.Resistance ? Color.FromArgb(110, 50, 190) : Color.FromArgb(40, 170, 80);   // purple = above price (resistance), green = below (support)
				var alpha = (z.Grade == 3 ? 120 : z.Grade == 2 ? 75 : 35) - 10 * Math.Min(z.Touches, 3);
				var rect = new Rectangle(x1, yTop, Math.Max(x2 - x1, 3), Math.Max(yBot - yTop, 2));
				context.FillRectangle(Color.FromArgb(Math.Max(alpha, 15), baseCol), rect);
				context.DrawRectangle(new RenderPen(Color.FromArgb(Math.Min(Math.Max(alpha + 60, 50), 255), baseCol), z.Grade == 3 ? 3 : z.Grade == 2 ? 2 : 1), rect);
				if (ShowLabels && z.Grade >= LabelMinGrade)
					context.DrawString($"{"CBA"[z.Grade - 1]} {z.Score:F1} {z.Codes} T{z.Touches}", font, Color.White, Math.Max(x1, 5) + 3, yTop + 2);
			}

			if (ShowMa)
			{
				for (var i = Math.Max(first, 1); i <= last; i++)
				{
					if (!_ma.TryGetValue(i, out var v1) || !_ma.TryGetValue(i - 1, out var v0)) continue;
					var xa = ChartInfo.GetXByBar(i - 1); var xb = ChartInfo.GetXByBar(i);
					if (xb < -50 || xa > 20000) continue;
					var col = v1 >= v0 ? Color.FromArgb(120, 230, 60) : Color.FromArgb(150, 90, 210);
					context.DrawLine(new RenderPen(col, 2), xa, ChartInfo.GetYByPrice(v0), xb, ChartInfo.GetYByPrice(v1));
				}
			}

			if (ShowPanel)
			{
				var y = 40;
				context.DrawString($"First-touch bounce rate (prior 0.50) - touches before {ArmAfterMinutes} min excluded", font, Color.Gainsboro, 70, y); y += 14;
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

		private void ResetAll()
		{
			_zones.Clear(); _pending.Clear(); _stats.Clear(); _ma.Clear(); _vol.Clear(); _tpo.Clear();
			_dayLastBar.Clear(); _dayFirstBar.Clear(); _dayOrder.Clear();
			_atr = 0; _prevClose = 0; _lastProcessed = -1; _sessionDate = DateTime.MinValue; _nextId = 1;
			_dayInit = false; _ibInit = false; _inSessionBars = 0; _sessions = 0;
		}

		private bool TryNySession(DateTime t, out DateTime day, out TimeSpan tod)
		{
			_ny ??= FindNy();
			var ny = TimeZoneInfo.ConvertTimeFromUtc(DateTime.SpecifyKind(t.AddHours(-ChartTimeOffsetHours), DateTimeKind.Utc), _ny);
			_lastTimes = $"candle={t:HH:mm} -> NY={ny:HH:mm}";
			day = ny.Date;
			tod = ny.TimeOfDay;
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
