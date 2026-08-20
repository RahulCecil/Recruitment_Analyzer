# Executive Brief: AI Match Quality & Data Integrity Audit

## Scope and Method

This analysis evaluates job application scoring data as of August 2026[cite: 5]. Applications were joined to job postings and candidate profiles[cite: 5]. The evaluated dataset contains **5,496 labeled applications** (excluding 504 pending applications without recruiter decisions)[cite: 5].

Operational Ground Truth is defined as:
* **Positive Outcome:** Recruiter decision of `interviewed` or `hired`[cite: 5].
* **Negative Outcome:** Recruiter decision of `rejected`[cite: 5].

---

## Executive Summary

Across the evaluated population, the **Rule-based Scorer outperforms the LLM Scorer in overall accuracy (65.0% vs. 62.0%)** at the baseline 0.5 decision threshold[cite: 5]:
* **LLM Scorer (Recall-Oriented):** Captures 90.4% of positive outcomes but yields low specificity (30.9%), causing 1,811 false-positive predictions[cite: 5]. It acts as a broad top-of-funnel filter[cite: 5].
* **Rule-Based Scorer (Precision-Oriented):** Delivers balanced accuracy (65.0% recall, 65.3% specificity)[cite: 5], but contains a severe rule collapse bug in the Healthcare job family[cite: 3, 5].

---

## System Performance Comparison

| Evaluation Metric | Rule-Based System | LLM-Based System | Strategic Implication |
| :--- | :---: | :---: | :--- |
| **Overall Accuracy** | **65.03%**[cite: 5] | **62.05%**[cite: 5] | Rule engine yields 2.98% higher accuracy overall[cite: 5]. |
| **Balanced Accuracy** | **65.04%**[cite: 5] | **60.66%**[cite: 5] | Rule system maintains uniform error rates across classes[cite: 5]. |
| **Recall (Sensitivity)** | **64.74%**[cite: 5] | **90.44%**[cite: 5] | LLM minimizes missed candidates (only 275 false negatives)[cite: 5]. |
| **Specificity** | **65.34%**[cite: 5] | **30.88%**[cite: 5] | LLM requires threshold recalibration to reduce recruiter noise[cite: 5]. |
| **Matthews Corr. (MCC)** | **0.301**[cite: 5] | **0.268**[cite: 5] | Rule predictions show stronger correlation with recruiter actions[cite: 5]. |

---

## Data & Model Integrity Findings

### 1. Healthcare Rule Engine Collapse
The rule-based engine assigned zero positive predictions (0.0%) to all 1,239 Healthcare applications (mean score: 0.142)[cite: 3, 5], despite a 50.8% positive recruiter ground-truth rate (~630 positive outcomes)[cite: 5].
* **Impact:** Healthcare applicants are systematically disqualified by the rule scorer[cite: 5].
* **Action:** Inspect Healthcare feature extraction and rule weights in the engine pipeline[cite: 5].

### 2. Synthetic Generator Inversions
* **Experience vs. Seniority:** Junior roles average **8.78 years** of experience, while Senior roles average **8.45 years**[cite: 3, 5].
* **Job Family Preference Mismatch:** **79.2%** of applications were submitted for job families outside the candidate's preferred family[cite: 3, 5].

### 3. LLM Profile Completeness Vulnerability
A negative correlation ($r = -0.151$) exists between profile completeness and normalized LLM score[cite: 3, 5]. Sparse candidate profiles trigger erratic LLM scoring, pointing to prompt formatting issues on missing fields[cite: 5].

---

## Recommendations

1. **Engineering:** Migrate PostgreSQL `rule_score` column precision to prevent rounding discrepancies between SQL queries and CSV analysis[cite: 5]. Fix Healthcare rule scoring logic[cite: 5].
2. **Product:** Expose dynamic classification threshold controls in the dashboard UI[cite: 5].
3. **Data Science:** Recalibrate decision thresholds independently for LLM and rule-based models[cite: 5].

---

## Historical Reference Statistics

