"""NovaActでヌーラボログイン画面を操作するスクリプト"""
import os
import sys
import termios
import tty

from browser_manager import BrowserOrchestrator

# AWSリージョンを設定
os.environ["AWS_REGION"] = "us-east-1"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


def wait_for_key() -> bool:
    """Enterキーで継続(True)、Escキーで停止(False)を返す"""
    print("\n待機中... Enterキーで継続、Escキーで停止...")

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
        
        if key in ['\r', '\n']:
            print("→ 継続します")
            return True
        elif key == '\x1b':
            print("→ 停止しました")
            return False
        else:
            print(f"→ 無効なキーです。Enterキーで継続、Escキーで停止してください")
            return wait_for_key()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def open_nulab_login():
    """ヌーラボログイン画面を開く"""

    with BrowserOrchestrator() as orchestrator:

        print("\n" + "="*60)
        print("ヌーラボアカウントログイン画面を開きます")
        print("="*60)

        # ヌーラボアカウントログイン画面
        nulab_login_url = "https://apps.nulab.com/signin"
        
        with orchestrator.create_session("ヌーラボログイン画面", nulab_login_url) as browser:

            print("\n→ ヌーラボアカウントログイン画面を開いています...")
            print(f"   URL: {nulab_login_url}")

            # コンソール画面が開くまで待機
            print("\n→ コンソール画面の読み込みを待っています...")
            
            # ページが完全に読み込まれるまで少し待つ
            browser.execute(
                "ページが完全に読み込まれるまで待ってください。"
            )

            if not wait_for_key():
                print("\n✗ 処理を中断しました")
                return False

            # コンソール画面が正しく表示されているか確認
            print("\n→ コンソール画面の表示を確認しています...")
            browser.execute(
                "現在表示されているページがヌーラボログインのホーム画面であることを確認してください。"
            )

            print("\n✓ ヌーラボログイン画面が正常に開きました！")
            print("\n次のステップ:")
            print("  - コンソール画面で各種AWSサービスにアクセスできます")
            print("  - 今後、具体的な操作（EC2インスタンス一覧表示など）を追加できます")

            return True


if __name__ == "__main__":
    try:
        result = open_nulab_login()
        if result:
            print("\n✓ 処理が完了しました！")
        else:
            print("\n✗ 処理が中断されました")
    except Exception as e:
        print(f"\n✗ エラーが発生しました:\n{e}")
        import traceback
        traceback.print_exc()
