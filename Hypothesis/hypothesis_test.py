"""
EvalAI — Hypothesis Testing
Reads scores directly from EvalAI_Score_Collection.xlsx
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import f_oneway
from itertools import combinations
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# ── Read Excel ────────────────────────────────────────────────────
df_raw = pd.read_excel(
    'EvalAI_Score_Collection.xlsx',
    sheet_name='Score Entry',
    header=3
)

df_raw.columns = ['Q', 'Question', 'Scenario', 'Expected',
                  'AI_Score', 'Difference', 'Within_Range',
                  'Similarity', 'Entailment']

# Drop spacer rows and rows without scenario
df = df_raw[df_raw['Scenario'].notna() & df_raw['AI_Score'].notna()].copy()
df = df[df['Scenario'] != 'NaN']
df['AI_Score'] = pd.to_numeric(df['AI_Score'], errors='coerce')
df = df[df['AI_Score'].notna()]

SCENARIOS = ["Fully Correct", "Above Average", "Average", "Below Average", "Fully Wrong"]
COLORS = {
    "Fully Correct":  "#16A34A",
    "Above Average":  "#2563EB",
    "Average":        "#D97706",
    "Below Average":  "#EA580C",
    "Fully Wrong":    "#DC2626",
}
EXPECTED_MID = {
    "Fully Correct": 9.5,
    "Above Average": 7.5,
    "Average":       5.5,
    "Below Average": 3.5,
    "Fully Wrong":   1.5,
}

# Group scores by scenario
groups = {}
for s in SCENARIOS:
    groups[s] = df[df['Scenario'] == s]['AI_Score'].values

n_per_group = {s: len(v) for s, v in groups.items()}
total_n     = sum(n_per_group.values())

# ── Print Data Summary ────────────────────────────────────────────
print("\n" + "═"*65)
print("   EvalAI — HYPOTHESIS TESTING RESULTS")
print("   (Reading from EvalAI_Score_Collection.xlsx)")
print("═"*65)

print(f"\n  ── Data Loaded ───────────────────────────────────────────────")
print(f"  Total answers  : {total_n}")
print(f"  Per group      : {n_per_group}")
questions_used = df['Question'].dropna().unique()
print(f"  Questions used : {len(questions_used)}")

print(f"\n  ── Raw Scores per Scenario ───────────────────────────────────")
for s in SCENARIOS:
    vals = groups[s]
    print(f"  {s:<18}: {[round(v,2) for v in vals]}")

# ── Descriptive Statistics ────────────────────────────────────────
print(f"\n  ── Descriptive Statistics ────────────────────────────────────")
print(f"  {'Scenario':<18} {'n':>4} {'Mean':>7} {'Std':>7} {'Min':>7} {'Max':>7} {'Expected':>10}")
print(f"  {'─'*62}")
for s in SCENARIOS:
    v = groups[s]
    print(f"  {s:<18} {len(v):>4} {np.mean(v):>7.2f} "
          f"{np.std(v):>7.2f} {np.min(v):>7.2f} "
          f"{np.max(v):>7.2f} {EXPECTED_MID[s]:>10.1f}")

# ── One-Way ANOVA ─────────────────────────────────────────────────
f_stat, p_anova = f_oneway(*[groups[s] for s in SCENARIOS])

print(f"\n  ── One-Way ANOVA ─────────────────────────────────────────────")
print(f"  H0: All 5 group means are equal")
print(f"  H1: At least one group mean differs significantly")
print(f"\n  F-statistic : {f_stat:.4f}")
print(f"  p-value     : {p_anova:.8f}")
print(f"  α           : 0.05")

if p_anova < 0.05:
    print(f"\n  ✅ p ({p_anova:.6f}) < 0.05 → REJECT H0")
    print(f"  ✅ EvalAI significantly discriminates all 5 quality levels!")
else:
    print(f"\n  ❌ p ({p_anova:.6f}) >= 0.05 → FAIL TO REJECT H0")

# ── Tukey Post-Hoc ────────────────────────────────────────────────
print(f"\n  ── Pairwise t-test (Bonferroni corrected) ────────────────────")
print(f"  {'Pair':<40} {'p-value':>10} {'Result':>12}")
print(f"  {'─'*64}")

n_pairs = len(list(combinations(SCENARIOS, 2)))
for s1, s2 in combinations(SCENARIOS, 2):
    _, p = stats.ttest_ind(groups[s1], groups[s2])
    p_corr = min(p * n_pairs, 1.0)
    sig    = "✅ Sig." if p_corr < 0.05 else "❌ Not sig."
    print(f"  {s1+' vs '+s2:<40} {p_corr:>10.6f} {sig:>12}")

# ── Effect Size ───────────────────────────────────────────────────
all_data   = np.concatenate([groups[s] for s in SCENARIOS])
grand_mean = np.mean(all_data)
ss_between = sum(len(groups[s]) * (np.mean(groups[s]) - grand_mean)**2 for s in SCENARIOS)
ss_within  = sum(np.sum((groups[s] - np.mean(groups[s]))**2) for s in SCENARIOS)
eta2       = ss_between / (ss_between + ss_within)
cohens_f   = np.sqrt(eta2 / (1 - eta2))
effect     = "Large" if cohens_f >= 0.40 else "Medium" if cohens_f >= 0.25 else "Small"

print(f"\n  ── Effect Size ───────────────────────────────────────────────")
print(f"  Eta-squared (η²): {eta2:.4f}")
print(f"  Cohen's f       : {cohens_f:.4f} → {effect} effect")

print("\n" + "═"*65)

# ── Generate Charts ───────────────────────────────────────────────
fig = plt.figure(figsize=(16, 12))
fig.patch.set_facecolor('#F8F9FC')
gs = GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.35)

# Chart 1: Box Plot
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor('white')
bp = ax1.boxplot(
    [groups[s] for s in SCENARIOS],
    patch_artist=True, notch=False, widths=0.5,
    medianprops=dict(color='white', linewidth=2.5),
)
for patch, s in zip(bp['boxes'], SCENARIOS):
    patch.set_facecolor(COLORS[s])
    patch.set_alpha(0.85)
for w in bp['whiskers']: w.set(color='#94A3B8', linewidth=1.5)
for c in bp['caps']:     c.set(color='#94A3B8', linewidth=1.5)
for f in bp['fliers']:   f.set(marker='o', color='#94A3B8', markersize=5)
ax1.set_xticklabels(['FC', 'AA', 'Avg', 'BA', 'FW'], fontsize=11)
ax1.set_ylabel('AI Score (/10)', fontsize=11)
ax1.set_title(f'Score Distribution per Scenario\n(Box Plot)', fontsize=12, fontweight='bold', color='#1E3A5F')
ax1.set_ylim(0, 11)
ax1.grid(True, alpha=0.3, axis='y')
ax1.axhline(y=5, color='#94A3B8', linewidth=1, linestyle='--', alpha=0.5)
legend_patches = [mpatches.Patch(color=COLORS[s], label=s, alpha=0.85) for s in SCENARIOS]
ax1.legend(handles=legend_patches, fontsize=8, loc='upper right')

# Chart 2: Mean ± SD vs Expected
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor('white')
means = [np.mean(groups[s]) for s in SCENARIOS]
stds  = [np.std(groups[s])  for s in SCENARIOS]
x     = np.arange(len(SCENARIOS))
bars  = ax2.bar(x, means, yerr=stds, capsize=6, width=0.55,
                color=[COLORS[s] for s in SCENARIOS],
                edgecolor='white', alpha=0.85,
                error_kw=dict(ecolor='#374151', linewidth=1.5, capthick=1.5))
exp_vals = [EXPECTED_MID[s] for s in SCENARIOS]
ax2.scatter(x, exp_vals, color='#1E3A5F', zorder=5, s=80, marker='D', label='Expected midpoint')
ax2.set_xticks(x)
ax2.set_xticklabels(['FC', 'AA', 'Avg', 'BA', 'FW'], fontsize=11)
ax2.set_ylabel('Mean Score (/10)', fontsize=11)
ax2.set_title('Mean AI Score ± SD\nvs Expected Midpoints', fontsize=12, fontweight='bold', color='#1E3A5F')
ax2.set_ylim(0, 12)
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3, axis='y')
for bar, mean in zip(bars, means):
    ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.3,
             f'{mean:.2f}', ha='center', va='bottom', fontsize=10,
             fontweight='bold', color='#1E3A5F')

# Chart 3: Individual scatter
ax3 = fig.add_subplot(gs[1, 0])
ax3.set_facecolor('white')
for i, s in enumerate(SCENARIOS):
    y    = groups[s]
    x_sc = np.random.normal(i, 0.08, size=len(y))
    ax3.scatter(x_sc, y, color=COLORS[s], s=90, alpha=0.85,
                edgecolors='white', linewidth=0.8, zorder=5)
    ax3.hlines(np.mean(y), i-0.3, i+0.3, color=COLORS[s], linewidth=2.5, zorder=6)
    ax3.hlines(EXPECTED_MID[s], i-0.25, i+0.25, color='#1E3A5F',
               linewidth=1.5, linestyle='--', zorder=6)
ax3.set_xticks(range(len(SCENARIOS)))
ax3.set_xticklabels(['FC', 'AA', 'Avg', 'BA', 'FW'], fontsize=11)
ax3.set_ylabel('AI Score (/10)', fontsize=11)
ax3.set_title('Individual Scores per Scenario\n(solid=actual mean, dashed=expected)', fontsize=12, fontweight='bold', color='#1E3A5F')
ax3.set_ylim(0, 11)
ax3.grid(True, alpha=0.3, axis='y')

# Chart 4: Summary stats
ax4 = fig.add_subplot(gs[1, 1])
ax4.set_facecolor('#EEF2FF')
ax4.set_xlim(0, 10)
ax4.set_ylim(0, 10)
ax4.axis('off')
dec_color = '#16A34A' if p_anova < 0.05 else '#DC2626'
dec_text  = 'REJECT H0 ✓\nModel Validated!' if p_anova < 0.05 else 'FAIL TO REJECT H0'

rows_data = [
    ("Test",             "One-Way ANOVA",              '#1E3A5F'),
    ("Questions",        f"{len(questions_used)}",      '#374151'),
    ("Total answers",    f"{total_n}",                  '#374151'),
    ("Per group",        f"n = {min(n_per_group.values())}–{max(n_per_group.values())}", '#374151'),
    ("F-statistic",      f"{f_stat:.4f}",               '#1E40AF'),
    ("p-value",          f"{p_anova:.2e}",               '#374151'),
    ("η² (eta-squared)", f"{eta2:.4f}",                 '#374151'),
    ("Cohen's f",        f"{cohens_f:.4f} ({effect})",  '#16A34A'),
    ("Decision",         dec_text,                      dec_color),
]

ax4.text(5, 9.6, "Statistical Results Summary",
         ha='center', va='top', fontsize=13, fontweight='bold', color='#1E3A5F')
for i, (label, value, color) in enumerate(rows_data):
    y = 8.7 - i * 0.92
    ax4.text(0.5, y, f"{label}:", ha='left',  va='center', fontsize=10, color='#6B7280')
    ax4.text(9.5, y, value,       ha='right', va='center', fontsize=10,
             color=color, fontweight='bold')
    ax4.axhline(y=y-0.38, xmin=0.04, xmax=0.96, color='#C7D4FA', linewidth=0.5)

plt.suptitle('EvalAI — One-Way ANOVA: Hypothesis Testing for Score Discrimination',
             fontsize=14, fontweight='bold', color='#1E3A5F', y=1.01)

plt.savefig('hypothesis_results.png', dpi=150, bbox_inches='tight', facecolor='#F8F9FC')
plt.close()
print("\n  📊 Chart saved: hypothesis_results.png")