For exact replication and source CSV auditing, the original reference statistics tables are preserved below[cite: 5]:

### Dataset Behavior

| Measure | Result |
| --- | ---: |
| Total applications | 6,000[cite: 5] |
| Labeled applications | 5,496[cite: 5] |
| Pending applications excluded | 504 (8.4%)[cite: 5] |
| Positive outcomes | 2,876 (52.3%)[cite: 5] |
| Rejected outcomes | 2,620 (47.7%)[cite: 5] |
| Hired outcomes | 1,597[cite: 5] |
| Interviewed outcomes | 1,279[cite: 5] |

### Score Distributions

| Statistic | Rule score | LLM score (normalized) |
| --- | ---: | ---: |
| Mean | 0.475[cite: 5] | 0.643[cite: 5] |
| Standard deviation | 0.242[cite: 5] | 0.179[cite: 5] |
| Minimum | 0.000[cite: 5] | 0.000[cite: 5] |
| 25th percentile | 0.263[cite: 5] | 0.530[cite: 5] |
| Median | 0.502[cite: 5] | 0.650[cite: 5] |
| 75th percentile | 0.643[cite: 5] | 0.760[cite: 5] |
| Maximum | 1.000[cite: 5] | 1.000[cite: 5] |

### Rule-based vs. LLM-based Performance Summary

| System | Accuracy | Correct | Incorrect | Precision | Recall | Specificity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rule-based | **65.03%**[cite: 5] | 3,574[cite: 5] | 1,922[cite: 5] | 67.22%[cite: 5] | 64.74%[cite: 5] | 65.34%[cite: 5] |
| LLM-based | **62.05%**[cite: 5] | 3,410[cite: 5] | 2,086[cite: 5] | 58.95%[cite: 5] | 90.44%[cite: 5] | 30.88%[cite: 5] |

### LLM Model-Version Comparison

| Version | Applications | Outcome rate | Rule accuracy | LLM accuracy | Mean rule | Mean LLM | Mean absolute delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| scorer-v1 | 2,945[cite: 5] | 51.6%[cite: 5] | 64.3%[cite: 5] | 63.3%[cite: 5] | 0.473[cite: 5] | 0.608[cite: 5] | 0.192[cite: 5] |
| scorer-v2 | 2,551[cite: 5] | 53.2%[cite: 5] | 65.8%[cite: 5] | 60.6%[cite: 5] | 0.477[cite: 5] | 0.685[cite: 5] | 0.230[cite: 5] |

### Job-Family Performance Breakdown

| Job family | N | Outcome rate | Rule accuracy | LLM accuracy | Mean rule | Mean LLM | Rule positive rate | LLM positive rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Healthcare | 1,239[cite: 5] | 50.8%[cite: 5] | **49.2%**[cite: 5] | 59.2%[cite: 5] | **0.142**[cite: 5] | 0.643[cite: 5] | **0.0%**[cite: 5] | 81.0%[cite: 5] |
| IT | 729[cite: 5] | 51.7%[cite: 5] | 68.9%[cite: 5] | 61.3%[cite: 5] | 0.557[cite: 5] | 0.627[cite: 5] | 63.1%[cite: 5] | 78.1%[cite: 5] |
| Logistics | 1,851[cite: 5] | 52.0%[cite: 5] | 70.0%[cite: 5] | 62.8%[cite: 5] | 0.570[cite: 5] | 0.645[cite: 5] | 63.0%[cite: 5] | 80.7%[cite: 5] |
| Manufacturing | 804[cite: 5] | 53.9%[cite: 5] | 68.2%[cite: 5] | 61.3%[cite: 5] | 0.589[cite: 5] | 0.654[cite: 5] | 70.0%[cite: 5] | 81.3%[cite: 5] |
| Office & Admin | 873[cite: 5] | 54.3%[cite: 5] | 71.0%[cite: 5] | 65.9%[cite: 5] | 0.572[cite: 5] | 0.646[cite: 5] | 66.6%[cite: 5] | 79.3%[cite: 5] |