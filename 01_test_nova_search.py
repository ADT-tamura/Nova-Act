# Nova ActとWorkflowをインポート
from nova_act import NovaAct, Workflow
import os

# AWSリージョンを設定（us-east-1でNova Actを使用）
os.environ["AWS_REGION"] = "us-east-1"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

def google_search_task():
    # Workflowを作成（AWS認証を使用してNova Actを実行）
    with Workflow(
        boto_session_kwargs={"region_name": "us-east-1", "profile_name": "default"},  # プロファイル名を指定
        workflow_definition_name="at-amzn-nova-act-demo",  # 事前に作成したワークフロー定義名
        model_id="nova-act-latest",  # 使用するNova Actモデル
    ) as workflow:
        # NovaActでブラウザを起動
        with NovaAct(
            starting_page="https://www.google.com",  # 開始ページ
            workflow=workflow,  # 上記で作成したWorkflowを渡す
            headless=False  # ブラウザを表示（Trueにすると非表示）
        ) as nova:
            print("🚀 ブラウザを操作して Google 検索を実行します...")
            # AIにブラウザ操作を指示
            result = nova.act("検索窓に『Amazon Nova』と入力して検索し、一番上の記事の要約を教えて")
            print(f"\n✅ 実行結果: {result}")
            input("\n⏸️  ブラウザを確認してください。終了するにはEnterキーを押してください...")
            return result

if __name__ == "__main__":
    try:
        google_search_task()
    except Exception as e:
        print(f"❌ エラーが発生しました: \n{e}")