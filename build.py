import numpy as np, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from model import simulate, MARKET_CAP, REV_TTM, YEARS, BUYBACK, Q

s = simulate(); r = s["ret"]; rev = s["q"] * 4; bust = s["any_bust"]
need0 = MARKET_CAP / (0.45 * 25) / (1 + BUYBACK) ** YEARS
need10 = need0 * 1.10 ** YEARS
R = {
 "median": np.median(r), "p_loss": np.mean(r < 0), "p10": np.mean(r > 0.10), "p20": np.mean(r > 0.20),
 "p_half": np.mean((1 + r) ** 5 < 0.5), "bust_share": bust.mean(),
 "med_bust": np.median(r[bust]), "med_nobust": np.median(r[~bust]),
 "rev5": np.median(s["ttm5"]), "need0": need0, "need10": need10,
}
curve = []
for bp in np.linspace(0, 0.30, 16):
    rr = simulate(bust_p=bp, rng=np.random.default_rng(1))["ret"]
    curve.append((bp, np.median(rr), np.mean(rr < 0)))
curve = np.array(curve)
be = float(np.interp(-0.10, -curve[:, 1], curve[:, 0]))   # bust prob where median return = 10%
R["breakeven_bust"] = be
sens = {}
for k, lab in [("g1", "Next-year growth"), ("decay", "Speed growth fades"), ("margin", "Year-5 net margin"), ("pe", "Year-5 P/E")]:
    x = s[k]; sens[lab] = (np.median(r[x < np.quantile(x, .1)]), np.median(r[x > np.quantile(x, .9)]))
sens["AI spending bust"] = (R["med_bust"], R["med_nobust"])
for k, v in R.items(): print(k, v)
print("sens", sens)

# ---------------- figures ----------------
plt.rcParams.update({"font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False})
years = 2026.5 + np.arange(Q + 1) / 4
rng = np.random.default_rng(5); idx = rng.choice(len(r), 1000, replace=False)
cmap = plt.get_cmap("turbo")

def spaghetti(ax, lw=0.5):
    for j, i in enumerate(idx):
        ax.plot(years, rev[i] / 1e9, lw=lw, alpha=0.55, color=cmap(0.05 + 0.9 * rng.random()))
    ax.axhline(need0 / 1e9, color="#222", lw=1.3, ls="--")
    ax.axhline(need10 / 1e9, color="#b2182b", lw=1.6, ls="--")
    ax.set_yscale("log"); ax.set_xticks(range(2027, 2032)); ax.set_xlim(2026.4, 2031.6)
    ax.set_yticks([100, 200, 300, 500, 1000, 2000]); ax.set_yticklabels(["$100B", "$200B", "$300B", "$500B", "$1T", "$2T"])
    ax.set_ylim(90, 2500); ax.grid(alpha=0.25)

fig, ax = plt.subplots(figsize=(7, 3.1))
spaghetti(ax)
bb = dict(fc="white", ec="none", alpha=0.85, pad=1.5)
ax.text(2026.55, need10 / 1e9 * 1.06, f"Needed to return 10%/yr: ${need10/1e9:.0f}B", color="#b2182b", fontsize=9, bbox=bb)
ax.text(2026.55, need0 / 1e9 * 1.06, f"Needed to break even: ${need0/1e9:.0f}B", color="#222", fontsize=9, bbox=bb)
ax.set_ylabel("Annualized revenue (log scale)")
fig.tight_layout(); fig.savefig("fig1.png", dpi=300); plt.close(fig)

fig, (a, b) = plt.subplots(1, 2, figsize=(7, 2.8))
bins = np.linspace(-0.4, 0.5, 60)
a.hist(100 * r[~bust], bins=100 * bins, alpha=0.75, color="#4575b4", label="No AI spending bust")
a.hist(100 * r[bust], bins=100 * bins, alpha=0.65, color="#d73027", label="At least one bust")
a.axvline(0, c="#222", lw=0.9); a.axvline(10, c="#222", lw=0.9, ls=":")
a.set_xlabel("Annual return, 2026-2031 (%)"); a.set_ylabel("Number of simulations")
a.set_title("(a) Two different worlds", loc="left"); a.legend(frameon=False, fontsize=8)
b.plot(100 * curve[:, 0], 100 * curve[:, 1], c="#222", lw=1.6, marker="o", ms=3)
b.axhline(10, c="#b2182b", lw=1, ls="--"); b.axhline(0, c="#999", lw=0.8)
b.axvline(100 * be, c="#b2182b", lw=0.8, ls=":")
b.text(100 * be + 0.8, 0.72, f"about {100*be:.0f}% per year", color="#b2182b", fontsize=9, transform=b.get_xaxis_transform(), va="top")
b.set_xlabel("Annual chance of an AI spending bust (%)"); b.set_ylabel("Median annual return (%)")
b.set_title("(b) The number that decides it", loc="left")
fig.tight_layout(); fig.savefig("fig2.png", dpi=300); plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 2.0))
items = sorted(sens.items(), key=lambda kv: abs(kv[1][1] - kv[1][0]))
for i, (lab, (lo, hi)) in enumerate(items):
    ax.barh(i, 100 * (hi - lo), left=100 * lo, color="#b2182b" if lab == "AI spending bust" else "#888", height=0.55)
