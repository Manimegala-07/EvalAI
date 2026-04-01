"""
thesis_evaluation.py
Generates Figure 5.1, 5.2, 5.3 and prints the full ANOVA table
matching Chapter 5 of the thesis.

Run from project root:
    python thesis_evaluation.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
from itertools import combinations

# ── The 35 AI scores from your evaluation (7 per scenario) ──────────────────
# Replace these with your actual scores if you re-run the evaluation
SCENARIOS = {
    "Fully Correct":  [8.05, 7.52, 9.52, 8.08, 9.05, 8.11, 9.93],
    "Above Average":  [7.10, 5.99, 6.81, 6.97, 7.90, 5.92, 7.72],
    "Average":        [5.33, 7.02, 5.40, 6.58, 4.68, 5.19, 6.21],
    "Below Average":  [4.31, 3.67, 3.05, 3.66, 6.18, 2.52, 5.84],
    "Fully Wrong":    [3.22, 3.66, 3.12, 3.39, 4.12, 3.11, 4.20],
}

EXPECTED_MIDPOINTS = {
    "Fully Correct":  9.5,
    "Above Average":  7.5,
    "Average":        5.5,
    "Below Average":  3.5,
    "Fully Wrong":    1.5,
}

COLORS = ["#16A34A", "#2D5BE3", "#D97706", "#F87171", "#DC2626"]
SCENARIO_LABELS = list(SCENARIOS.keys())

all_scores  = [SCENARIOS[s] for s in SCENARIO_LABELS]
all_flat    = [score for group in all_scores for score in group]
group_labels= [s for s in SCENARIO_LABELS for _ in SCENARIOS[s]]


# ── ANOVA ────────────────────────────────────────────────────────────────────
f_stat, p_value = stats.f_oneway(*all_scores)

grand_mean  = np.mean(all_flat)
k           = len(SCENARIO_LABELS)
N           = len(all_flat)
n_per_group = N // k

ss_between = sum(len(SCENARIOS[s]) * (np.mean(SCENARIOS[s]) - grand_mean)**2 for s in SCENARIO_LABELS)
ss_within  = sum((x - np.mean(SCENARIOS[s]))**2 for s in SCENARIO_LABELS for x in SCENARIOS[s])
ss_total   = ss_between + ss_within

eta_sq     = ss_between / ss_total
cohens_f   = np.sqrt(eta_sq / (1 - eta_sq))

# Pearson r between AI scores and expected midpoints
ai_means   = [np.mean(SCENARIOS[s]) for s in SCENARIO_LABELS]
exp_mids   = [EXPECTED_MIDPOINTS[s]  for s in SCENARIO_LABELS]
pearson_r, _ = stats.pearsonr(ai_means, exp_mids)

# MAE per scenario
mae_per = {s: np.mean(np.abs(np.array(SCENARIOS[s]) - EXPECTED_MIDPOINTS[s])) for s in SCENARIO_LABELS}
overall_mae = np.mean(list(mae_per.values()))

# ── Print ANOVA table ─────────────────────────────────────────────────────────
print("\n" + "="*60)
print("   THESIS EVALUATION — ANOVA RESULTS")
print("="*60)
print(f"  F-statistic      : {f_stat:.4f}")
print(f"  p-value          : {p_value:.8f}  ({'< 0.0001' if p_value < 0.0001 else f'{p_value:.4f}'})")
print(f"  Eta-squared (n2) : {eta_sq:.4f}")
print(f"  Cohen's f        : {cohens_f:.4f}")
print(f"  Pearson r        : {pearson_r:.4f}")
print(f"  Decision         : {'REJECT H0' if p_value < 0.05 else 'FAIL TO REJECT H0'}")
print()
print("  Per-scenario stats:")
print(f"  {'Scenario':<18} {'Mean':>6} {'Std':>6} {'MAE':>6}")
print("  " + "-"*40)
for s in SCENARIO_LABELS:
    arr = np.array(SCENARIOS[s])
    print(f"  {s:<18} {arr.mean():>6.2f} {arr.std():>6.2f} {mae_per[s]:>6.4f}")
print(f"\n  Overall MAE: {overall_mae:.4f}")

# ── Pairwise t-tests with Bonferroni correction ───────────────────────────────
pairs = list(combinations(SCENARIO_LABELS, 2))
n_pairs = len(pairs)
print(f"\n  Pairwise t-tests (Bonferroni corrected, n_pairs={n_pairs}):")
print(f"  {'Pair':<42} {'Corrected p':>12} {'Sig?':>6}")
print("  " + "-"*62)
for a, b in pairs:
    _, raw_p = stats.ttest_ind(SCENARIOS[a], SCENARIOS[b])
    corrected = min(raw_p * n_pairs, 1.0)
    sig = "✓ Yes" if corrected < 0.05 else "✗ No"
    print(f"  {a+' vs '+b:<42} {corrected:>12.6f} {sig:>6}")

print("="*60)


# ── FIGURE 5.1 — Box Plot ────────────────────────────────────────────────────
fig1, ax1 = plt.subplots(figsize=(10, 6))

bp = ax1.boxplot(all_scores, patch_artist=True, notch=False,
                 medianprops=dict(color="white", linewidth=2.5))

for patch, color in zip(bp["boxes"], COLORS):
    patch.set_facecolor(color)
    patch.set_alpha(0.8)
for whisker in bp["whiskers"]:
    whisker.set(color="#555", linewidth=1.5, linestyle="--")
for cap in bp["caps"]:
    cap.set(color="#555", linewidth=1.5)
for flier in bp["fliers"]:
    flier.set(marker="o", color="#999", alpha=0.5)

ax1.set_xticks(range(1, k + 1))
ax1.set_xticklabels(SCENARIO_LABELS, fontsize=11)
ax1.set_ylabel("AI Score (out of 10)", fontsize=12)
ax1.set_title(
    f"Figure 5.1: Score Distribution Across Five Answer Quality Levels\n"
    f"F({k-1}, {N-k}) = {f_stat:.2f}, p < 0.0001, n2 = {eta_sq:.4f}",
    fontsize=12, pad=12
)
ax1.set_ylim(0, 11)
ax1.axhline(grand_mean, color="gray", linestyle=":", linewidth=1, label=f"Grand mean = {grand_mean:.2f}")
ax1.legend(fontsize=10)
ax1.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("thesis_fig5_1_boxplot.png", dpi=150, bbox_inches="tight")
print("\n  ✅ Saved: thesis_fig5_1_boxplot.png")
plt.show()


# ── FIGURE 5.2 — Mean AI Score vs Expected Midpoints ────────────────────────
fig2, ax2 = plt.subplots(figsize=(9, 5))

x = np.arange(k)
width = 0.35

bars1 = ax2.bar(x - width/2, exp_mids,  width, label="Expected Midpoint", color="#CBD5E1", edgecolor="#64748B")
bars2 = ax2.bar(x + width/2, ai_means,  width, label="Mean AI Score",     color="#2D5BE3", edgecolor="#1A3A9E", alpha=0.85)

# Difference annotations
for i, (exp, ai) in enumerate(zip(exp_mids, ai_means)):
    diff = ai - exp
    color = "#16A34A" if abs(diff) < 1 else "#DC2626"
    ax2.annotate(f"{diff:+.2f}", xy=(x[i] + width/2, ai + 0.15),
                 ha="center", fontsize=9, color=color, fontweight="bold")

ax2.set_xticks(x)
ax2.set_xticklabels(SCENARIO_LABELS, fontsize=10)
ax2.set_ylabel("Score (out of 10)", fontsize=12)
ax2.set_title(
    f"Figure 5.2: Mean AI Score vs Expected Midpoints per Scenario\n"
    f"Pearson r = {pearson_r:.4f}, Overall MAE = {overall_mae:.4f}",
    fontsize=12, pad=12
)
ax2.set_ylim(0, 12)
ax2.legend(fontsize=10)
ax2.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("thesis_fig5_2_means.png", dpi=150, bbox_inches="tight")
print("  ✅ Saved: thesis_fig5_2_means.png")
plt.show()


# ── FIGURE 5.3 — Individual Scores per Scenario (scatter + mean line) ────────
fig3, ax3 = plt.subplots(figsize=(10, 6))

for i, (s, color) in enumerate(zip(SCENARIO_LABELS, COLORS)):
    scores = SCENARIOS[s]
    jitter = np.random.uniform(-0.15, 0.15, len(scores))
    ax3.scatter([i + j for j in jitter], scores, color=color, s=70, alpha=0.8, zorder=3)
    ax3.hlines(np.mean(scores), i - 0.3, i + 0.3, colors=color, linewidth=2.5, zorder=4)
    ax3.hlines(EXPECTED_MIDPOINTS[s], i - 0.3, i + 0.3,
               colors="black", linewidth=1.5, linestyles="--", zorder=4)

ax3.set_xticks(range(k))
ax3.set_xticklabels(SCENARIO_LABELS, fontsize=11)
ax3.set_ylabel("AI Score (out of 10)", fontsize=12)
ax3.set_title("Figure 5.3: Individual AI Scores per Scenario with Group Means", fontsize=12, pad=12)
ax3.set_ylim(0, 11)
ax3.grid(axis="y", alpha=0.3)

legend_handles = [
    mpatches.Patch(color=c, label=s, alpha=0.8)
    for s, c in zip(SCENARIO_LABELS, COLORS)
] + [
    plt.Line2D([0], [0], color="black", linewidth=1.5, linestyle="--", label="Expected midpoint"),
]
ax3.legend(handles=legend_handles, fontsize=9, loc="upper right")
plt.tight_layout()
plt.savefig("thesis_fig5_3_scatter.png", dpi=150, bbox_inches="tight")
print("  ✅ Saved: thesis_fig5_3_scatter.png")
plt.show()
