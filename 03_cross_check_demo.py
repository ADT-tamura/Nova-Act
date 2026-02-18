# Nova ActとWorkflowをインポート
from nova_act import NovaAct, Workflow
import os
import sys
import termios
import tty
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
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
class SearchResult:
    """検索結果を格納するデータクラス"""
    query: str
    urls: List[str] = field(default_factory=list)
    summaries: Dict[str, str] = field(default_factory=dict)
    
    def add_url(self, url: str):
        """URLを追加"""
        if url and url not in self.urls:
            self.urls.append(url)
    
    def add_summary(self, url: str, summary: str):
        """URLに対する要約を追加"""
        self.summaries[url] = summary


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


def browser_a_collect_urls(orchestrator: BrowserOrchestrator, query: str) -> List[str]:
    """
    ブラウザAでGoogle検索を実行し、URLを収集する
    
    Args:
        orchestrator: BrowserOrchestrator インスタンス
        query: 検索クエリ
    
    Returns:
        収集したURLのリスト
    """
    print("\n" + "="*60)
    print("フェーズ1: ブラウザAでURL収集")
    print("="*60)
    
    urls = []
    
    with orchestrator.create_session("ブラウザA", "https://www.google.com") as browser_a:
        
        # Step 1: 検索実行
        print(f"📍 Step 1: 検索を実行します...")
        browser_a.execute(f"検索窓に『{query}』と入力してEnterキーを押してください")
        
        # 検索結果の読み込みを待つ
        print(f"\n⏳ 検索結果の読み込みを待っています...")
        browser_a.execute("検索結果が表示されるまで待ってください。表示されたら『検索結果が表示されました』と返答してください")
        
        # Step 2: 検索結果のURLを1つずつ取得
        print(f"\n📍 Step 2: 検索結果のURLを取得します...")
        
        urls = []  # URL格納用リスト
        for i in range(1, 4):  # 上位3件
            try:
                print(f"\n  {i}件目のURLを取得中...")
                result = browser_a.execute(
                    f"検索結果の{i}番目のリンクをクリックせずに、そのURLだけを取得して教えてください。"
                    f"回答は『URL: https://...』の形式で、URLのみを返してください。"
                )
                print(f"  Novaの返答: {result}")
                
                # ActResultから何らかの形でURLを抽出する試み
                result_str = str(result)
                
                # 返答文字列からURLを抽出（正規表現を使用）
                url_pattern = r'https?://[^\s\)"\',<>]+'
                found_urls = re.findall(url_pattern, result_str)
                
                if found_urls:
                    url = found_urls[0]  # 最初に見つかったURLを使用
                    urls.append(url)
                    print(f"  ✅ 取得: {url}")
                else:
                    print(f"  ⚠️  URLが見つかりませんでした")
                    
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                continue
        
        if len(urls) < 2:
            print(f"\n⚠️  警告: 取得できたURLが{len(urls)}件です。最低2件必要です。")
            print(f"\n💡 代替案: 手動でURLを入力してください")
            
            # 手動入力のフォールバック
            urls = []
            for i in range(2):
                url = input(f"{i+1}つ目のURL: ").strip()
                if url:
                    urls.append(url)
            
            if len(urls) < 2:
                print("URLが不足しています。処理を中断します。")
                return []
        
        print(f"\n✅ {len(urls)}件のURLを取得しました:")
        for i, url in enumerate(urls[:3], 1):
            print(f"  {i}. {url}")
        
        if not wait_for_key():
            print("処理を中断しました")
            return []
    
    return urls


