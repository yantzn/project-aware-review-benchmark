from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import yaml


def load_gold(case_id: str, gold_ref: str) -> dict:
    path = f"expected/{case_id}.yaml"
    completed = subprocess.run(
        ["git", "show", f"{gold_ref}:{path}"],
        check=True,
        text=True,
        capture_output=True,
    )
    return yaml.safe_load(completed.stdout)


def flatten_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True).lower()


def matches(actual: dict, expected: dict) -> bool:
    if expected.get("category") and actual.get("category") != expected["category"]:
        return False
    if expected.get("file") and actual.get("file") != expected["file"]:
        return False
    text = flatten_text(actual)
    return all(str(term).lower() in text for term in expected.get("required_terms", []))


def score(actual: dict, gold: dict) -> dict:
    findings = list(actual.get("findings", []))
    expected_findings = list(gold.get("expected_findings", []))
    human_checks = list(actual.get("human_checks", []))
    expected_human = list(gold.get("human_checks", []))
    excluded = list(actual.get("excluded_findings", []))

    used: set[int] = set()
    true_positive = 0
    missed = 0

    for expected in expected_findings:
        found = None
        for index, finding in enumerate(findings):
            if index not in used and matches(finding, expected):
                found = index
                break
        if found is None:
            missed += 1
        else:
            used.add(found)
            true_positive += 1

    false_positive = len(findings) - len(used)

    human_matched = sum(
        1
        for expected in expected_human
        if any(
            all(term.lower() in flatten_text(item) for term in expected.get("required_terms", []))
            for item in human_checks
        )
    )

    must_not_report = list(gold.get("must_not_report", []))
    prohibited_reported = sum(
        1
        for item in must_not_report
        if any(
            all(term.lower() in flatten_text(finding) for term in item.get("required_terms", []))
            for finding in findings
        )
    )
    correctly_excluded = sum(
        1
        for item in must_not_report
        if any(
            all(term.lower() in flatten_text(ex) for term in item.get("required_terms", []))
            for ex in excluded
        )
    )

    expected_total = len(expected_findings)
    precision = true_positive / len(findings) if findings else (1.0 if expected_total == 0 else 0.0)
    recall = true_positive / expected_total if expected_total else 1.0

    return {
        "正検出数": true_positive,
        "見逃し数": missed,
        "誤検出数": false_positive,
        "適合率": round(precision, 4),
        "再現率": round(recall, 4),
        "人間確認振り分け": f"{human_matched}/{len(expected_human)}",
        "禁止指摘の残存数": prohibited_reported,
        "反証による期待除外数": correctly_excluded,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--result", required=True, type=Path)
    parser.add_argument("--gold-ref", default="benchmark-gold")
    args = parser.parse_args()

    actual = json.loads(args.result.read_text(encoding="utf-8"))
    gold = load_gold(args.case, args.gold_ref)
    print(json.dumps(score(actual, gold), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
