"""NovaActのブラウザ操作関連"""
from nova_act import NovaAct, Workflow
from typing import Dict, Optional, Any


class BrowserSession:
    """個別のブラウザセッションを管理するクラス"""
    
    def __init__(self, session_name: str, starting_page: str, workflow: Workflow, headless: bool = False):
        self.session_name = session_name
        self.starting_page = starting_page
        self.workflow = workflow
        self.headless = headless
        self.nova: Optional[NovaAct] = None
        self.session_data: Dict[str, Any] = {}
    
    def __enter__(self):
        """コンテキストマネージャー: ブラウザを起動"""
        print(f"\n🌐 [{self.session_name}] ブラウザを起動: {self.starting_page}")
        self.nova = NovaAct(
            starting_page=self.starting_page,
            workflow=self.workflow,
            headless=self.headless
        ).__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー: ブラウザを終了"""
        if self.nova:
            self.nova.__exit__(exc_type, exc_val, exc_tb)
        print(f"✅ [{self.session_name}] ブラウザを終了しました")
    
    def execute(self, instruction: str, max_retries: int = 5, verify_change: bool = False) -> Any:
        """Nova Actに指示を実行（リトライ機能付き）
        
        Args:
            instruction: 実行する指示
            max_retries: 最大リトライ回数（デフォルト: 5）
            verify_change: 画面変化の検証を行うか（デフォルト: False）
        """
        if not self.nova:
            raise RuntimeError(f"[{self.session_name}] ブラウザが起動していません")
        
        print(f"📍 [{self.session_name}] 実行: {instruction}")
        
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                if retry_count > 0:
                    print(f"   🔄 リトライ {retry_count}/{max_retries}")
                
                result = self.nova.act(instruction)
                
                if result is not None or not verify_change:
                    if retry_count > 0:
                        print(f"   ✅ リトライ成功しました")
                    else:
                        print(f"   完了しました")
                    return result
                
                print(f"   ⚠️ 実行結果が取得できませんでした")
                retry_count += 1
                
            except Exception as e:
                last_error = e
                print(f"   ❌ エラーが発生しました: {e}")
                retry_count += 1
                
                if retry_count >= max_retries:
                    error_msg = f"[{self.session_name}] {max_retries}回試行しましたが失敗しました"
                    print(f"   ❌ {error_msg}")
                    raise RuntimeError(error_msg) from last_error
        
        error_msg = f"[{self.session_name}] {max_retries}回試行しましたが、正常に完了しませんでした"
        print(f"   ❌ {error_msg}")
        raise RuntimeError(error_msg)


class BrowserOrchestrator:
    """複数のブラウザセッションを統括管理するクラス"""
    
    def __init__(self, workflow_name: str = "at-amzn-nova-act-demo", model_id: str = "nova-act-latest"):
        self.workflow_name = workflow_name
        self.model_id = model_id
        self.workflow: Optional[Workflow] = None
        self.shared_data: Dict[str, Any] = {}
    
    def __enter__(self):
        """Workflowを作成"""
        print("🚀 BrowserOrchestrator を起動します...")
        self.workflow = Workflow(
            boto_session_kwargs={"region_name": "us-east-1", "profile_name": "default"},
            workflow_definition_name=self.workflow_name,
            model_id=self.model_id,
        ).__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Workflowを終了"""
        if self.workflow:
            self.workflow.__exit__(exc_type, exc_val, exc_tb)
        print("\n✅ BrowserOrchestrator を終了しました")
    
    def create_session(self, session_name: str, starting_page: str, headless: bool = False) -> BrowserSession:
        """新しいブラウザセッションを作成"""
        if not self.workflow:
            raise RuntimeError("Workflowが起動していません")
        
        return BrowserSession(
            session_name=session_name,
            starting_page=starting_page,
            workflow=self.workflow,
            headless=headless
        )
    
    def share_data(self, key: str, value: Any):
        """ブラウザ間で共有するデータを保存"""
        self.shared_data[key] = value
        print(f"💾 共有データを保存: {key}")
    
    def get_shared_data(self, key: str) -> Optional[Any]:
        """共有データを取得"""
        return self.shared_data.get(key)
