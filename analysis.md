# Dataset and Model Analysis

## Scope and method

This analysis uses the CSV files in `Tables/` as of 2026-08-19. Applications were joined to jobs on `job_id` and candidates on `candidate_id`. The evaluated population contains applications with a non-null `recruiter_decision`; 504 pending applications are excluded.

Ground truth is the same operational definition used by the backend:

- Positive: `interviewed` or `hired`
- Negative: `rejected`

Both systems are evaluated as binary classifiers using a threshold of 0.5. The rule score is already on a 0-1 scale; the LLM score is normalized from 0-100 to 0-1. Accuracy is the percentage of predictions matching this recruiter-derived ground truth.

## Dataset behavior

| Measure | Result |
| --- | ---: |
| Total applications | 6,000 |
| Labeled applications | 5,496 |
| Pending applications excluded | 504 (8.4%) |
| Positive outcomes | 2,876 (52.3%) |
| Rejected outcomes | 2,620 (47.7%) |
| Hired outcomes | 1,597 |
| Interviewed outcomes | 1,279 |

The evaluated data is nearly balanced between positive and negative outcomes, so accuracy has a meaningful baseline: an always-positive or always-negative classifier would be about 52.3% or 47.7% accurate respectively.

Two different disagreement measures are used below and should not be conflated:

- Large score-gap rate: absolute score difference greater than 0.4.
- Classification disagreement: one score is at least 0.5 and the other is below 0.5.

### Score distributions

| Statistic | Rule score | LLM score (normalized) |
| --- | ---: | ---: |
| Mean | 0.475 | 0.643 |
| Standard deviation | 0.242 | 0.179 |
| Minimum | 0.000 | 0.000 |
| 25th percentile | 0.263 | 0.530 |
| Median | 0.502 | 0.650 |
| 75th percentile | 0.643 | 0.760 |
| Maximum | 1.000 | 1.000 |

The LLM scores are shifted materially higher than rule scores. The mean absolute score difference is 0.210, with a median of 0.142 and a maximum of 0.863. The score correlation is moderate rather than strong: 0.439. Correlation with ground truth is 0.310 for the rule score and 0.386 for the LLM score.

## Rule-based versus LLM-based performance

| System | Accuracy | Correct | Incorrect | Precision | Recall | Specificity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rule-based | **65.03%** | 3,574 | 1,922 | 67.22% | 64.74% | 65.34% |
| LLM-based | **62.05%** | 3,410 | 2,086 | 58.95% | 90.44% | 30.88% |

Balanced accuracy is 65.04% for the rule system and 60.66% for the LLM. Matthews correlation coefficient is 0.301 and 0.268 respectively. Approximate 95% Wilson confidence intervals for accuracy are 63.8%-66.3% for the rule system and 60.8%-63.3% for the LLM.

The rule-based system is 2.98 percentage points more accurate overall. Its errors are more balanced: it produces 908 false positives and 1,014 false negatives. The LLM is much more sensitive to positive outcomes, producing 2,601 true positives and only 275 false negatives, but it also produces 1,811 false positives. This explains its high recall and low specificity. At this threshold, the LLM behaves more like a broad screening or recall-oriented system, while the rule system is the better balanced classifier.

The two systems make the same binary classification on 3,460 of 5,496 evaluated applications (63.0%). They disagree on 2,036 applications (37.0%). Separately, 1,024 applications (18.6%) have an absolute score gap greater than 0.4. Both measures are large enough to warrant review rather than treating the scores as interchangeable.

### LLM model-version comparison

| Version | Applications | Outcome rate | Rule accuracy | LLM accuracy | Mean rule | Mean LLM | Mean absolute delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| scorer-v1 | 2,945 | 51.6% | 64.3% | 63.3% | 0.473 | 0.608 | 0.192 |
| scorer-v2 | 2,551 | 53.2% | 65.8% | 60.6% | 0.477 | 0.685 | 0.230 |

LLM accuracy falls by 2.7 percentage points from `scorer-v1` to `scorer-v2`, while its mean score rises from 0.608 to 0.685 and its average divergence from the rule score increases. This is an association, not a controlled version experiment, because the versions may be exposed to different application mixes.

## Job-family bias inspection

The following table uses the job family on the job posting. Positive-prediction rate is the share of applications assigned a score of at least 0.5.

| Job family | N | Outcome rate | Rule accuracy | LLM accuracy | Mean rule | Mean LLM | Rule positive rate | LLM positive rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Healthcare | 1,239 | 50.8% | **49.2%** | 59.2% | **0.142** | 0.643 | **0.0%** | 81.0% |
| IT | 729 | 51.7% | 68.9% | 61.3% | 0.557 | 0.627 | 63.1% | 78.1% |
| Logistics | 1,851 | 52.0% | 70.0% | 62.8% | 0.570 | 0.645 | 63.0% | 80.7% |
| Manufacturing | 804 | 53.9% | 68.2% | 61.3% | 0.589 | 0.654 | 70.0% | 81.3% |
| Office & Admin | 873 | 54.3% | 71.0% | 65.9% | 0.572 | 0.646 | 66.6% | 79.3% |

### Finding

There is clear systematic job-family dependence in model behavior, especially for Healthcare. The rule-based scorer assigns no Healthcare application a positive prediction and has a mean score of 0.142, despite a 50.8% positive ground-truth rate. Its Healthcare accuracy is therefore close to the negative-class baseline and 20.8 percentage points below its best family accuracy. This is strong evidence of a family-specific scoring or feature problem in the rule system, not evidence that Healthcare applicants are inherently less suitable.

The LLM does not show the same collapse, but it is also not uniform: its accuracy ranges from 59.2% in Healthcare to 65.9% in Office & Admin, and its positive-prediction rate ranges from 78.1% to 81.3%. Because the LLM has low specificity overall, its high positive rates should not be interpreted as calibrated hiring probabilities.

These are model-performance disparities by job family, not a definitive fairness finding about people. The data does not include protected characteristics, and the recruiter decision is itself an imperfect and potentially biased proxy for ground truth. Family sample sizes are also uneven, so these comparisons should be followed by confidence intervals and a controlled error analysis before changing production thresholds.

## Conclusions and next checks

1. Against the current recruiter-derived ground truth, the rule system is more accurate: **65.03% versus 62.05%** for the LLM.
2. At the evaluated threshold, the LLM has substantially higher recall (**90.44%**) but much lower specificity (**30.88%**), making it more appropriate for a recall-first workflow unless its threshold is recalibrated.
3. The Healthcare rule-score distribution is anomalous and should be investigated first. Check feature availability, family-specific normalization, and rule thresholds for Healthcare jobs.
4. Re-evaluate thresholds separately from accuracy. Report precision-recall trade-offs, calibration, and family-level false-positive and false-negative rates rather than relying on one global 0.5 threshold.
5. Treat recruiter decisions as a noisy label. A future audit should include independent review or outcome-based validation, and should stratify by country, seniority, model version, and job family together.

## Reproducibility and data-quality notes

The backend now exposes the metric definitions used here through `/api/overview/kpis`, including confusion matrices, balanced accuracy, MCC, and Wilson intervals. Re-run the repository validation script after changing the CSV inputs or database view. The dataset contains a clear rule-configuration artifact: every Healthcare application is labeled `low` by the rule scorer, so the Healthcare result should be treated as a configuration/data-generation defect until independently verified.