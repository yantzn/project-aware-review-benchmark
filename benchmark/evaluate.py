from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
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


def terms_match(value: object, spec: dict) -> bool:
    text = flatten_text(value)
    if not all(str(term).lower() in text for term in spec.get("required_terms", [])):
        return False
    for alternatives in spec.get("any_terms", []):
        if not any(str(term).lower() in text for term in alternatives):
            return False
    return True


def finding_matches(actual: dict, expected: dict) -> bool:
    if expected.get("category") and actual.get("category") != expected["category"]:
        return False
    if expected.get("file") and actual.get("file") != expected["file"]:
        return False
    return terms_match(actual, expected)


def reference_ok(actual: dict, terms: list[str]) -> bool:
    if not terms:
        return True
    text = flatten_text(actual)
    return all(term.lower() in text for term in terms)


def score(actual: dict, gold: dict) -> dict:
    findings = list(actual.get("findings", []))
    expected_findings = list(gold.get("expected_findings", []))
    human_checks = list(actual.get("human_checks", []))
    expected_human = list(gold.get("human_checks", []))
    excluded = list(actual.get("excluded_findings", []))

    used: set[int] = set()
    matched_pairs: list[tuple[dict, dict]] = []

    for expected in expected_findings:
        match_index = next(
            (
                index
                for index, finding in enumerate(findings)
                if index not in used and finding_matches(finding, expected)
            ),
            None,
        )
        if match_index is not None:
            used.add(match_index)
            matched_pairs.append((findings[match_index], expected))

    true_positive = len(matched_pairs)
    missed = len(expected_findings) - true_positive
    false_positive = len(findings) - true_positive

    human_matched = sum(
        1
        for expected in expected_human
        if any(terms_match(item, expected) for item in human_checks)
    )

    design_targets = [
        (actual_finding, expected)
        for actual_finding, expected in matched_pairs
        if expected.get("design_reference_terms")
    ]
    design_ref_ok = sum(
        1
        for actual_finding, expected in design_targets
        if reference_ok(actual_finding, expected.get("design_reference_terms", []))
    )

    rule_targets = [
        (actual_finding, expected)
        for actual_finding, expected in matched_pairs
        if expected.get("project_rule_reference_terms")
    ]
    rule_ref_ok = sum(
        1
        for actual_finding, expected in rule_targets
        if reference_ok(actual_finding, expected.get("project_rule_reference_terms", []))
    )

    must_not_report = list(gold.get("must_not_report", []))
    prohibited_reported = sum(
        1
        for item in must_not_report
        if any(terms_match(finding, item) for finding in findings)
    )
    correctly_excluded = sum(
        1
        for item in must_not_report
        if any(terms_match(excluded_item, item) for excluded_item in excluded)
    )

    correct_finding_wrongly_excluded = sum(
        1
        for expected in expected_findings
        if any(terms_match(excluded_item, expected) for excluded_item in excluded)
    )

    keys = [
        (finding.get("category"), finding.get("file"), finding.get("message"))
        for finding in findings
    ]
    duplicate_count = sum(count - 1 for count in Counter(keys).values() if count > 1)
    duplicate_rate = duplicate_count / len(findings) if findings else 0.0

    expected_total = len(expected_findings)
    precision = true_positive / len(findings) if findings else (1.0 if expected_total == 0 else 0.0)
    recall = true_positive / expected_total if expected_total else 1.0

    evidence_ok = sum(
        1
        for actual_finding, expected in matched_pairs
        if (
            reference_ok(actual_finding, expected.get("evidence_terms", []))
            if expected.get("evidence_terms")
            else bool(actual_finding.get("evidence") or actual_finding.get("rationale"))
        )
    )
    evidence_accuracy = evidence_ok / len(matched_pairs) if matched_pairs else (1.0 if not expected_findings else 0.0)

    result = {
        "正検出数": true_positive,
        "見逃し数": missed,
        "誤検出数": false_positive,
        "適合率": round(precision, 4),
        "再現率": round(recall, 4),
        "根拠整合率": round(evidence_accuracy, 4),
        "人間確認振り分け精度": (
            round(human_matched / len(expected_human), 4) if expected_human else 1.0
        ),
        "重複指摘率": round(duplicate_rate, 4),
        "反証による誤検出除外数": correctly_excluded,
        "正しい指摘の誤棄却数": correct_finding_wrongly_excluded,
        "反証後の誤検出率": round(false_positive / len(findings), 4) if findings else 0.0,
        "禁止指摘の残存数": prohibited_reported,
        "意見相違検出数": len(actual.get("conflicts", [])),
    }

    if design_targets:
        result["設計書参照精度"] = round(design_ref_ok / len(design_targets), 4)
    else:
        result["設計書参照精度"] = None

    if rule_targets:
        result["プロジェクトルール判定精度"] = round(rule_ref_ok / len(rule_targets), 4)
    else:
        result["プロジェクトルール判定精度"] = None

    coverage = actual.get("review_coverage", {})
    result["レビュー実施範囲"] = {
        "確認済み": coverage.get("reviewed", []),
        "未確認": coverage.get("not_reviewed", []),
        "不足情報": coverage.get("missing_context", []),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--result", required=True, type=Path)
    parser.add_argument("--gold-ref", default="origin/benchmark-gold")
    args = parser.parse_args()

    actual = json.loads(args.result.read_text(encoding="utf-8"))
    gold = load_gold(args.case, args.gold_ref)
    print(json.dumps(score(actual, gold), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
