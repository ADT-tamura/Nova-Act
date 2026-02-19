"""メインオーケストレーター - 全処理を自動実行"""
import os
import sys

# AWSリージョンを設定
os.environ["AWS_REGION"] = "us-east-1"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


def main():
    """全処理を順番に実行"""
    
    print("="*60)
    print("Amazon Nova Act 情報収集 & フォーム入力")
    print("="*60)
    
    # ステップ1: NovaActで情報収集
    print("\n" + "="*60)
    print("ステップ1: NovaActでページ内容を収集")
    print("="*60)
    
    try:
        from collect_info import collect_page_content
        raw_text = collect_page_content()
        
        if not raw_text:
            print("\n❌ 情報収集に失敗しました")
            return
        
        print("\n✅ ステップ1完了")
        
    except Exception as e:
        print(f"\n❌ ステップ1でエラーが発生しました:\n{e}")
        import traceback
        traceback.print_exc()
        return
    
    # ステップ2: Claudeで構造化
    print("\n" + "="*60)
    print("ステップ2: Claudeでデータを構造化")
    print("="*60)
    
    try:
        from structure_data import structure_with_nova
        research_data = structure_with_nova(raw_text)
        
        if not research_data:
            print("\n❌ データ構造化に失敗しました")
            return
        
        # JSONファイルに保存
        research_data.save_to_json()
        
        print("\n📊 構造化されたデータ:")
        print(f"  overview: {research_data.nova_act_info.overview[:100]}...")
        print(f"  features: {research_data.nova_act_info.features}")
        print(f"  use_cases: {research_data.nova_act_info.use_cases}")
        
        print("\n✅ ステップ2完了")
        
        print("\n🔍 デバッグ: ステップ2が完了しました。ステップ3に進みます...")
        
    except Exception as e:
        print(f"\n❌ ステップ2でエラーが発生しました:\n{e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n🔍 デバッグ: ステップ3の直前です")
    
    # ステップ3: Googleフォームに入力
    print("\n" + "="*60)
    print("ステップ3: Googleフォームに入力")
    print("="*60)
    
    input("\n🔔 ステップ3を開始します。Enterキーを押してください...")
    
    try:
        # research_demo.pyのフォーム入力部分を実行
        import termios
        import tty
        from datetime import datetime
        from browser_manager import BrowserOrchestrator
        
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
        
        print("\n✅ ステップ3完了")
        
    except Exception as e:
        print(f"\n❌ ステップ3でエラーが発生しました:\n{e}")
        import traceback
        traceback.print_exc()
        return
    
    # 完了
    print("\n" + "="*60)
    print("🎉 すべての処理が完了しました！")
    print("="*60)
    print(f"📄 結果は nova_act_research.json に保存されています")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ ユーザーによって中断されました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました:\n{e}")
        import traceback
        traceback.print_exc()
