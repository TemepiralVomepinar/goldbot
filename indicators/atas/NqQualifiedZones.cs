// NQ 1-minute Qualified Zones — statistical reference map (NO entry/exit logic).
// Spec: docs/NQ_QUALIFIED_ZONES_SPEC.md
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

	[DisplayName("NQ Qualified Zones (stat map)")]
	public class NqQualifiedZones : Indicator
	{
		private enum ZState { Qualified, Weakened, Expired }

		private sealed class Zone
		{
			public int Id, FormBar, Touches, Dir;                 // Dir: +1 buy-dominated, -1 sell-dominated
			public decimal Lo, Hi, MassV, Consumed, ZV0, ZI;      // MassV = volume in zone at formation
			public double Med0, Mad0, PBH, PeakSm;
			public bool Armed = true, Round;
			public ZState State = ZState.Qualified;
			public int LastBar;
			public DateTime Day;
		}

		private sealed class Pending { public Zone Z; public int StartBar, TouchIdx; public int ApproachDir; public decimal Atr0; }

		private sealed class Beta { public int S, F, N; }        // continuation / rejection / neutral

		// ---- parameters ----
		[Display(Name = "Chart time UTC offset (h)", GroupName = "Session")] public int ChartTimeOffsetHours { get; set; } // VERIFY candle.Time timezone
		[Display(Name = "Smooth K (ticks)", GroupName = "Mass")] public int SmoothK { get; set; } = 2;
		[Display(Name = "Min z (mass)", GroupName = "Mass")] public double ZMin { get; set; } = 2.0;
		[Display(Name = "FDR q", GroupName = "Mass")] public double FdrQ { get; set; } = 0.05;
		[Display(Name = "Min |z| imbalance", GroupName = "Imbalance")] public double ZIMin { get; set; } = 2.0;
		[Display(Name = "Min bars in session", GroupName = "Mass")] public int MinBars { get; set; } = 15;
		[Display(Name = "Kappa (expiry x mass)", GroupName = "Memory")] public double Kappa { get; set; } = 1.5;
		[Display(Name = "Max touches", GroupName = "Memory")] public int MaxTouches { get; set; } = 3;
		[Display(Name = "Alpha total", GroupName = "Memory")] public double AlphaTotal { get; set; } = 0.05;
		[Display(Name = "Outcome horizon (bars)", GroupName = "Outcome")] public int HorizonBars { get; set; } = 10;
		[Display(Name = "Outcome ATR k", GroupName = "Outcome")] public decimal OutcomeAtrK { get; set; } = 0.5m;
		[Display(Name = "Show expired", GroupName = "Display")] public bool ShowExpired { get; set; }

		// ---- state ----
		private readonly Dictionary<decimal, (decimal a, decimal b)> _profile = new();
		private readonly List<Zone> _zones = new();
		private readonly List<Pending> _pending = new();
		private readonly Dictionary<(bool aligned, int touch), Beta> _stats = new();
		private int _lastProcessed = -1, _barsInSession, _nextId = 1, _lastBar;
		private DateTime _sessionDate = DateTime.MinValue;
		private decimal _atr;
		private const decimal AtrAlpha = 2m / 15m;

		public NqQualifiedZones() : base(true)
		{
			DenyToChangePanel = true;
			Panel = IndicatorDataProvider.CandlesPanel;   // VERIFY: draw on the price panel
			EnableCustomDrawing = true;                                                  // without this OnRender is never called
			SubscribeToDrawingEvents(DrawingLayouts.Final);
		}

		protected override void OnCalculate(int bar, decimal value)
		{
			if (bar == 0) { ResetAll(); }
			_lastBar = bar;
			if (bar < 1 || bar - 1 <= _lastProcessed) return;
			_lastProcessed = bar - 1;

			var c = GetCandle(bar - 1);
			if (!TryNySession(c.Time, out var day)) return;
			if (day != _sessionDate) { ResetSession(); _sessionDate = day; }

			_barsInSession++;
			foreach (var lvl in c.GetAllPriceLevels())            // VERIFY: PriceVolumeInfo.Price/Ask/Bid
			{
				_profile.TryGetValue(lvl.Price, out var ab);
				_profile[lvl.Price] = (ab.a + lvl.Ask, ab.b + lvl.Bid);
			}

			var tr = Math.Max(c.High - c.Low, Math.Max(Math.Abs(c.High - c.Close), Math.Abs(c.Low - c.Close)));
			_atr = _atr == 0 ? tr : _atr + AtrAlpha * (tr - _atr);

			UpdateZones(bar - 1, c);
			ResolvePending(bar - 1, c);
			if (_barsInSession >= MinBars) DetectNewZones(bar - 1);
		}

		// ---------- session ----------
		private bool TryNySession(DateTime t, out DateTime day)
		{
			var tz = TimeZoneInfo.FindSystemTimeZoneById("America/New_York"); // use "Eastern Standard Time" on Windows
			var ny = TimeZoneInfo.ConvertTimeFromUtc(DateTime.SpecifyKind(t.AddHours(-ChartTimeOffsetHours), DateTimeKind.Utc), tz);
			day = ny.Date;
			var tod = ny.TimeOfDay;
			return tod >= new TimeSpan(9, 30, 0) && tod < new TimeSpan(16, 0, 0);
		}

		private void ResetSession()
		{
			foreach (var z in _zones.Where(z => z.State != ZState.Expired)) z.State = ZState.Expired; // no carry-over
			_profile.Clear(); _pending.Clear(); _barsInSession = 0; _atr = 0;
		}

		private void ResetAll() { ResetSession(); _zones.Clear(); _stats.Clear(); _lastProcessed = -1; _sessionDate = DateTime.MinValue; _nextId = 1; }

		// ---------- detection (spec §2) ----------
		private void DetectNewZones(int bar)
		{
			var tick = InstrumentInfo.TickSize;
			if (tick <= 0 || _profile.Count < 20) return;
			var lo = _profile.Keys.Min(); var hi = _profile.Keys.Max();
			var n = (int)((hi - lo) / tick) + 1;
			if (n < 20 || n > 5000) return;

			var v = new double[n]; var d = new double[n];
			foreach (var kv in _profile) { var i = (int)((kv.Key - lo) / tick); v[i] = (double)(kv.Value.a + kv.Value.b); d[i] = (double)(kv.Value.a - kv.Value.b); }

			var sm = Smooth(v, SmoothK);
			var nz = sm.Where(x => x > 0).ToArray();
			var med = Median(nz); var mad = 1.4826 * Median(nz.Select(x => Math.Abs(x - med)).ToArray());
			if (mad <= 1e-9) return;

			// overdispersion phi: median(D^2/V)/0.455
			var ratios = Enumerable.Range(0, n).Where(i => v[i] > 0).Select(i => d[i] * d[i] / v[i]).ToArray();
			var phi = Math.Max(1.0, Median(ratios) / 0.455);

			// local maxima with min separation 8 ticks
			var cand = new List<(int i, double z, double p)>();
			for (var i = 1; i < n - 1; i++)
			{
				if (sm[i] < sm[i - 1] || sm[i] <= sm[i + 1]) continue;
				var z = (sm[i] - med) / mad;
				if (z >= ZMin) cand.Add((i, z, NormalSf(z)));
			}
			cand = cand.OrderByDescending(x => x.z).Aggregate(new List<(int i, double z, double p)>(),
				(acc, x) => { if (acc.All(y => Math.Abs(y.i - x.i) >= 8)) acc.Add(x); return acc; });
			if (cand.Count == 0) return;

			// Benjamini-Hochberg
			var sorted = cand.OrderBy(x => x.p).ToList(); var m = sorted.Count; var kMax = -1;
			for (var k = 0; k < m; k++) if (sorted[k].p <= (k + 1.0) / m * FdrQ) kMax = k;
			if (kMax < 0) return;

			foreach (var c in sorted.Take(kMax + 1))
			{
				var price = lo + c.i * tick;
				if (_zones.Any(z => z.Day == _sessionDate && price >= z.Lo - 4 * tick && price <= z.Hi + 4 * tick)) continue; // also blocks re-creation of expired zones

				int l = c.i, u = c.i;                              // extend while smoothed >= 50% of peak, max 12 ticks
				while (l > 0 && sm[l - 1] >= 0.5 * sm[c.i] && c.i - l < 12) l--;
				while (u < n - 1 && sm[u + 1] >= 0.5 * sm[c.i] && u - c.i < 12) u++;

				double vz = 0, dz = 0; for (var i = l; i <= u; i++) { vz += v[i]; dz += d[i]; }
				var zi = dz / Math.Sqrt(phi * vz);
				if (Math.Abs(zi) < ZIMin) continue;

				var zone = new Zone
				{
					Id = _nextId++, Day = _sessionDate, FormBar = bar, LastBar = bar, Lo = lo + l * tick, Hi = lo + u * tick,
					MassV = (decimal)vz, ZI = (decimal)zi, Dir = Math.Sign(dz), Med0 = med, Mad0 = mad,
					ZV0 = (decimal)c.z, PBH = c.p, PeakSm = sm[c.i], Round = NearRound(price, tick)
				};
				_zones.Add(zone);
			}
		}

		// ---------- touches, consumption, alpha-spending, expiry (spec §3) ----------
		private void UpdateZones(int bar, IndicatorCandle c)
		{
			foreach (var z in _zones.Where(z => z.State != ZState.Expired && z.FormBar < bar))
			{
				z.LastBar = bar;
				var inside = c.Low <= z.Hi && c.High >= z.Lo;
				if (!inside)
				{
					if (!z.Armed && (c.Low > z.Hi + _atr || c.High < z.Lo - _atr)) z.Armed = true;
					continue;
				}

				decimal traded = 0;
				foreach (var lvl in c.GetAllPriceLevels()) if (lvl.Price >= z.Lo && lvl.Price <= z.Hi) traded += lvl.Volume;
				z.Consumed += traded;

				if (z.Armed)
				{
					z.Armed = false; z.Touches++;
					var dir = c.Open > z.Hi ? -1 : c.Open < z.Lo ? 1 : 0;       // approach direction (+1 = from below going up)
					if (dir != 0) _pending.Add(new Pending { Z = z, StartBar = bar, TouchIdx = z.Touches, ApproachDir = dir, Atr0 = _atr });

					var alphaN = AlphaTotal * Math.Pow(2, -(z.Touches + 1));     // alpha spending
					var remFrac = Math.Max((double)(1m - z.Consumed / z.MassV), 0);   // residual mass fraction
					var zEff = (z.PeakSm * remFrac - z.Med0) / z.Mad0;             // peak (smoothed units) scaled by residual mass
					z.State = NormalSf(zEff) <= alphaN ? ZState.Qualified : ZState.Weakened;
				}

				if (z.Consumed >= (decimal)Kappa * z.MassV || z.Touches > MaxTouches) z.State = ZState.Expired;
			}
		}

		// ---------- outcome labelling (spec §2e): statistics only ----------
		private void ResolvePending(int bar, IndicatorCandle c)
		{
			for (var i = _pending.Count - 1; i >= 0; i--)
			{
				var p = _pending[i]; var k = OutcomeAtrK * p.Atr0; int? res = null;   // +1 continuation, -1 rejection
				var beyond = p.ApproachDir > 0 ? c.Close > p.Z.Hi + k : c.Close < p.Z.Lo - k;
				var back = p.ApproachDir > 0 ? c.Close < p.Z.Lo - k : c.Close > p.Z.Hi + k;
				if (beyond) res = 1; else if (back) res = -1;
				var expired = bar - p.StartBar >= HorizonBars;
				if (res == null && !expired) continue;

				var key = (p.ApproachDir == p.Z.Dir, Math.Min(p.TouchIdx, 3));
				if (!_stats.TryGetValue(key, out var b)) _stats[key] = b = new Beta();
				if (res == 1) b.S++; else if (res == -1) b.F++; else b.N++;
				_pending.RemoveAt(i);
			}
		}

		private string Label(Zone z)
		{
			_stats.TryGetValue((true, Math.Min(Math.Max(z.Touches, 1), 3)), out var b);
			double a = 5 + (b?.S ?? 0), bb = 5 + (b?.F ?? 0);
			return $"Z{z.Id} T{z.Touches} zV={z.ZV0:F1} zI={z.ZI:F1} p̂={a / (a + bb):F2} (n={(b?.S ?? 0) + (b?.F ?? 0)}){(z.Round ? " R" : "")}";
		}

		// ---------- rendering ----------
		protected override void OnRender(RenderContext context, DrawingLayouts layout)   // VERIFY signature
		{
			if (ChartInfo is null || InstrumentInfo is null) return;
			if (layout != DrawingLayouts.Final) return;                                  // VERIFY enum member
			var font = new RenderFont("Arial", 9);
			foreach (var z in _zones)
			{
				if (z.State == ZState.Expired && !ShowExpired) continue;
				var x1 = ChartInfo.GetXByBar(z.FormBar);                                 // VERIFY
				var x2 = ChartInfo.GetXByBar(z.State == ZState.Expired ? z.LastBar : _lastBar);
				var yTop = ChartInfo.GetYByPrice(z.Hi + InstrumentInfo.TickSize);        // VERIFY
				var yBot = ChartInfo.GetYByPrice(z.Lo);
				var baseCol = z.Dir > 0 ? Color.FromArgb(0, 160, 90) : Color.FromArgb(200, 60, 60);
				var col = z.State switch
				{
					ZState.Qualified => Color.FromArgb(70, baseCol),
					ZState.Weakened => Color.FromArgb(35, Color.Gray),
					_ => Color.FromArgb(15, Color.Gray)
				};
				var rect = new Rectangle(x1, yTop, Math.Max(x2 - x1, 2), Math.Max(yBot - yTop, 2));
				context.FillRectangle(col, rect);
				if (z.State != ZState.Expired) context.DrawString(Label(z), font, Color.White, x1 + 2, yTop - 12);
			}
		}

		// ---------- helpers ----------
		private static double[] Smooth(double[] v, int k)
		{
			var o = new double[v.Length];
			for (var i = 0; i < v.Length; i++)
			{
				double s = 0, w = 0;
				for (var j = -k; j <= k; j++) { var idx = i + j; if (idx < 0 || idx >= v.Length) continue; var wt = k + 1 - Math.Abs(j); s += wt * v[idx]; w += wt; }
				o[i] = s / w;
			}
			return o;
		}

		private static double Median(double[] a)
		{
			if (a.Length == 0) return 0;
			var s = (double[])a.Clone(); Array.Sort(s);
			return s.Length % 2 == 1 ? s[s.Length / 2] : 0.5 * (s[s.Length / 2 - 1] + s[s.Length / 2]);
		}

		private static double NormalSf(double z) => 0.5 * Erfc(z / Math.Sqrt(2));

		private static double Erfc(double x)   // Abramowitz-Stegun 7.1.26 (|err| < 1.5e-7)
		{
			var t = 1.0 / (1.0 + 0.3275911 * Math.Abs(x));
			var y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.Exp(-x * x);
			return x >= 0 ? 1 - y : 1 + y;
		}

		private static bool NearRound(decimal price, decimal tick)
		{
			foreach (var step in new[] { 25m, 50m, 100m })
			{
				var r = price % step; var dist = Math.Min(r, step - r);
				if (dist <= 2 * tick) return true;
			}
			return false;
		}
	}
}
