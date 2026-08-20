# Executive Brief: AI Match Quality & Data Integrity Audit

## Scope and Method

This analysis evaluates job application scoring data as of August 2026. Applications were joined to job postings and candidate profiles. The evaluated dataset contains **5,496 labeled applications** (excluding 504 pending applications without recruiter decisions).

Operational Ground Truth is defined as:
* **Positive Outcome:** Recruiter decision of `interviewed` or `hired`.
* **Negative Outcome:** Recruiter decision of `rejected`.

---

## Executive Summary

Across the evaluated population, the **Rule-based Scorer outperforms the LLM Scorer in overall accuracy (65.0% vs. 62.0%)** at the baseline 0.5 decision threshold:
* **LLM Scorer (Recall-Oriented):** Captures 90.4% of positive outcomes but yields low specificity (30.9%), causing 1,811 false-positive predictions. It acts as a broad top-of-funnel filter.
* **Rule-Based Scorer (Precision-Oriented):** Delivers balanced accuracy (65.0% recall, 65.3% specificity), but contains a severe rule collapse bug in the Healthcare job family.

---

## System Performance Comparison

| Evaluation Metric | Rule-Based System | LLM-Based System | Strategic Implication |
| :--- | :---: | :---: | :--- |
| **Overall Accuracy** | **65.03%** | **62.05%** | Rule engine yields 2.98% higher accuracy overall. |
| **Balanced Accuracy** | **65.04%** | **60.66%** | Rule system maintains uniform error rates across classes. |
| **Recall (Sensitivity)** | **64.74%** | **90.44%** | LLM minimizes missed candidates (only 275 false negatives). |
| **Specificity** | **65.34%** | **30.88%** | LLM requires threshold recalibration to reduce recruiter noise. |
| **Matthews Corr. (MCC)** | **0.301** | **0.268** | Rule predictions show stronger correlation with recruiter actions. |

---

## Data & Model Integrity Findings

### 1. Healthcare Rule Engine Collapse
The rule-based engine assigned zero positive predictions (0.0%) to all 1,239 Healthcare applications (mean score: 0.142), despite a 50.8% positive recruiter ground-truth rate (~630 positive outcomes).
* **Impact:** Healthcare applicants are systematically disqualified by the rule scorer.
* **Action:** Inspect Healthcare feature extraction and rule weights in the engine pipeline.

### 2. Synthetic Generator Inversions
* **Experience vs. Seniority:** Junior roles average **8.78 years** of experience, while Senior roles average **8.45 years**.
* **Job Family Preference Mismatch:** **79.2%** of applications were submitted for job families outside the candidate's preferred family.

### 3. LLM Profile Completeness Vulnerability
A negative correlation ($r = -0.151$) exists between profile completeness and normalized LLM score. Sparse candidate profiles trigger erratic LLM scoring, pointing to prompt formatting issues on missing fields.

---

## Recommendations

1. **Engineering:** Migrate PostgreSQL `rule_score` column precision to prevent rounding discrepancies between SQL queries and CSV analysis. Fix Healthcare rule scoring logic.
2. **Product:** Expose dynamic classification threshold controls in the dashboard UI.
3. **Data Science:** Recalibrate decision thresholds independently for LLM and rule-based models.

---

## Historical Reference Statistics

For exact replication and source CSV auditing, the original reference statistics tables are preserved below:

### Dataset Behavior

| Measure | Result |
| --- | ---: |
| Total applications | 6,000 |
| Labeled applications | 5,496 |
| Pending applications excluded | 504 (8.4%) |
| Positive outcomes | 2,876 (52.3%) |
| Rejected outcomes | 2,620 (47.7%) |
| Hired outcomes | 1,597 |
| Interviewed outcomes | 1,279 |

### Score Distributions

| Statistic | Rule score | LLM score (normalized) |
| --- | ---: | ---: |
| Mean | 0.475 | 0.643 |
| Standard deviation | 0.242 | 0.179 |
| Minimum | 0.000 | 0.000 |
| 25th percentile | 0.263 | 0.530 |
| Median | 0.502 | 0.650 |
| 75th percentile | 0.643 | 0.760 |
| Maximum | 1.000 | 1.000 |

### Rule-based vs. LLM-based Performance Summary

| System | Accuracy | Correct | Incorrect | Precision | Recall | Specificity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rule-based | **65.03%** | 3,574 | 1,922 | 67.22% | 64.74% | 65.34% |
| LLM-based | **62.05%** | 3,410 | 2,086 | 58.95% | 90.44% | 30.88% |

### LLM Model-Version Comparison

| Version | Applications | Outcome rate | Rule accuracy | LLM accuracy | Mean rule | Mean LLM | Mean absolute delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| scorer-v1 | 2,945 | 51.6% | 64.3% | 63.3% | 0.473 | 0.608 | 0.192 |
| scorer-v2 | 2,551 | 53.2% | 65.8% | 60.6% | 0.477 | 0.685 | 0.230 |

### Job-Family Performance Breakdown

| Job family | N | Outcome rate | Rule accuracy | LLM accuracy | Mean rule | Mean LLM | Rule positive rate | LLM positive rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Healthcare | 1,239 | 50.8% | **49.2%** | 59.2% | **0.142** | 0.643 | **0.0%** | 81.0% |
| IT | 729 | 51.7% | 68.9% | 61.3% | 0.557 | 0.627 | 63.1% | 78.1% |
| Logistics | 1,851 | 52.0% | 70.0% | 62.8% | 0.570 | 0.645 | 63.0% | 80.7% |
| Manufacturing | 804 | 53.9% | 68.2% | 61.3% | 0.589 | 0.654 | 70.0% | 81.3% |
| Office & Admin | 873 | 54.3% | 71.0% | 65.9% | 0.572 | 0.646 | 66.6% | 79.3% |