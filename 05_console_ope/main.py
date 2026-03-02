"""メインオーケストレーター - 全処理を自動実行"""
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


def main():
    """全処理を順番に実行"""

    print("="*60)
    print("Amazon Nova Act - ヌーラボ操作デモ")
    print("="*60)

    with BrowserOrchestrator() as orchestrator:

        # ステップ1: ヌーラボログイン
        print("\n" + "="*60)
        print("ステップ1: ヌーラボログイン")
        print("="*60)

        nulab_login_url = "https://apps.nulab.com/signin"
        
        with orchestrator.create_session("ヌーラボログイン", nulab_login_url) as browser:

            print("\n→ ログイン画面を開いています...")
            browser.execute("ページが完全に読み込まれるまで待ってください。")

            print("\n→ Emailを入力しています...")
            browser.execute("Emailの入力フォームに'advance.sbn.saas.test@gmail.com'を入力してください。")

            print("\n→ Nextボタンを押しています...")
            browser.execute("Nextボタンをクリックしてください。")

            print("\n→ パスワードを入力しています...")
            browser.execute("パスワードの入力フォームに'sjduvnfu'を入力してください。")

            print("\n→ ログインボタンを押しています...")
            browser.execute("ログインボタンをクリックしてください。")
            print("  - ログイン完了")

        print("\n✓ ステップ1完了")

        # ステップ2: プロジェクト選択
        print("\n" + "="*60)
        print("ステップ2: プロジェクト選択")
        print("="*60)

        nulab_projects_url = "https://apps.nulab.com/"
        
        with orchestrator.create_session("プロジェクト選択", nulab_projects_url) as browser:

            print("\n→ プロジェクト一覧画面を開いています...")
            browser.execute("ページが完全に読み込まれるまで待ってください。")

            print("\n→ プロジェクト一覧を確認しています...")
            browser.execute("現在表示されているページにプロジェクト一覧が表示されていることを確認してください。")

            print("\n→ 'NovaActデモプレイ'プロジェクトを選択しています...")
            browser.execute("プロジェクト一覧から'NovaActデモプレイ'という名前のプロジェクトをクリックしてください。")
            print("  - プロジェクト選択完了")

            if not wait_for_key():
                print("\n→ 処理を中断します")
                return

        print("\n✓ ステップ2完了")

    # 完了
    print("\n" + "="*60)
    print("✓ すべての処理が完了しました！")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n→ ユーザーによって中断されました")
    except Exception as e:
        print(f"\n✗ エラーが発生しました:\n{e}")
        import traceback
        traceback.print_exc()
