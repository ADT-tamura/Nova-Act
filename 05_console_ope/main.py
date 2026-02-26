"""メインオーケストレーター - 全処理を自動実行"""
import os
import sys

# AWSリージョンを設定
os.environ["AWS_REGION"] = "us-east-1"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


def main():
    """全処理を順番に実行"""

    print("="*60)
    print("Amazon Nova Act - AWSコンソール操作デモ")
    print("="*60)

    # ステップ1: NovaActでAWSコンソールを開く
    print("\n" + "="*60)
    print("ステップ1: NovaActでヌーラボアカウントログイン画面を開く")
    print("="*60)

    try:
        from nulab_login import open_nulab_login
        result = open_nulab_login()

        if not result:
            print("\n✗ ヌーラボアカウントログイン画面を開くのに失敗しました")
            return

        print("\n✓ ステップ1完了")

    except Exception as e:
        print(f"\n✗ ステップ1でエラーが発生しました:\n{e}")
        import traceback
        traceback.print_exc()
        return

    # 今後のステップ（コメントアウト）
    # ステップ2: 特定のAWSサービスにアクセス
    # ステップ3: 情報を収集
    # など

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
