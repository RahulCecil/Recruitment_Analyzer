"""Recompute the report's core metrics from the source CSV files."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "Tables"


def read_csv(name: str) -> list[dict[str, str]]:
    with (TABLES / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def classifier_metrics(rows: list[dict[str, object]], score_key: str) -> dict[str, object]:
    counts = Counter()
    for row in rows:
        prediction = int(float(row[score_key]) >= 0.5)
        actual = int(row["outcome"])
        counts[(prediction, actual)] += 1

    tp = counts[(1, 1)]
    tn = counts[(0, 0)]
    fp = counts[(1, 0)]
    fn = counts[(0, 1)]
    total = tp + tn + fp + fn
    recall = ratio(tp, tp + fn)
    specificity = ratio(tn, tn + fp)
    denominator = ((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)) ** 0.5
    return {
        "total": total,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": ratio(tp + tn, total),
        "precision": ratio(tp, tp + fp),
        "recall": recall,
        "specificity": specificity,
        "balanced_accuracy": (recall + specificity) / 2,
        "mcc": (tp * tn - fp * fn) / denominator if denominator else 0.0,
    }


def main() -> None:
    applications = read_csv("applications.csv")
    candidate_rows = read_csv("candidates.csv")
    job_rows = read_csv("jobs.csv")
    candidates = {row["candidate_id"]: row for row in candidate_rows}
    jobs = {row["job_id"]: row for row in job_rows}

    assert len(applications) == len({row["application_id"] for row in applications})
    assert len(candidates) == len(candidate_rows)
    assert len(jobs) == len(job_rows)

    evaluated = []
    for application in applications:
        assert application["candidate_id"] in candidates
        assert application["job_id"] in jobs
        if not application["recruiter_decision"]:
            continue
        assert application["rule_score"] is not None
        assert application["llm_score"] is not None
        evaluated.append(
            {
                "outcome": int(
                    application["recruiter_decision"] in {"interviewed", "hired"}
                ),
                "rule_score": float(application["rule_score"]),
                "llm_score": float(application["llm_score"]) / 100,
                "job_family": jobs[application["job_id"]]["job_family"],
                "model_version": application["llm_model_version"],
            }
        )

    rule = classifier_metrics(evaluated, "rule_score")
    llm = classifier_metrics(evaluated, "llm_score")
    large_score_gaps = sum(
        abs(float(row["rule_score"]) - float(row["llm_score"])) > 0.4
        for row in evaluated
    )
    classification_disagreements = sum(
        (float(row["rule_score"]) >= 0.5) != (float(row["llm_score"]) >= 0.5)
        for row in evaluated
    )

    by_version = defaultdict(list)
    for row in evaluated:
        by_version[row["model_version"]].append(row)

    result = {
        "total_applications": len(applications),
        "evaluated_applications": len(evaluated),
        "pending_applications": len(applications) - len(evaluated),
        "rule": rule,
        "llm": llm,
        "large_score_gap_rate": ratio(large_score_gaps, len(evaluated)),
        "classification_disagreement_rate": ratio(
            classification_disagreements, len(evaluated)
        ),
        "versions": {
            version: {
                "applications": len(rows),
                "rule": classifier_metrics(rows, "rule_score"),
                "llm": classifier_metrics(rows, "llm_score"),
            }
            for version, rows in sorted(by_version.items())
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
