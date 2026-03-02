"""ヌーラボログインとプロジェクト選択を1つのセッションで実行"""
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


def nulab_workflow():
    """ヌーラボログインからプロジェクト選択まで一連の処理"""

    print("="*60)
    print("Amazon Nova Act - ヌーラボ操作デモ")
    print("="*60)

    with BrowserOrchestrator() as orchestrator:
        
        nulab_login_url = "https://apps.nulab.com/signin"
        
        with orchestrator.create_session("ヌーラボ操作", nulab_login_url) as browser:

            # ========== ステップ1: ログイン ==========
            print("\n" + "="*60)
            print("ステップ1: ヌーラボログイン")
            print("="*60)

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

            # ========== ステップ2: プロジェクト選択 ==========
            print("\n" + "="*60)
            print("ステップ2: プロジェクト選択")
            print("="*60)

            print("\n→ プロジェクト一覧画面に移動しています...")
            browser.execute("現在のページから'NovaActデモプレイ'という名前のプロジェクトをダブルクリックしてください。")
            print("  - プロジェクト選択完了")

            if not wait_for_key():
                print("\n→ 処理を中断します")
                return False

            print("\n✓ ステップ2完了")

            return True

    # 完了
    print("\n" + "="*60)
    print("✓ すべての処理が完了しました！")
    print("="*60)


if __name__ == "__main__":
    try:
        result = nulab_workflow()
        if not result:
            print("\n✗ 処理が中断されました")
    except KeyboardInterrupt:
        print("\n\n→ ユーザーによって中断されました")
    except Exception as e:
        print(f"\n✗ エラーが発生しました:\n{e}")
        import traceback
        traceback.print_exc()
