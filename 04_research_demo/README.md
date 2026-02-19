# Amazon Nova Act 情報収集 & フォーム入力システム

## 概要
NovaActで公式ページから情報を収集し、Amazon Nova Proで構造化して、Googleフォームに自動入力するシステムです。

## ファイル構成

### メインファイル
- **`main.py`** - 全体のオーケストレーター（これを実行）
  - 3つのステップを自動的に順番に実行
  - エラーハンドリングと進捗表示

### ステップ別ファイル
1. **`collect_info.py`** - NovaActでページ内容を収集
   - NovaActでページをスクロール
   - requestsとBeautifulSoupでHTMLを取得
   - テキストを抽出して`raw_summary.txt`に保存

2. **`structure_data.py`** - Amazon Nova Proでデータを構造化
   - `raw_summary.txt`を読み込み
   - Amazon Bedrock Nova Proに渡してJSON形式に構造化
   - `nova_act_research.json`に保存

3. **`form_input.py`** - Googleフォームに自動入力
   - `nova_act_research.json`を読み込み
   - フォームのHTML構造を事前取得
   - NovaActでフォームに自動入力

### サポートファイル
- **`browser_manager.py`** - NovaActのブラウザ操作管理
  - `BrowserSession`: 個別のブラウザセッション
  - `BrowserOrchestrator`: 複数セッションの統括管理
  - リトライ機能（最大5回）

- **`data_manager.py`** - データ構造とJSON操作
  - `NovaActInfo`: 基本情報（overview, features, use_cases）
  - `ResearchData`: 全体データ管理
  - JSON保存・読み込み機能

## 処理フロー

```
ステップ1: 情報収集
  ├─ NovaActでページをスクロール（視覚確認）
  ├─ requestsでHTMLを取得
  ├─ BeautifulSoupでテキスト抽出
  └─ raw_summary.txt に保存

ステップ2: データ構造化
  ├─ raw_summary.txt を読み込み
  ├─ Amazon Nova Proで構造化
  │   ├─ overview（概要）
  │   ├─ features（機能）
  │   └─ use_cases（ユースケース）
  └─ nova_act_research.json に保存

ステップ3: フォーム入力
  ├─ nova_act_research.json を読み込み
  ├─ NovaActでフォームを開く
  ├─ フォーム全体をスクロール
  ├─ 「NovaActの特徴」の質問に features を入力
  └─ 送信ボタンを表示
```

## 使い方

### 前提条件
```bash
# 必要なパッケージをインストール
pip install boto3 requests beautifulsoup4 nova-act

# AWS認証（NovaActとBedrock用）
aws sso login --profile default
```

### 実行方法

#### 全自動実行（推奨）
```bash
cd 04_research_demo
python main.py
```

#### 個別実行（デバッグ用）
```bash
# ステップ1のみ
python collect_info.py

# ステップ2のみ
python structure_data.py

# ステップ3のみ
python form_input.py
```

### 実行の流れ
1. **ステップ1開始**
   - NovaActがブラウザを起動
   - ページをスクロール
   - HTMLからテキストを抽出
   - Enter/Escで続行/中断

2. **ステップ2開始**
   - Nova Proがデータを構造化
   - 構造化されたデータを表示
   - JSONファイルに保存

3. **ステップ3開始**
   - Enterキーで開始
   - NovaActがGoogleフォームを開く
   - フォームをスクロール
   - 「NovaActの特徴」の質問に機能を入力
   - 送信ボタンを表示
   - Enter/Escで送信/スキップ

4. **完了**

## データ構造

### raw_summary.txt（中間ファイル）
```
Amazon Nova Actは...
（ページから抽出した生テキスト）
```

### nova_act_research.json（最終出力）
```json
{
  "research_date": "2026-02-19T12:00:00",
  "nova_act_info": {
    "overview": "Amazon Nova Actは...",
    "features": ["機能1", "機能2", "機能3"],
    "use_cases": ["ユースケース1", "ユースケース2", "ユースケース3"],
    "additional_info": "収集日時: 2026-02-19T12:00:00, URL: https://aws.amazon.com/jp/nova/act/"
  },
  "case_studies": []
}
```

## 技術的なポイント

### NovaActの返り値問題の解決
NovaActの`execute()`は`ActResult`オブジェクトを返し、実際の応答テキストが含まれていません。

**解決策**: 
- NovaActはページのスクロールのみを担当
- requestsとBeautifulSoupでHTMLを直接取得
- テキスト抽出はPythonで処理

### 2段階処理
1. **NovaAct**: ブラウザ操作と視覚的確認
2. **Nova Pro**: テキストの構造化と自然言語処理

役割を明確に分離することで、確実性を向上。

### Amazon Bedrock Nova Pro
- AWSのネイティブモデル
- 追加の申請不要（Claudeは申請必要）
- 日本語対応
- `converse` APIを使用

```python
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
response = bedrock_runtime.converse(
    modelId="us.amazon.nova-pro-v1:0",
    messages=[{"role": "user", "content": prompt}],
    inferenceConfig={"max_new_tokens": 1024, "temperature": 0.7}
)
```

### シンプルなプロンプト設計
NovaActに対して明確で簡潔な指示を出すことで、入力精度を向上。

```python
# 質問を特定して入力欄をクリック
browser_b.execute(
    "「NovaActの特徴」という質問の下にある「回答を入力」と書かれた入力欄をクリックしてください。"
)

# フォーカスされた入力欄にテキストを入力
browser_b.execute(
    f"フォーカスされている入力欄に次のテキストを入力してください: {features_text}"
)
```

## トラブルシューティング

### NovaActが情報を取得できない
```bash
# AWS認証を確認
aws sso login --profile default
aws sts get-caller-identity
```

### Nova Proが構造化に失敗する
- AWS認証情報を確認
- Bedrockでのモデルアクセス権限を確認
- `raw_summary.txt`の内容を確認（空でないか）

### フォーム入力が失敗する
- GoogleフォームのURLが正しいか確認
- 入力欄の数や順序が変わっていないか確認
- NovaActのブラウザが正しく起動しているか確認

### ステップ3が実行されない
- ステップ2が正常に完了しているか確認
- 「✅ ステップ2完了」メッセージが表示されているか確認
- Enterキーを押してステップ3を開始

## 拡張可能性

- 他のWebサイトの情報収集
- 異なるフォームへの自動入力
- 複数ページからの情報収集
- データベースへの保存
- 定期実行（cron）との組み合わせ
- Slackやメールでの通知機能

## ライセンス

このプロジェクトは教育目的のデモです。
