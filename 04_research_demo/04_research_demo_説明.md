# 04_research_demo.py の説明

## 概要
NovaActの公式ページから情報を収集し、さらに先行事例・導入事例を調査して、結果をJSONファイルに保存するデモです。

## シナリオの流れ

### フェーズ1: NovaActの情報収集
**ブラウザA**: https://aws.amazon.com/jp/nova/act/ にアクセス

1. **概要の取得**
   - Novaがページを読んで概要を説明
   - ユーザーが内容を確認して入力

2. **機能・特徴の取得**
   - Novaが主な機能を箇条書きで説明
   - ユーザーが各機能を入力（空行で終了）

3. **ユースケースの取得**
   - Novaがユースケースを説明
   - ユーザーが各ユースケースを入力（空行で終了）

### フェーズ2: 先行事例・導入事例の調査
**ブラウザB**: Google検索で事例を調査

1. **検索実行**
   - 「Amazon Nova Act 事例」で検索

2. **事例の収集**（デフォルト2件、変更可能）
   - 検索結果からURLを手動で選択・入力
   - Novaが各ページを開いて内容を確認
   - タイトルと要約を収集

3. **データ保存**
   - 全ての情報をJSONファイルに保存

## データ構造

### ResearchData
調査データ全体を管理
```python
{
  "research_date": "2026-02-17T10:30:00",
  "nova_act_info": {...},
  "case_studies": [...]
}
```

### NovaActInfo
NovaActの基本情報
```python
{
  "overview": "概要テキスト",
  "features": ["機能1", "機能2", ...],
  "use_cases": ["ユースケース1", "ユースケース2", ...],
  "additional_info": "追加情報"
}
```

### CaseStudy
個別の事例情報
```python
{
  "title": "事例のタイトル",
  "summary": "要約",
  "url": "https://...",
  "collected_at": "2026-02-17T10:35:00"
}
```

## 出力ファイル

### nova_act_research.json
```json
{
  "research_date": "2026-02-17T10:30:00.123456",
  "nova_act_info": {
    "overview": "Amazon Nova Actは...",
    "features": [
      "ブラウザ自動操作",
      "自然言語での指示"
    ],
    "use_cases": [
      "Webスクレイピング",
      "テスト自動化"
    ],
    "additional_info": ""
  },
  "case_studies": [
    {
      "title": "事例1のタイトル",
      "summary": "事例1の要約...",
      "url": "https://example.com/case1",
      "collected_at": "2026-02-17T10:35:00.123456"
    }
  ]
}
```

## 使い方

```bash
python3 04_research_demo.py
```

### 操作の流れ

1. **フェーズ1開始**
   - ブラウザAが公式ページを開く

2. **概要入力**
   - Novaの説明を聞く
   - 概要を入力
   - Enter/Escで続行/中断

3. **機能入力**
   - Novaの説明を聞く
   - 機能を1つずつ入力（空行で終了）
   - Enter/Escで続行/中断

4. **ユースケース入力**
   - Novaの説明を聞く
   - ユースケースを1つずつ入力（空行で終了）
   - Enter/Escで続行/中断

5. **フェーズ2開始**
   - 調査する事例数を入力（デフォルト: 2）
   - ブラウザBでGoogle検索

6. **事例収集**（各事例ごと）
   - 検索結果からURLを選んで入力
   - Enter/Escで続行/スキップ
   - タイトルを入力
   - 要約を入力
   - 次の事例へ

7. **結果表示と保存**
   - 収集した全データを表示
   - JSONファイルに自動保存

## 主要なクラス

### BrowserSession
個別のブラウザを管理
- ブラウザの起動・終了
- Nova Actへの指示実行

### BrowserOrchestrator
複数のブラウザを統括
- ブラウザセッションの作成
- データ共有機能

### ResearchData
調査データの管理
- データ構造の定義
- JSON保存機能

## 技術的なポイント

### データ共有
```python
# フェーズ1でデータを保存
orchestrator.share_data("research_data", research_data)

# フェーズ2でデータを取得
research_data = orchestrator.get_shared_data("research_data")
```

### 柔軟な入力
- 事例数を動的に変更可能
- 各ステップでスキップ可能
- Enter/Escキーで細かく制御

### エラーハンドリング
- 各フェーズで中断可能
- 中断時も収集済みデータを保存
- 例外発生時もトレースバック表示

## 拡張可能性

- 他のWebサイトの情報収集にも応用可能
- JSONデータを使った分析・レポート生成
- 複数の調査対象を並行処理
- データベースへの保存機能追加
