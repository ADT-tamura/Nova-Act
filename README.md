# NovaAct デモ

Amazon Nova Actを使用してブラウザ操作を自動化するデモプロジェクト

## 前提条件

- Python 3.x
- AWS CLI
- AWS SSO設定済み
- nova-actライブラリ

## セットアップ

### 1. AWS SSOログイン

スクリプトを実行する前に、AWS SSOで認証する必要があります。

```bash
aws sso login --profile default
```

コマンドを実行すると、ブラウザが自動的に開くか、以下のようなメッセージが表示されます:

```
Attempting to automatically open the SSO authorization page in your default browser.
If the browser does not open or you wish to use a different device to authorize this request, open the following URL:

https://device.sso.us-east-1.amazonaws.com/

Then enter the code: XXXX-XXXX
```

**手順:**
1. 表示されたURLにブラウザでアクセス
2. 表示されたコードを入力
3. AWS認証情報でログイン
4. 認証を承認

### 2. 認証確認

```bash
aws sts get-caller-identity
```

正常に認証されていれば、AWSアカウント情報が表示されます。

### 3. スクリプト実行

```bash
python3 test_nova_search.py
```

## トラブルシューティング

### トークン有効期限切れエラー

```
IAM validation failed: Token has expired and refresh failed
```

このエラーが発生した場合は、再度 `aws sso login` を実行してください。

### プロファイル名の変更

デフォルト以外のプロファイルを使用する場合は、`test_nova_search.py` の以下の行を修正してください:

```python
boto_session_kwargs={"region_name": "us-east-1", "profile_name": "your-profile-name"}
```
```
/mnt/c/Users/tamura.hiromi/AppData/Local/Programs/Kiro/bin/kiro .
```