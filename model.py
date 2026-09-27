"""
Is Nvidia the next Cisco? A Monte Carlo test.
Author: Jacob Rodan
Run: pip install numpy matplotlib reportlab  ->  python build.py
"""
import numpy as np

# ---------------- inputs (sources in the paper) ----------------
MARKET_CAP = 5.43e12                            # Sept 25, 2026
Q_REV = [57.0e9, 68.1e9, 81.6e9, 96.2e9]        # last four reported quarters (NVIDIA 8-Ks)
REV_TTM = sum(Q_REV)
YEARS, Q = 5, 20
N = 100_000
BUYBACK = 0.01                                  # net share count shrink per year
rng = np.random.default_rng(2026)

def simulate(n=N, rng=rng, bust_p=0.12):
    g1 = np.clip(rng.normal(0.35, 0.15, n), 0.0, 0.9)   # growth of the revenue run-rate, next 12 months
    decay = rng.uniform(0.45, 0.80, n)                   # how fast hypergrowth fades each year
    floor = 0.04                                         # long-run growth
    margin = rng.uniform(0.35, 0.55, n)                  # net margin in 2031
    pe = rng.uniform(15, 35, n)                          # P/E in 2031
    q_start = 1 - (1 - bust_p) ** 0.25                   # chance a bust starts in a given quarter
    q = np.empty((n, Q + 1)); q[:, 0] = Q_REV[-1]
    left = np.zeros(n, int); size = np.zeros(n); any_bust = np.zeros(n, bool)
    for t in range(1, Q + 1):
        g_ann = np.maximum(g1 * decay ** ((t - 1) // 4), floor)
        step = (1 + g_ann) ** 0.25 - 1 + rng.normal(0, 0.035, n)
        start = (left == 0) & (rng.random(n) < q_start)
        size[start] = rng.uniform(0.20, 0.50, start.sum()); left[start] = 2; any_bust |= start
        in_bust = left > 0
        step[in_bust] = (1 - size[in_bust]) ** 0.5 - 1   # the drop plays out over two quarters
        left[in_bust] -= 1
        q[:, t] = q[:, t - 1] * (1 + step)
    ttm5 = q[:, -4:].sum(axis=1)
    value5 = ttm5 * margin * pe * (1 + BUYBACK) ** YEARS
    ret = (value5 / MARKET_CAP) ** (1 / YEARS) - 1
    return {"q": q, "ttm5": ttm5, "ret": ret, "g1": g1, "decay": decay, "margin": margin, "pe": pe, "any_bust": any_bust}
