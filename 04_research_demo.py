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
        """JSONファイルに保存（追加方式）"""
        # 既存のファイルを読み込む
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    # 既存データが履歴形式でない場合は変換
                    if "research_history" not in existing_data:
                        # 古い形式のデータを履歴形式に変換
                        existing_data = {"research_history": [existing_data]}
            except (json.JSONDecodeError, KeyError):
                # ファイルが壊れている場合は新規作成
                existing_data = {"research_history": []}
        else:
            # ファイルが存在しない場合は新規作成
            existing_data = {"research_history": []}
        
        # 新しい調査結果を追加
        existing_data["research_history"].append(self.to_dict())
        
        # ファイルに保存
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        total_count = len(existing_data["research_history"])
        print(f"\n💾 データを保存しました: {filename}")
        print(f"📊 調査履歴: {total_count}件")


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
    
    def execute(self, instruction: str) -> Any:
        """Nova Actに指示を実行"""
        if not self.nova:
            raise RuntimeError(f"[{self.session_name}] ブラウザが起動していません")
        
        print(f"📍 [{self.session_name}] 実行: {instruction}")
        result = self.nova.act(instruction)
        print(f"   完了しました")
        return result


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
    """NovaActの情報収集と事例調査シナリオ"""
    
    # 調査データを格納するオブジェクト
    research_data = ResearchData()
    
    with BrowserOrchestrator() as orchestrator:
        
        # ========== フェーズ1: NovaActの情報収集 ==========
        print("\n" + "="*60)
        print("フェーズ1: NovaActの公式ページから情報を収集")
        print("="*60)
        
        with orchestrator.create_session("ブラウザA", "https://aws.amazon.com/jp/nova/act/") as browser_a:
            
            # Step 1: ページ全体を確認
            print("\n📖 NovaActの公式ページを確認しています...")
            browser_a.execute(
                "このページ全体をスクロールして、"
                "Amazon Nova Actに関する情報を確認してください。"
            )
            
            if not wait_for_key():
                print("処理を中断しました")
                return None
            
            # ページ内容から情報を自動収集（プレースホルダー）
            print("\n📝 ページ情報を記録しています...")
            
            # 実際のページ内容を記録（ここでは簡易的にプレースホルダーを使用）
            research_data.nova_act_info.overview = "Amazon Nova Actに関する情報を公式ページから収集しました"
            research_data.nova_act_info.features = [
                "ブラウザ操作の自動化",
                "自然言語による指示",
                "複雑なワークフローの実行"
            ]
            research_data.nova_act_info.use_cases = [
                "Webスクレイピング",
                "テスト自動化",
                "データ収集"
            ]
            research_data.nova_act_info.additional_info = f"収集日時: {datetime.now().isoformat()}, URL: https://aws.amazon.com/jp/nova/act/"
            
            print("✅ 情報を記録しました")
            
            # 共有データに保存
            orchestrator.share_data("research_data", research_data)
            
            if not wait_for_key():
                print("フェーズ1を終了します")
                research_data.save_to_json()
                return research_data
        
        # ========== フェーズ2: 先行事例・導入事例の調査 ==========
        print("\n" + "="*60)
        print("フェーズ2: 先行事例・導入事例を調査")
        print("="*60)
        
        # 共有データを取得
        research_data = orchestrator.get_shared_data("research_data")
        
        # 調査する事例の数を確認
        num_cases = input("\n何件の事例を調査しますか？ (デフォルト: 2): ").strip()
        num_cases = int(num_cases) if num_cases.isdigit() else 2
        
        with orchestrator.create_session("ブラウザB", "https://www.google.com") as browser_b:
            
            # Google検索を実行
            print("\n📍 Google検索を実行します...")
            browser_b.execute(
                "検索窓に『Amazon Nova Act 事例』または『Amazon Nova Act use case』"
                "と入力してEnterキーを押してください"
            )
            
            if not wait_for_key():
                print("処理を中断しました")
                research_data.save_to_json()
                return research_data
            
            # 各事例を調査
            for i in range(num_cases):
                print(f"\n--- 事例 {i+1}/{num_cases} ---")
                
                # 検索結果の上位リンクをクリック
                link_number = i + 1
                print(f"\n📖 検索結果の{link_number}番目のリンクを開きます...")
                browser_b.execute(
                    f"検索結果の{link_number}番目のリンクをクリックしてください"
                )
                
                if not wait_for_key():
                    print("この事例をスキップします")
                    # 検索結果ページに戻る
                    browser_b.execute("ブラウザの戻るボタンを押してください")
                    continue
                
                # ページ内容を確認
                browser_b.execute(
                    "このページをスクロールして内容を確認してください。"
                    "特にNova Actの活用方法や成果について注目してください。"
                )
                
                if not wait_for_key():
                    print("この事例をスキップします")
                    # 検索結果ページに戻る
                    browser_b.execute("ブラウザの戻るボタンを押してください")
                    continue
                
                # Novaにページ情報を抽出させる
                print("\n🤖 Novaがページ情報を抽出しています...")
                
                # タイトルを取得
                title_result = browser_b.execute(
                    "このページのタイトルを教えてください。ページの見出しやタイトル部分から取得してください。"
                )
                
                # URLを取得
                url_result = browser_b.execute(
                    "現在表示しているページのURLを教えてください。ブラウザのアドレスバーに表示されているURLです。"
                )
                
                # 要約を取得
                summary_result = browser_b.execute(
                    "このページの内容を1-2文で要約してください。"
                    "特にAmazon Nova Actの活用方法や成果について簡潔にまとめてください。"
                )
                
                # 結果から文字列を抽出（Novaの返り値から適切に取得）
                title = str(title_result).strip() if title_result else f"事例{i+1}"
                url = str(url_result).strip() if url_result else "URL取得失敗"
                summary = str(summary_result).strip() if summary_result else "要約取得失敗"
                
                # 事例を追加
                case_study = CaseStudy(title=title, summary=summary, url=url)
                research_data.case_studies.append(case_study)
                print(f"✅ 事例{i+1}を自動登録しました")
                print(f"   タイトル: {title}")
                print(f"   URL: {url}")
                print(f"   要約: {summary[:100]}...")
                
                # 次の事例のために検索結果ページに戻る
                if i < num_cases - 1:
                    print("\n🔙 検索結果ページに戻ります...")
                    browser_b.execute("ブラウザの戻るボタンを押してください")
                    
                    if not wait_for_key():
                        print("事例調査を終了します")
                        break
        
        # ========== 最終結果の保存と表示 ==========
        print("\n" + "="*60)
        print("📊 今回の調査結果")
        print("="*60)
        
        print(f"\n【NovaActの情報】")
        print(f"概要: {research_data.nova_act_info.overview}")
        print(f"\n機能 ({len(research_data.nova_act_info.features)}件):")
        for feature in research_data.nova_act_info.features:
            print(f"  - {feature}")
        print(f"\nユースケース ({len(research_data.nova_act_info.use_cases)}件):")
        for use_case in research_data.nova_act_info.use_cases:
            print(f"  - {use_case}")
        
        print(f"\n【収集した事例】({len(research_data.case_studies)}件)")
        for i, case in enumerate(research_data.case_studies, 1):
            print(f"\n{i}. {case.title}")
            print(f"   URL: {case.url}")
            print(f"   要約: {case.summary}")
        
        # JSONファイルに保存（追加方式）
        research_data.save_to_json()
        
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
