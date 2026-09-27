# project-aware-review-benchmark

AIコードレビューを、コードだけではなく **要件・設計書・プロジェクト固有ルール・テスト結果** まで含めて評価するためのベンチマーク用リポジトリです。

対象は `yantzn/copilot-multi-review` のプロジェクト適合型レビューです。

## 目的

次の5方式を同じ検証ケースで比較します。

1. 単純レビュー
2. 単一AIによる構造化レビュー
3. 観点別レビュー担当
4. 観点別レビュー担当 + 反証レビュー
5. 観点別レビュー担当 + 反証レビュー + 総合整理 + 設計書 + プロジェクト固有ルール

「指摘数が多いほど良い」とは評価しません。特に、根拠のない指摘、設計書の誤参照、存在しないプロジェクトルールの捏造、AIだけでは決められない事項の過剰断定を重視します。

## 判定指標

- 正検出数
- 見逃し数
- 誤検出数
- 根拠整合率
- 設計書参照精度
- プロジェクトルール判定精度
- 人間確認振り分け精度
- 重複指摘率
- 反証による誤検出除外数
- 正しい指摘の誤棄却数
- 反証後の誤検出率
- 意見相違検出数
- レビュー実施範囲

## Gold Dataの分離

`main` と各 `case-XX` ブランチには期待答えを置きません。

期待結果は **`benchmark-gold` ブランチだけ** に置きます。レビュー対象側から期待答えが見えてベンチマークが汚染されるのを避けるためです。

## 構成

```text
src/                         正常系の基準実装
tests/                       基準テスト
requirements/                要件
design/                      Excel設計書と設計索引
project-rules/               プロジェクト固有ルール
tools/                       Excel解析・関連設計情報抽出
benchmark/
  cases.yaml                 検証ケース一覧（答えは含めない）
  result-template.json       評価入力フォーマット
  evaluate.py                評価スクリプト
```

## Excel設計書

`design/system-design.xlsx` は実際の `.xlsx` ファイルです。

`tools/parse_excel.py` で、ファイル名・シート名・セル座標を保持したJSONへ変換できます。

```bash
python tools/parse_excel.py design/system-design.xlsx > design-context.json
```

## ベンチマークケース

各ケースは `case-01` から `case-12` の専用ブランチとDraft PRで用意します。期待するレビュー結果はPR本文には書きません。

## 評価

レビュー結果を `benchmark/result-template.json` に合わせて保存し、次を実行します。

```bash
python benchmark/evaluate.py --case case-05 --result result.json
```

評価スクリプトは既定で `origin/benchmark-gold` の期待結果を `git show` で読み込みます。ローカルブランチを使う場合は `--gold-ref benchmark-gold` を指定します。

## セットアップ

Python 3.11以上を想定しています。

```bash
python -m pip install -e .[dev]
python -m pytest
```


## 実行手順

詳細な実行・採点手順は `benchmark/runbook.md` を参照してください。
