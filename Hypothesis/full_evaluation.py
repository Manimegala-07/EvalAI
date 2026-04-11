"""
EvalAI — Complete Evaluation Metrics
Includes:
  1. Spearman Correlation
  2. Quadratic Weighted Kappa (QWK)
  3. Precision / Recall / F1
  4. Confusion Matrix
  5. MAE overall + per difficulty level
  6. One-Way ANOVA + Effect Size
  7. Bland-Altman Analysis
  8. Pearson Correlation
  9. Score Consistency Check

Run: python -m Hypothesis.full_evaluation
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from scipy import stats
from scipy.stats import spearmanr, pearsonr, f_oneway
from sklearn.metrics import (
    cohen_kappa_score, precision_score,
    recall_score, f1_score, confusion_matrix
)
from itertools import combinations
import warnings
warnings.filterwarnings("ignore")

# ── Load Data ─────────────────────────────────────────────────
df_raw = pd.read_excel(
    "EvalAI_Score_Collection.xlsx",
    sheet_name="Score Entry",
    header=3
)
df_raw.columns = ["Q","Question","Scenario","Expected","AI_Score","Difference","Within_Range","Similarity","Entailment"]
df = df_raw[df_raw["Scenario"].notna() & df_raw["AI_Score"].notna()].copy()
df["AI_Score"] = pd.to_numeric(df["AI_Score"], errors="coerce")
df = df[df["AI_Score"].notna()]

SCENARIOS = ["Fully Correct","Above Average","Average","Below Average","Fully Wrong"]
EXPECTED_MID = {"Fully Correct":9.5,"Above Average":7.5,"Average":5.5,"Below Average":3.5,"Fully Wrong":1.5}
COLORS = {"Fully Correct":"#16A34A","Above Average":"#2563EB","Average":"#D97706","Below Average":"#EA580C","Fully Wrong":"#DC2626"}

groups = {s: df[df["Scenario"]==s]["AI_Score"].values for s in SCENARIOS}
all_ai     = np.concatenate([groups[s] for s in SCENARIOS])
all_exp    = np.concatenate([[EXPECTED_MID[s]]*len(groups[s]) for s in SCENARIOS])
total_n    = len(all_ai)
questions_used = df["Question"].dropna().unique()

# ── Grade band helper ──────────────────────────────────────────
def band3(score):
    if score <= 3:   return 0   # Incorrect
    elif score <= 6: return 1   # Partial
    else:            return 2   # Correct

def band2(score):
    return 1 if score >= 5 else 0  # Pass / Fail

ai_band3  = [band3(s) for s in all_ai]
exp_band3 = [band3(s) for s in all_exp]
ai_band2  = [band2(s) for s in all_ai]
exp_band2 = [band2(s) for s in all_exp]

sep = "=" * 65

print(f"\n{sep}")
print("   EvalAI — COMPLETE EVALUATION METRICS REPORT")
print(f"{sep}")
print(f"  Total answers  : {total_n}")
print(f"  Questions used : {len(questions_used)}")
print(f"  Per scenario   : {dict((s, len(groups[s])) for s in SCENARIOS)}")

# ══════════════════════════════════════════════════════════════
# 1. SPEARMAN CORRELATION
# ══════════════════════════════════════════════════════════════
spearman_r, spearman_p = spearmanr(all_ai, all_exp)
print(f"\n{sep}")
print("  1. SPEARMAN RANK CORRELATION")
print(f"{sep}")
print(f"  Spearman r : {spearman_r:.4f}")
print(f"  p-value    : {spearman_p:.6f}")
interp = "Very Strong" if abs(spearman_r)>=0.9 else "Strong" if abs(spearman_r)>=0.7 else "Moderate" if abs(spearman_r)>=0.5 else "Weak"
print(f"  Strength   : {interp}")
print(f"  Meaning    : AI ranks answers in the same order as expected scores")

# ══════════════════════════════════════════════════════════════
# 2. PEARSON CORRELATION
# ══════════════════════════════════════════════════════════════
pearson_r, pearson_p = pearsonr(all_ai, all_exp)
print(f"\n{sep}")
print("  2. PEARSON CORRELATION")
print(f"{sep}")
print(f"  Pearson r  : {pearson_r:.4f}")
print(f"  p-value    : {pearson_p:.6f}")
print(f"  R-squared  : {pearson_r**2:.4f} ({round(pearson_r**2*100,1)}% variance explained)")
print(f"  Meaning    : Linear relationship between AI scores and expected scores")

# ══════════════════════════════════════════════════════════════
# 3. QUADRATIC WEIGHTED KAPPA
# ══════════════════════════════════════════════════════════════
qwk = cohen_kappa_score(ai_band3, exp_band3, weights="quadratic")
print(f"\n{sep}")
print("  3. QUADRATIC WEIGHTED KAPPA (QWK)")
print(f"{sep}")
print(f"  QWK        : {qwk:.4f}")
kappa_interp = "Excellent" if qwk>0.8 else "Strong" if qwk>0.65 else "Moderate" if qwk>0.5 else "Weak"
print(f"  Agreement  : {kappa_interp}")
print(f"  Bands used : 0-3=Incorrect, 4-6=Partial, 7-10=Correct")
print(f"  Meaning    : Agreement between AI and expected grade bands (penalizes large disagreements more)")

# ══════════════════════════════════════════════════════════════
# 4. PRECISION / RECALL / F1
# ══════════════════════════════════════════════════════════════
precision = precision_score(exp_band2, ai_band2, zero_division=0)
recall    = recall_score(exp_band2, ai_band2, zero_division=0)
f1        = f1_score(exp_band2, ai_band2, zero_division=0)
print(f"\n{sep}")
print("  4. PRECISION / RECALL / F1 (Pass/Fail Classification)")
print(f"{sep}")
print(f"  Threshold  : Score >= 5 = Pass, < 5 = Fail")
print(f"  Precision  : {precision:.4f}  — of answers AI said PASS, how many were actually PASS")
print(f"  Recall     : {recall:.4f}  — of actual PASS answers, how many did AI correctly identify")
print(f"  F1 Score   : {f1:.4f}  — harmonic mean of precision and recall")
print(f"  Meaning    : AI classification accuracy for pass/fail grading")

# ══════════════════════════════════════════════════════════════
# 5. CONFUSION MATRIX
# ══════════════════════════════════════════════════════════════
cm = confusion_matrix(exp_band3, ai_band3)
labels = ["Incorrect (0-3)", "Partial (4-6)", "Correct (7-10)"]
print(f"\n{sep}")
print("  5. CONFUSION MATRIX (3-class: Incorrect / Partial / Correct)")
print(f"{sep}")
print(f"  {'':20} {'AI: Incorrect':>14} {'AI: Partial':>12} {'AI: Correct':>12}")
print(f"  {'-'*60}")
for i, label in enumerate(labels):
    row = cm[i] if i < len(cm) else [0,0,0]
    print(f"  {'Exp: '+label:<20} {row[0] if len(row)>0 else 0:>14} {row[1] if len(row)>1 else 0:>12} {row[2] if len(row)>2 else 0:>12}")
total_correct_class = np.trace(cm)
accuracy = total_correct_class / total_n
print(f"\n  Classification Accuracy : {accuracy:.4f} ({round(accuracy*100,1)}%)")
print(f"  Meaning : How often AI assigns the correct grade band")

# ══════════════════════════════════════════════════════════════
# 6. MAE — OVERALL + PER SCENARIO
# ══════════════════════════════════════════════════════════════
overall_mae = np.mean(np.abs(all_ai - all_exp))
print(f"\n{sep}")
print("  6. MEAN ABSOLUTE ERROR (MAE)")
print(f"{sep}")
print(f"  Overall MAE : {overall_mae:.4f}")
print(f"  Meaning     : On average AI score differs from expected by {overall_mae:.2f} points")
print(f"\n  Per Scenario MAE:")
print(f"  {'Scenario':<20} {'MAE':>8} {'Mean AI':>10} {'Expected':>10} {'Bias':>8}")
print(f"  {'-'*58}")
for s in SCENARIOS:
    v   = groups[s]
    exp = EXPECTED_MID[s]
    mae = np.mean(np.abs(v - exp))
    bias = np.mean(v) - exp
    direction = "over-scores" if bias > 0 else "under-scores"
    print(f"  {s:<20} {mae:>8.4f} {np.mean(v):>10.2f} {exp:>10.1f} {bias:>+8.2f} ({direction})")

# ══════════════════════════════════════════════════════════════
# 7. ONE-WAY ANOVA + EFFECT SIZE
# ══════════════════════════════════════════════════════════════
f_stat, p_anova = f_oneway(*[groups[s] for s in SCENARIOS])
grand_mean  = np.mean(all_ai)
ss_between  = sum(len(groups[s])*(np.mean(groups[s])-grand_mean)**2 for s in SCENARIOS)
ss_within   = sum(np.sum((groups[s]-np.mean(groups[s]))**2) for s in SCENARIOS)
eta2        = ss_between / (ss_between + ss_within)
cohens_f    = np.sqrt(eta2 / (1 - eta2))
effect      = "Large" if cohens_f>=0.40 else "Medium" if cohens_f>=0.25 else "Small"

print(f"\n{sep}")
print("  7. ONE-WAY ANOVA")
print(f"{sep}")
print(f"  H0: All 5 scenario means are equal")
print(f"  H1: At least one scenario mean differs")
print(f"  F-statistic    : {f_stat:.4f}")
print(f"  p-value        : {p_anova:.8f}")
print(f"  Decision       : {'REJECT H0 — AI discriminates quality levels' if p_anova<0.05 else 'FAIL TO REJECT H0'}")
print(f"  Eta-squared    : {eta2:.4f} ({round(eta2*100,1)}% variance explained by answer quality)")
print(f"  Cohen's f      : {cohens_f:.4f} → {effect} effect")

print(f"\n  Pairwise t-tests (Bonferroni corrected):")
print(f"  {'Pair':<42} {'p-value':>10} {'Sig?':>8}")
print(f"  {'-'*62}")
n_pairs = len(list(combinations(SCENARIOS,2)))
for s1,s2 in combinations(SCENARIOS,2):
    _,p = stats.ttest_ind(groups[s1],groups[s2])
    p_c = min(p*n_pairs,1.0)
    sig = "Yes" if p_c<0.05 else "No"
    print(f"  {s1+' vs '+s2:<42} {p_c:>10.6f} {sig:>8}")

# ══════════════════════════════════════════════════════════════
# 8. BLAND-ALTMAN ANALYSIS
# ══════════════════════════════════════════════════════════════
differences = all_ai - all_exp
averages    = (all_ai + all_exp) / 2
mean_diff   = np.mean(differences)
std_diff    = np.std(differences)
loa_upper   = mean_diff + 1.96 * std_diff
loa_lower   = mean_diff - 1.96 * std_diff

# print(f"\n{sep}")
# print("  8. BLAND-ALTMAN ANALYSIS")
# print(f"{sep}")
# print(f"  Mean Difference (Bias) : {mean_diff:+.4f}")
# print(f"  Std of Differences     : {std_diff:.4f}")
# print(f"  Upper Limit of Agreement (LoA) : {loa_upper:+.4f}")
# print(f"  Lower Limit of Agreement (LoA) : {loa_lower:+.4f}")
# bias_dir = "over-scores" if mean_diff > 0 else "under-scores"
# print(f"  Interpretation : AI {bias_dir} by {abs(mean_diff):.2f} points on average")
# print(f"  95% of differences fall between {loa_lower:.2f} and {loa_upper:.2f}")

# ══════════════════════════════════════════════════════════════
# 9. SCORE CONSISTENCY (Std within same scenario)
# ══════════════════════════════════════════════════════════════
print(f"\n{sep}")
print("  9. SCORE CONSISTENCY (Within-Scenario Std Dev)")
print(f"{sep}")
print(f"  Lower std = more consistent scoring within same quality level")
print(f"  {'Scenario':<20} {'Std Dev':>10} {'Consistency':>14}")
print(f"  {'-'*46}")
for s in SCENARIOS:
    std = np.std(groups[s])
    consistency = "High" if std<1.0 else "Medium" if std<1.5 else "Low"
    print(f"  {s:<20} {std:>10.4f} {consistency:>14}")

# ══════════════════════════════════════════════════════════════
# SUMMARY TABLE
# ══════════════════════════════════════════════════════════════
print(f"\n{sep}")
print("  COMPLETE METRICS SUMMARY")
print(f"{sep}")
print(f"  {'Metric':<35} {'Value':>10} {'Interpretation'}")
print(f"  {'-'*70}")
print(f"  {'Spearman Correlation':<35} {spearman_r:>10.4f}  {interp} rank agreement")
print(f"  {'Pearson Correlation':<35} {pearson_r:>10.4f}  {round(pearson_r**2*100,1)}% variance explained")
print(f"  {'Quadratic Weighted Kappa':<35} {qwk:>10.4f}  {kappa_interp} grade band agreement")
print(f"  {'Precision (Pass/Fail)':<35} {precision:>10.4f}  AI pass prediction accuracy")
print(f"  {'Recall (Pass/Fail)':<35} {recall:>10.4f}  AI pass detection rate")
print(f"  {'F1 Score':<35} {f1:>10.4f}  Overall classification balance")
print(f"  {'Classification Accuracy':<35} {accuracy:>10.4f}  Correct grade band assignment")
print(f"  {'Overall MAE':<35} {overall_mae:>10.4f}  Avg score error in points")
print(f"  {'ANOVA F-statistic':<35} {f_stat:>10.4f}  Score discrimination power")
print(f"  {'Eta-squared':<35} {eta2:>10.4f}  {round(eta2*100,1)}% variance by quality")
print(f"  {'Cohen f':<35} {cohens_f:>10.4f}  {effect} effect size")
print(f"  {'Bland-Altman Bias':<35} {mean_diff:>+10.4f}  Systematic over/under scoring")
print(f"{sep}")

# ══════════════════════════════════════════════════════════════
# CHARTS
# ══════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(20, 16))
fig.patch.set_facecolor("#F8F9FC")
gs = GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

# Chart 1: Box Plot
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor("white")
bp = ax1.boxplot([groups[s] for s in SCENARIOS], patch_artist=True,
                 medianprops=dict(color="white", linewidth=2.5), widths=0.5)
for patch, s in zip(bp["boxes"], SCENARIOS):
    patch.set_facecolor(COLORS[s]); patch.set_alpha(0.85)
for w in bp["whiskers"]: w.set(color="#94A3B8", linewidth=1.5)
for c in bp["caps"]:     c.set(color="#94A3B8", linewidth=1.5)
ax1.set_xticklabels(["FC","AA","Avg","BA","FW"], fontsize=10)
ax1.set_ylabel("AI Score (/10)", fontsize=10)
ax1.set_title("Score Distribution\n(Box Plot)", fontsize=11, fontweight="bold", color="#1E3A5F")
ax1.set_ylim(0, 11)
ax1.grid(True, alpha=0.3, axis="y")

# Chart 2: Mean vs Expected
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor("white")
means = [np.mean(groups[s]) for s in SCENARIOS]
stds  = [np.std(groups[s])  for s in SCENARIOS]
x     = np.arange(len(SCENARIOS))
ax2.bar(x, means, yerr=stds, capsize=5, width=0.55,
        color=[COLORS[s] for s in SCENARIOS], alpha=0.85,
        error_kw=dict(ecolor="#374151", linewidth=1.5))
ax2.scatter(x, [EXPECTED_MID[s] for s in SCENARIOS], color="#1E3A5F", zorder=5, s=60, marker="D", label="Expected")
ax2.set_xticks(x); ax2.set_xticklabels(["FC","AA","Avg","BA","FW"], fontsize=10)
ax2.set_title("Mean AI Score vs Expected\n(with Std Dev)", fontsize=11, fontweight="bold", color="#1E3A5F")
ax2.set_ylim(0, 12); ax2.legend(fontsize=9); ax2.grid(True, alpha=0.3, axis="y")

# Chart 3: Confusion Matrix
ax3 = fig.add_subplot(gs[0, 2])
ax3.set_facecolor("white")
im = ax3.imshow(cm, interpolation="nearest", cmap="Blues")
ax3.set_xticks([0,1,2]); ax3.set_yticks([0,1,2])
ax3.set_xticklabels(["Incorrect","Partial","Correct"], fontsize=9)
ax3.set_yticklabels(["Incorrect","Partial","Correct"], fontsize=9)
ax3.set_xlabel("AI Prediction", fontsize=10); ax3.set_ylabel("Expected", fontsize=10)
ax3.set_title(f"Confusion Matrix\n(Accuracy: {accuracy:.2%})", fontsize=11, fontweight="bold", color="#1E3A5F")
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax3.text(j, i, str(cm[i,j]), ha="center", va="center",
                 color="white" if cm[i,j] > cm.max()/2 else "black", fontsize=12, fontweight="bold")

# Chart 4: MAE per Scenario
ax4 = fig.add_subplot(gs[1, 0])
ax4.set_facecolor("white")
mae_vals = [np.mean(np.abs(groups[s] - EXPECTED_MID[s])) for s in SCENARIOS]
bars = ax4.bar(range(len(SCENARIOS)), mae_vals, color=[COLORS[s] for s in SCENARIOS], alpha=0.85, width=0.6)
ax4.set_xticks(range(len(SCENARIOS)))
ax4.set_xticklabels(["FC","AA","Avg","BA","FW"], fontsize=10)
ax4.set_ylabel("MAE (points)", fontsize=10)
ax4.set_title(f"MAE per Scenario\n(Overall MAE: {overall_mae:.3f})", fontsize=11, fontweight="bold", color="#1E3A5F")
ax4.grid(True, alpha=0.3, axis="y")
for bar, val in zip(bars, mae_vals):
    ax4.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.05, f"{val:.2f}",
             ha="center", fontsize=9, fontweight="bold")

# Chart 5: Bland-Altman
ax5 = fig.add_subplot(gs[1, 1])
ax5.set_facecolor("white")
colors_ba = [COLORS[s] for s in SCENARIOS for _ in groups[s]]
ax5.scatter(averages, differences, c=colors_ba, alpha=0.7, s=50, edgecolors="white", linewidth=0.5)
ax5.axhline(mean_diff,  color="#2D5BE3", linewidth=2, linestyle="-",  label=f"Mean diff: {mean_diff:+.2f}")
ax5.axhline(loa_upper,  color="#DC2626", linewidth=1.5, linestyle="--", label=f"+1.96 SD: {loa_upper:+.2f}")
ax5.axhline(loa_lower,  color="#DC2626", linewidth=1.5, linestyle="--", label=f"-1.96 SD: {loa_lower:+.2f}")
ax5.axhline(0, color="#94A3B8", linewidth=1, linestyle=":")
ax5.set_xlabel("Average of AI and Expected Score", fontsize=10)
ax5.set_ylabel("Difference (AI - Expected)", fontsize=10)
ax5.set_title("Bland-Altman Plot\n(Bias Analysis)", fontsize=11, fontweight="bold", color="#1E3A5F")
ax5.legend(fontsize=8); ax5.grid(True, alpha=0.3)

# Chart 6: Scatter AI vs Expected
ax6 = fig.add_subplot(gs[1, 2])
ax6.set_facecolor("white")
ax6.scatter(all_exp, all_ai, c=colors_ba, alpha=0.7, s=50, edgecolors="white", linewidth=0.5)
ax6.plot([0,10],[0,10], color="#94A3B8", linewidth=1.5, linestyle="--", label="Perfect agreement")
m, b = np.polyfit(all_exp, all_ai, 1)
x_line = np.linspace(0, 10, 100)
ax6.plot(x_line, m*x_line+b, color="#2D5BE3", linewidth=2, label=f"Trend (r={pearson_r:.3f})")
ax6.set_xlabel("Expected Score", fontsize=10)
ax6.set_ylabel("AI Score", fontsize=10)
ax6.set_title(f"AI vs Expected Score\n(Pearson r={pearson_r:.4f})", fontsize=11, fontweight="bold", color="#1E3A5F")
ax6.legend(fontsize=8); ax6.grid(True, alpha=0.3)
ax6.set_xlim(0,11); ax6.set_ylim(0,11)

# Chart 7: Precision / Recall / F1 bar
ax7 = fig.add_subplot(gs[2, 0])
ax7.set_facecolor("white")
metrics_vals = [precision, recall, f1, accuracy]
metrics_lbls = ["Precision","Recall","F1 Score","Accuracy"]
metric_colors = ["#2D5BE3","#16A34A","#7C3AED","#D97706"]
bars7 = ax7.bar(metrics_lbls, metrics_vals, color=metric_colors, alpha=0.85, width=0.5)
ax7.set_ylim(0, 1.2)
ax7.set_title("Classification Metrics\n(Pass/Fail)", fontsize=11, fontweight="bold", color="#1E3A5F")
ax7.grid(True, alpha=0.3, axis="y")
for bar, val in zip(bars7, metrics_vals):
    ax7.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.02, f"{val:.3f}",
             ha="center", fontsize=10, fontweight="bold")

# Chart 8: Consistency (Std per scenario)
ax8 = fig.add_subplot(gs[2, 1])
ax8.set_facecolor("white")
stds_per = [np.std(groups[s]) for s in SCENARIOS]
bars8 = ax8.bar(range(len(SCENARIOS)), stds_per, color=[COLORS[s] for s in SCENARIOS], alpha=0.85, width=0.6)
ax8.set_xticks(range(len(SCENARIOS)))
ax8.set_xticklabels(["FC","AA","Avg","BA","FW"], fontsize=10)
ax8.set_ylabel("Std Dev (points)", fontsize=10)
ax8.set_title("Score Consistency\n(Lower = More Consistent)", fontsize=11, fontweight="bold", color="#1E3A5F")
ax8.grid(True, alpha=0.3, axis="y")
for bar, val in zip(bars8, stds_per):
    ax8.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.02, f"{val:.2f}",
             ha="center", fontsize=9, fontweight="bold")

# Chart 9: Summary text panel
ax9 = fig.add_subplot(gs[2, 2])
ax9.set_facecolor("#EEF2FF")
ax9.set_xlim(0,10); ax9.set_ylim(0,10); ax9.axis("off")
ax9.text(5, 9.5, "Metrics Summary", ha="center", va="top", fontsize=12, fontweight="bold", color="#1E3A5F")
summary_rows = [
    ("Spearman r",    f"{spearman_r:.4f}",  "#16A34A"),
    ("Pearson r",     f"{pearson_r:.4f}",   "#16A34A"),
    ("QWK",           f"{qwk:.4f}",         "#16A34A"),
    ("F1 Score",      f"{f1:.4f}",          "#2D5BE3"),
    ("Accuracy",      f"{accuracy:.4f}",    "#2D5BE3"),
    ("Overall MAE",   f"{overall_mae:.4f}", "#D97706"),
    ("ANOVA F",       f"{f_stat:.2f}",      "#7C3AED"),
    ("Eta-squared",   f"{eta2:.4f}",        "#7C3AED"),
    ("Bland-Altman",  f"{mean_diff:+.4f}",  "#D97706"),
]
for i, (lbl, val, col) in enumerate(summary_rows):
    y = 8.6 - i * 0.9
    ax9.text(0.5, y, f"{lbl}:", ha="left", va="center", fontsize=9, color="#6B7280")
    ax9.text(9.5, y, val, ha="right", va="center", fontsize=9, color=col, fontweight="bold")
    ax9.axhline(y=y-0.35, xmin=0.04, xmax=0.96, color="#C7D4FA", linewidth=0.5)

plt.suptitle("EvalAI — Complete Evaluation Metrics Dashboard",
             fontsize=15, fontweight="bold", color="#1E3A5F", y=1.01)

plt.savefig("Hypothesis/full_evaluation_results.png", dpi=150, bbox_inches="tight", facecolor="#F8F9FC")
plt.close()
print(f"\n  Chart saved: Hypothesis/full_evaluation_results.png")
print(f"{sep}")
