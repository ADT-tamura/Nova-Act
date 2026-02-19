# Nova ActとWorkflowをインポート
from nova_act import NovaAct, Workflow
import os
import sys
import termios
import tty
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime

# AWSリージョンを設定
os.environ["AWS_REGION"] = "us-east-1"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


def wait_for_key() -> bool:
    """
    Enterキーで続行(True)、Escキーで停止(False)を返す
    """
    print("\n⏸️  Enterキーで続行、Escキーで停止...")
    
    # 端末の設定を保存
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    try:
        # raw modeに設定（キー入力を即座に取得）
        tty.setraw(fd)
        key = sys.stdin.read(1)
        
        # Enterキー（\r または \n）
        if key in ['\r', '\n']:
            print("✅ 続行します")
            return True
        # Escキー（\x1b）
        elif key == '\x1b':
            print("⛔ 停止しました")
            return False
        else:
            # その他のキーは無視して再度待機
            print(f"❌ 無効なキーです。Enterキーで続行、Escキーで停止してください")
            return wait_for_key()
    finally:
        # 端末設定を復元
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


@dataclass
class NovaActInfo:
    """NovaActの基本情報を格納するデータクラス"""
    overview: str = ""
    features: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    additional_info: str = ""


@dataclass
class CaseStudy:
    """事例情報を格納するデータクラス"""
    title: str
    summary: str
    url: str
    collected_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ResearchData:
    """調査データ全体を管理するデータクラス"""
    nova_act_info: NovaActInfo = field(default_factory=NovaActInfo)
    case_studies: List[CaseStudy] = field(default_factory=list)
    research_date: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return {
            "research_date": self.research_date,
            "nova_act_info": asdict(self.nova_act_info),
            "case_studies": [asdict(cs) for cs in self.case_studies]
        }
    
    def save_to_json(self, filename: str = "nova_act_research.json"):
        """JSONファイルに保存（上書き方式）"""
        # ファイルに保存（上書き）
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 データを保存しました: {filename}")


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
                
                # Nova Actを実行
                result = self.nova.act(instruction)
                
                # 成功した場合
                if result is not None or not verify_change:
                    if retry_count > 0:
                        print(f"   ✅ リトライ成功しました")
                    else:
                        print(f"   完了しました")
                    return result
                
                # 結果がNoneで検証が必要な場合
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
        
        # 最大リトライ回数に達した場合
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


def research_scenario():
    """NovaActの情報収集とフォーム入力シナリオ"""
    
    research_data = ResearchData()
    
    with BrowserOrchestrator() as orchestrator:
        
        # ========== フェーズ1: 情報収集 ==========
        print("\n" + "="*60)
        print("フェーズ1: NovaActの情報を収集")
        print("="*60)
        
        with orchestrator.create_session("ブラウザA", "https://aws.amazon.com/jp/nova/act/") as browser_a:
            
            browser_a.execute("このページ全体をスクロールして、Amazon Nova Actに関する情報を確認してください。")
            
            if not wait_for_key():
                return None
            
            # 機能を取得
            features_result = browser_a.execute(
                "このページからAmazon Nova Actの主な機能を3つ挙げてください。カンマ区切りで回答してください。"
            )
            if features_result:
                research_data.nova_act_info.features = [f.strip() for f in str(features_result).strip().split(',') if f.strip()]
            
            # ユースケースを取得
            use_cases_result = browser_a.execute(
                "このページからAmazon Nova Actの主なユースケースを3つ挙げてください。カンマ区切りで回答してください。"
            )
            if use_cases_result:
                research_data.nova_act_info.use_cases = [u.strip() for u in str(use_cases_result).strip().split(',') if u.strip()]
            
            research_data.nova_act_info.additional_info = f"収集日時: {datetime.now().isoformat()}"
            
            print("✅ 情報を記録しました")
            
            # JSONファイルに保存
            research_data.save_to_json()
            
            orchestrator.share_data("research_data", research_data)
            
            if not wait_for_key():
                return research_data
        
        # ========== フェーズ2: フォーム入力 ==========
        print("\n" + "="*60)
        print("フェーズ2: Googleフォームに入力")
        print("="*60)
        
        research_data = orchestrator.get_shared_data("research_data")
        
        with orchestrator.create_session("ブラウザB", "https://forms.gle/RA4yez3AsU5LxbtQ6") as browser_b:
            
            browser_b.execute("このページ全体をゆっくりスクロールして、すべての質問項目を確認してください。")
            
            if not wait_for_key():
                return research_data
            
            nova_info = research_data.nova_act_info
            
            # 1つ目: 機能
            if nova_info.features:
                features_text = ", ".join(nova_info.features)
                print(f"\n📝 機能を入力: {features_text}")
                browser_b.execute("ページの一番上にある最初のテキスト入力欄をクリックしてください。")
                browser_b.execute(f"クリックした入力欄に次のテキストを入力してください: {features_text}")
                
                if not wait_for_key():
                    return research_data
            
            # 2つ目: ユースケース
            if nova_info.use_cases:
                use_cases_text = ", ".join(nova_info.use_cases)
                print(f"\n📝 ユースケースを入力: {use_cases_text}")
                browser_b.execute("ページを下にスクロールして、1つ目の入力欄の下にある次のテキスト入力欄を画面に表示してください。")
                browser_b.execute("今画面に表示されている、1つ目とは異なる2番目のテキスト入力欄をクリックしてください。")
                browser_b.execute(f"今クリックした2番目の入力欄に次のテキストを入力してください: {use_cases_text}")
                
                if not wait_for_key():
                    return research_data
            
            print("\n✅ 入力完了")
            browser_b.execute("ページの下部にある送信ボタンを探して表示してください。")
            
            if not wait_for_key():
                return research_data
        
        print("\n✅ 調査完了")
        return research_data


if __name__ == "__main__":
    try:
        result = research_scenario()
        if result:
            print("\n✅ 調査が正常に完了しました！")
            print(f"📄 結果は nova_act_research.json に保存されています")
    except Exception as e:
        print(f"\n❌ エラーが発生しました:\n{e}")
        import traceback
        traceback.print_exc()
