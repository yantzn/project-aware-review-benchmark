# ベンチマーク実行手順

## 1. 前提

- `yantzn/copilot-multi-review` のプロジェクト適合型レビュー版を利用する
- このリポジトリをローカルへcloneする
- `origin/benchmark-gold` を取得しておく
- Gold Dataはレビュー実行時のコンテキストへ渡さない

## 2. 1ケースの実行

例: case-05

```bash
git checkout case-05
```

レビューエンジン側から対象リポジトリを指定する。

```bash
ai-review review --repo <project-aware-review-benchmarkのローカルパス> --target base
```

標準経路では、対象リポジトリから以下を読み取り専用で収集する。

- `requirements/`
- `design/system-design.xlsx`
- `project-rules/`
- diff
- quality check結果

## 3. 評価用JSON

`copilot-multi-review` の保存結果では、Final Reviewerの構造化結果を使用する。

想定:

```text
reports/<project-id>/latest/agents/final.json
```

最終結果に次があることを確認する。

- `findings`
- `human_checks`
- `challenge_decisions`
- `excluded_findings`
- `review_coverage`

必要に応じて `benchmark/result-template.json` と同じ形へ変換する。

## 4. 採点

```bash
python benchmark/evaluate.py \
  --case case-05 \
  --result <final-review-result.json>
```

既定では `origin/benchmark-gold:expected/case-05.yaml` を参照する。

## 5. 比較方式

同じケースに対して最低限次を保存する。

```text
results/
└── case-05/
    ├── 方式A_単純レビュー.json
    ├── 方式B_単一構造化レビュー.json
    ├── 方式C_観点別レビュー.json
    ├── 方式D_観点別+反証.json
    └── 方式E_プロジェクト適合型.json
```

`results/` は実験成果物であり、検証開始前のGold Dataとは分離する。

## 6. 判定時の注意

単純な指摘件数では評価しない。

特に以下を見る。

- 誤検出が減ったか
- 正しい指摘を反証担当が消していないか
- Excel設計書の正しい箇所を根拠としているか
- プロジェクト固有ルールIDを正しく参照しているか
- 要件と設計が矛盾した際に人間確認へ戻せたか
- 問題のないcase-01 / case-12で不要な指摘を作っていないか
