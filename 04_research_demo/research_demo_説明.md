# 04_research_demo の説明

## 概要
NovaActで公式ページから情報を収集し、Claudeで構造化して、Googleフォームに自動入力するデモです。

## ファイル構成

### 1. main.py（メインオーケストレーター）
全処理を自動的に順番に実行するメインファイル

- ステップ1: NovaActでページ内容を収集
- ステップ2: Claudeでデータを構造化
- ステップ3: Googleフォームに自動入力

### 2. collect_info.py
NovaActでページ内容を収集

- ページをスクロールして内容を確認
- Novaに詳しく説明させる
- 生テキストを`raw_summary.txt`に保存

### 3. structure_data.py
Amazon BedrockのClaudeでデータを構造化

- `raw_summary.txt`を読み込み
- Amazon BedrockのClaude 3.5 Sonnetに渡してJSON形式に構造化
- `nova_act_research.json`に保存

### 4. browser_manager.py
NovaActのブラウザ操作を管理

- `BrowserSession`: 個別のブラウザセッション管理
- `BrowserOrchestrator`: 複数のブラウザセッションの統括管理
- リトライ機能付きの実行メソッド（最大5回）

### 5. data_manager.py
JSONファイル操作とデータクラス

- `NovaActInfo`: NovaActの基本情報
- `CaseStudy`: 事例情報
- `ResearchData`: 調査データ全体の管理
- `save_to_json()`: JSONファイルへの上書き保存
- `load_from_json()`: JSONファイルからの読み込み

## 処理の流れ

### ステップ1: NovaActで情報収集
1. ブラウザAで https://aws.amazon.com/jp/nova/act/ を開く
2. ページ全体をスクロール
3. Novaに「ページに書かれている内容を詳しく説明してください」と指示
4. 返ってきた生テキストを`raw_summary.txt`に保存

### ステップ2: Amazon BedrockのClaudeで構造化
1. `raw_summary.txt`を読み込み
2. Amazon BedrockのClaude 3.5 Sonnetに以下の形式で構造化を依頼：
   ```json
   {
     "overview": "概要を3-5文で",
     "features": ["機能1", "機能2", "機能3"],
     "use_cases": ["ユースケース1", "ユースケース2", "ユースケース3"]
   }
   ```
3. Claudeの応答をパースして`ResearchData`オブジェクトに変換
4. `nova_act_research.json`に保存

### ステップ3: Googleフォームに入力
1. ブラウザBで https://forms.gle/RA4yez3AsU5LxbtQ6 を開く
2. フォーム全体をスクロール
3. 1つ目の入力欄に`features`をカンマ区切りで入力
4. 2つ目の入力欄に`use_cases`をカンマ区切りで入力
5. 送信ボタンを表示

## データ構造

### raw_summary.txt（中間ファイル）
NovaActが取得した生テキスト
```
Amazon Nova Actは...（Novaの説明がそのまま保存される）
```

### nova_act_research.json（最終出力）
```json
{
  "research_date": "2026-02-19T10:30:00",
  "nova_act_info": {
    "overview": "Amazon Nova Actは...",
    "features": ["機能1", "機能2", "機能3"],
    "use_cases": ["ユースケース1", "ユースケース2", "ユースケース3"],
    "additional_info": "収集日時: 2026-02-19T10:30:00, URL: https://aws.amazon.com/jp/nova/act/"
  },
  "case_studies": []
}
```

## 使い方

### 前提条件
- AWS認証情報が設定されている（NovaActとBedrock用）
- `aws sso login --profile default`でログイン済み

### 実行方法
```bash
cd 04_research_demo
python main.py
```

### 実行の流れ
1. **ステップ1開始**
   - NovaActがブラウザを起動
   - ページをスクロール
   - Enter/Escで続行/中断

2. **ステップ2開始**
   - Claudeがデータを構造化
   - 構造化されたデータを表示

3. **ステップ3開始**
   - NovaActがGoogleフォームを開く
   - フォームをスクロール
   - Enter/Escで続行/中断
   - 1つ目の入力欄に機能を入力
   - Enter/Escで続行/中断
   - 2つ目の入力欄にユースケースを入力
   - Enter/Escで続行/中断
   - 送信ボタンを表示

4. **完了**
   - すべての処理が完了

## 主要な機能

### 完全自動化
- 1つのコマンドで全処理を実行
- 人間の手動入力は一切不要
- 各ステップで確認ポイントあり

### 2段階処理
- NovaAct: ページ内容の取得（画像認識）
- Amazon Bedrock Claude: テキストの構造化（自然言語処理）
- 役割を明確に分離して確実性を向上
- すべてAWS認証で統一

### エラーハンドリング
- 各ステップで例外をキャッチ
- エラー発生時は詳細なトレースバックを表示
- いつでも中断可能（Escキー）

### リトライ機能
- NovaActの各操作は最大5回まで自動リトライ
- 一時的なエラーに対応

## 技術的なポイント

### NovaActの返り値問題の解決
NovaActの`execute()`は`ActResult`オブジェクトを返すため、直接テキストを取得できない問題がありました。

解決策：
1. NovaActには「詳しく説明してください」とだけ指示
2. 返り値を文字列化して生テキストとして保存
3. Claudeに渡して構造化

### モジュール分割
```python
# main.py
from collect_info import collect_page_content
from structure_data import structure_with_claude

# 各ステップを順番に実行
raw_text = collect_page_content()
research_data = structure_with_claude(raw_text)
```

### Claude APIの使用
```python
import boto3
import json

# Bedrockクライアントを作成
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

# リクエスト
request_body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": prompt}]
}

response = bedrock_runtime.invoke_model(
    modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
    body=json.dumps(request_body)
)

# レスポンスを解析
response_body = json.loads(response['body'].read())
response_text = response_body['content'][0]['text']
```

## トラブルシューティング

### NovaActが情報を取得できない
- AWS認証情報を確認
- `aws sso login --profile default`を実行

### Claudeが構造化に失敗する
- AWS認証情報を確認
- `aws sso login --profile default`を実行
- Bedrockでのモデルアクセス権限を確認
- `raw_summary.txt`の内容を確認

### フォーム入力が失敗する
- GoogleフォームのURLが正しいか確認
- 入力欄の数や順序が変わっていないか確認

## 拡張可能性

- 他のWebサイトの情報収集にも応用可能
- 異なるフォームへの自動入力
- 複数ページからの情報収集
- データベースへの保存機能追加
- 定期実行（cronなど）との組み合わせ
