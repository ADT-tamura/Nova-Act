"""NovaActでページ内容を収集するスクリプト"""
import os
import sys
import termios
import tty

from browser_manager import BrowserOrchestrator

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


def collect_page_content():
    """ページ内容を収集"""
    
    with BrowserOrchestrator() as orchestrator:
        
        print("\n" + "="*60)
        print("ページ内容を収集")
        print("="*60)
        
        with orchestrator.create_session("ブラウザA", "https://aws.amazon.com/jp/nova/act/") as browser_a:
            
            # ページ内容を取得
            print("\n📖 ページ内容を取得しています...")
            
            # まずページをスクロール
            browser_a.execute(
                "このページ全体を上から下までゆっくりスクロールして、すべての内容を確認してください。"
            )
            
            if not wait_for_key():
                return None
            
            # ページのテキストをコピー（別のアプローチ）
            print("\n📝 ページのテキストを取得しています...")
            
            # 代替案: ページのHTMLを直接取得
            # NovaActではなく、Seleniumやrequestsを使う
            import requests
            from bs4 import BeautifulSoup
            
            try:
                response = requests.get("https://aws.amazon.com/jp/nova/act/")
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 主要なテキストを抽出
                # スクリプトやスタイルを除外
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # テキストを取得
                text = soup.get_text()
                
                # 空行を削除して整形
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                raw_summary = '\n'.join(chunk for chunk in chunks if chunk)
                
                print(f"✅ ページのテキストを取得しました（{len(raw_summary)}文字）")
                print(f"\n📝 取得した内容（最初の500文字）:\n{raw_summary[:500]}...\n")
                
            except Exception as e:
                print(f"❌ ページの取得に失敗しました: {e}")
                return None
            
            # 生テキストを一時ファイルに保存
            if raw_summary:
                with open("raw_summary.txt", 'w', encoding='utf-8') as f:
                    f.write(raw_summary)
                print(f"💾 生テキストを raw_summary.txt に保存しました")
                return raw_summary
            else:
                print(f"⚠️ 内容を取得できませんでした")
                return None


if __name__ == "__main__":
    try:
        result = collect_page_content()
        if result:
            print("\n✅ 情報収集が完了しました！")
            print(f"📄 次のステップ: python structure_data.py を実行してください")
    except Exception as e:
        print(f"\n❌ エラーが発生しました:\n{e}")
        import traceback
        traceback.print_exc()
