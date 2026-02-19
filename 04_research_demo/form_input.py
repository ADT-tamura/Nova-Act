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
        
        with orchestrator.create_session("ブラウザB", "https://forms.gle/bkfqLXki7hoHX1iT7") as browser_b:
            
            browser_b.execute("このページ全体をゆっくりスクロールして、すべての質問項目を確認してください。")
            
            nova_info = research_data.nova_act_info
            
            # 特徴を入力
            if nova_info.features:
                features_text = ", ".join(nova_info.features)
                print(f"\n📝 特徴を入力: {features_text}")
                
                # まずクリック
                browser_b.execute(
                    "「NovaActの特徴」という質問の下にある「回答を入力」と書かれた入力欄をクリックしてください。"
                )
                
                # 次に入力
                browser_b.execute(
                    f"フォーカスされている入力欄に次のテキストを入力してください: {features_text}"
                )
                
                print(f"✅ 入力完了")
            
            print("\n✅ 入力が完了しました")
            
            # 送信ボタンを表示
            browser_b.execute(
                "ページの下部にスクロールして、「送信」ボタンを画面に表示してください。"
            )
            
            if not wait_for_key():
                print("\n⛔ 送信をスキップしました")
                return
            
            # 送信ボタンをクリック
            browser_b.execute(
                "「送信」ボタンをクリックしてください。"
            )
            
            print("\n✅ フォームを送信しました！")
    
    print("\n✅ フォーム入力処理が完了しました！")


if __name__ == "__main__":
    try:
        input_to_form()
    except Exception as e:
        print(f"\n❌ エラーが発生しました:\n{e}")
        import traceback
        traceback.print_exc()
