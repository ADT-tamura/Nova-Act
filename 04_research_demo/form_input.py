"""Googleフォームに入力するスクリプト"""
import os
import sys
import termios
import tty

from browser_manager import BrowserOrchestrator
from data_manager import ResearchData

# AWSリージョンを設定
os.environ["AWS_REGION"] = "us-east-1"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


def wait_for_key() -> bool:
    """Enterキーで続行(True)、Escキーで停止(False)を返す"""
    print("\n⏸️  Enterキーで続行、Escキーで停止...")
    
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
        
        if key in ['\r', '\n']:
            print("✅ 続行します")
            return True
        elif key == '\x1b':
            print("⛔ 停止しました")
            return False
        else:
            print(f"❌ 無効なキーです。Enterキーで続行、Escキーで停止してください")
            return wait_for_key()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def input_to_form():
    """Googleフォームに入力"""
    
    # JSONファイルから読み込み
    try:
        research_data = ResearchData.load_from_json()
        print(f"📖 nova_act_research.json を読み込みました")
    except FileNotFoundError:
        print(f"❌ nova_act_research.json が見つかりません")
        return
    
    print("\n" + "="*60)
    print("Googleフォームに入力")
    print("="*60)
    
    with BrowserOrchestrator() as orchestrator:
        
        with orchestrator.create_session("ブラウザB", "https://forms.gle/RA4yez3AsU5LxbtQ6") as browser_b:
            
            browser_b.execute("このページ全体をゆっくりスクロールして、すべての質問項目を確認してください。")
            
            if not wait_for_key():
                print("\n⛔ フォーム入力をスキップしました")
                return
            
            nova_info = research_data.nova_act_info
            
            # 1つ目: 機能
            if nova_info.features:
                features_text = ", ".join(nova_info.features)
                print(f"\n📝 機能を入力: {features_text}")
                browser_b.execute("ページの一番上にある最初のテキスト入力欄をクリックしてください。")
                browser_b.execute(f"クリックした入力欄に次のテキストを入力してください: {features_text}")
                
                if not wait_for_key():
                    return
            
            # 2つ目: ユースケース
            if nova_info.use_cases:
                use_cases_text = ", ".join(nova_info.use_cases)
                print(f"\n📝 ユースケースを入力: {use_cases_text}")
                browser_b.execute("ページを下にスクロールして、1つ目の入力欄の下にある次のテキスト入力欄を画面に表示してください。")
                browser_b.execute("今画面に表示されている、1つ目とは異なる2番目のテキスト入力欄をクリックしてください。")
                browser_b.execute(f"今クリックした2番目の入力欄に次のテキストを入力してください: {use_cases_text}")
                
                if not wait_for_key():
                    return
            
            print("\n✅ 入力完了")
            browser_b.execute("ページの下部にある送信ボタンを探して表示してください。")
            
            if not wait_for_key():
                return
    
    print("\n✅ フォーム入力が完了しました！")


if __name__ == "__main__":
    try:
        input_to_form()
    except Exception as e:
        print(f"\n❌ エラーが発生しました:\n{e}")
        import traceback
        traceback.print_exc()