ax.set_yticks(range(len(items)), [k for k, _ in items]); ax.axvline(100 * R["median"], c="#222", lw=0.9)
ax.set_xlabel("Median annual return when the input is at its worst vs. best 10% (%)")
fig.tight_layout(); fig.savefig("fig3.png", dpi=300); plt.close(fig)

# LinkedIn image
plt.rcParams.update({"font.family": "DejaVu Sans"})
fig = plt.figure(figsize=(10, 11.25), dpi=120)
ax = fig.add_axes([0.08, 0.1, 0.88, 0.7])
spaghetti(ax, lw=0.6)
bb = dict(fc="white", ec="none", alpha=0.85, pad=2)
ax.text(2026.55, need10 / 1e9 * 1.06, f"Revenue needed to return 10% a year: ${need10/1e9:.0f}B", color="#b2182b", fontsize=12, fontweight="bold", bbox=bb)
ax.text(2026.55, need0 / 1e9 * 1.06, f"Revenue needed just to break even: ${need0/1e9:.0f}B", color="#222", fontsize=12, bbox=bb)
ax.tick_params(labelsize=12)
fig.text(0.08, 0.935, "Is Nvidia the next Cisco?", fontsize=26, fontweight="bold")
fig.text(0.08, 0.895, "100,000 simulated futures for Nvidia's revenue, 2026 to 2031. 1,000 shown.", fontsize=13.5, color="#555")
fig.text(0.08, 0.845, f"No AI spending bust:  median return {100*R['med_nobust']:.0f}% a year.     "
         f"At least one bust:  {100*R['med_bust']:.0f}% a year.", fontsize=13.5, fontweight="bold")
fig.text(0.08, 0.035, "Assumes 35-55% net margin and a 15-35x P/E in 2031, 45%/25x for the lines. Model, not a forecast.",
         fontsize=9.5, color="#666")
fig.savefig("linkedin_nvidia_monte_carlo.png", facecolor="white"); plt.close(fig)

# equations
def eq(tex, path):
    f = plt.figure(figsize=(0.01, 0.01)); plt.rcParams["font.family"] = "STIXGeneral"
    f.text(0, 0, f"${tex}$", fontsize=13); f.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.02, transparent=True); plt.close(f)
eq(r"R_{t}=R_{t-1}\,(1+g_{t}),\qquad g_{t}=\max\left(g_{1}\,\rho^{\,t-1},\;4\%\right)\ \ \mathrm{normal\ year},\qquad g_{t}=-b_{t}\ \ \mathrm{bust\ year}", "eq1.png")
eq(r"V_{5}=R_{5}\times m\times \mathrm{P/E}\times(1.01)^{5},\qquad r=\left(V_{5}/V_{0}\right)^{1/5}-1", "eq2.png")

import json; json.dump({k: float(v) for k, v in R.items()} | {"sens": {k: [float(a), float(b)] for k, (a, b) in sens.items()}}, open("results.json", "w"), indent=1)
