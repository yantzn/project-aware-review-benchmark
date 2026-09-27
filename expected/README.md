# Benchmark Gold Data

このブランチには各検証ケースの期待結果だけを保持します。

通常のAIレビューでは、このブランチをレビュー文脈として渡さないでください。

- `expected_findings`: 最終的に残ることを期待する指摘
- `human_checks`: AIが断定せず人間へ戻すことを期待する事項
- `must_not_report`: 最終指摘として残してはいけない事項

評価時のみ `benchmark/evaluate.py` から参照します。
