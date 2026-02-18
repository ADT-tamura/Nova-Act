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
            
            # Atomic Commands: 各ステップを明確に分割
            # Step 1: 検索窓に'Amazon Nova'を入力して検索実行
            print("📍 Step 1: 検索窓に'Amazon Nova'を入力して検索しています...")
            step1 = nova.act("検索窓に『Amazon Nova』と入力してEnterキーを押してください")
            print(f"   結果: {step1}")
            
            # Step 2: 検索結果の一番上の記事を特定
            print("📍 Step 2: 一番上の記事を探しています...")
            step2 = nova.act("検索結果の一番上の記事を見つけてください")
            print(f"   結果: {step2}")
            
            # Step 3: 記事の内容を要約
            print("📍 Step 3: 記事の要約を作成しています...")
            result = nova.act("一番上の記事の内容を読んで、要約を教えてください")
            print(f"\n✅ 最終結果: {result}")
            
            input("\n⏸️  ブラウザを確認してください。終了するにはEnterキーを押してください...")
            return result

if __name__ == "__main__":
    try:
        google_search_task()
    except Exception as e:
        print(f"❌ エラーが発生しました: \n{e}")