def save_urls_to_json(urls: List[str], filename: str = "collected_urls.json") -> bool:
    """
    収集したURLをJSONファイルに保存する
    
    Args:
        urls: URLのリスト
        filename: 保存先ファイル名
    
    Returns:
        保存が成功したかどうか
    """
    print("\n" + "="*60)
    print("共有データをJSONファイルに保存")
    print("="*60)
    
    data = {
        "collected_at": datetime.now().isoformat(),
        "query": "Amazon Nova",
        "urls": urls,
        "count": len(urls)
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 URLを保存しました: {filename}")
    print(f"📊 保存したURL数: {len(urls)}")
    
    if not wait_for_key():
        print("処理を中断しました")
        return False
    
    return True


def browser_b_summarize_urls(orchestrator: BrowserOrchestrator, urls: List[str]) -> SearchResult:
    """
    ブラウザBで各URLを開いて内容を要約する
    
    Args:
        orchestrator: BrowserOrchestrator インスタンス
        urls: 処理するURLのリスト
    
    Returns:
        SearchResult オブジェクト
    """
    print("\n" + "="*60)
    print("フェーズ2: ブラウザBでURL要約")
    print("="*60)
    
    search_result = SearchResult(query="Amazon Nova")
    
    if not urls or len(urls) < 2:
        print("❌ URLが不足しています")
        return search_result
    
    # 最初の2つのURLを処理対象とする
    target_urls = urls[:2]
    print(f"\n📥 以下の{len(target_urls)}件のURLを処理します:")
    for i, url in enumerate(target_urls, 1):
        print(f"  {i}. {url}")
    
    # 最初のURLで確認
    print(f"\n🔗 1つ目のURL: {target_urls[0]}")
    if not wait_for_key():
        print("処理を中断しました")
        return search_result
    
    with orchestrator.create_session("ブラウザB", target_urls[0]) as browser_b:
        
        # 1つ目のURLを処理
        print(f"\n📖 1つ目のURLを開いています...")
        summary1 = browser_b.execute(
            "このページの内容を3-4文で要約してください。"
            "特にAmazon Novaに関する重要な情報を含めてください。"
        )
        
        search_result.add_url(target_urls[0])
        search_result.add_summary(target_urls[0], str(summary1))
        print(f"\n📝 要約結果:\n{summary1}")
        
        # 2つ目のURLで確認
        print(f"\n🔗 2つ目のURL: {target_urls[1]}")
        if not wait_for_key():
            print("2つ目の処理をスキップしました")
        else:
            # 2つ目のURLを開く
            print(f"\n📖 2つ目のURLを開いています...")
            browser_b.execute(
                f"ブラウザのアドレスバーをクリックして、"
                f"このURL『{target_urls[1]}』を入力してEnterキーを押してください"
            )
            
            summary2 = browser_b.execute(
                "このページの内容を3-4文で要約してください。"
                "特にAmazon Novaに関する重要な情報を含めてください。"
            )
            
            search_result.add_url(target_urls[1])
            search_result.add_summary(target_urls[1], str(summary2))
            print(f"\n📝 要約結果:\n{summary2}")
        
        if not wait_for_key():
            print("処理を終了します")
            return search_result
    
    return search_result


def cross_check_scenario():
    """シナリオ2: 情報クロスチェック（リファクタリング版）"""
    
    with BrowserOrchestrator() as orchestrator:
        
        # フェーズ1: ブラウザAでURL収集
        urls = browser_a_collect_urls(orchestrator, "Amazon Nova")
        
        if not urls:
            print("URL収集に失敗しました。処理を終了します。")
            return None
        
        # 共有データに保存
        orchestrator.share_data("urls", urls)
        
        # JSONファイルに保存
        if not save_urls_to_json(urls):
            print("処理を中断しました")
            return None
        
        # フェーズ2: ブラウザBで要約
        search_result = browser_b_summarize_urls(orchestrator, urls)
        
        # 最終結果の表示
        print("\n" + "="*60)
        print("📊 最終結果")
        print("="*60)
        print(f"検索クエリ: {search_result.query}")
        print(f"収集したURL数: {len(search_result.urls)}")
        print(f"要約数: {len(search_result.summaries)}")
        
        for url, summary in search_result.summaries.items():
            print(f"\n🔗 URL: {url}")
            print(f"📄 要約: {summary}")
        
        return search_result


if __name__ == "__main__":
    try:
        result = cross_check_scenario()
        if result:
            print("\n✅ シナリオが正常に完了しました！")
    except Exception as e:
        print(f"\n❌ エラーが発生しました:\n{e}")
        import traceback
        traceback.print_exc()
