"""NovaActの情報収集とフォーム入力のメインシナリオ"""
import os
import sys
import termios
import tty
from datetime import datetime

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


def research_scenario():
    """NovaActの情報収集とフォーム入力シナリオ"""
    
    research_data = ResearchData()
    
    with BrowserOrchestrator() as orchestrator:
        
        # ========== フェーズ1: 情報収集 ==========
        print("\n" + "="*60)
        print("フェーズ1: NovaActの情報を収集")
        print("="*60)
        
        with orchestrator.create_session("ブラウザA", "https://testaimarket.xsrv.jp/technology/amazon-nova-act/#Nova_Act-2") as browser_a:
            
            # ページを要約
            print("\n📖 ページをスクロールしています...")
            scroll_result = browser_a.execute(
                "このページ全体をスクロールして、Amazon Nova Actに関する情報を確認してください。"
            )
            
            print(f"\n🔍 スクロール結果の型: {type(scroll_result)}")
            print(f"🔍 スクロール結果: {str(scroll_result)[:200]}...")
            
            if not wait_for_key():
                return None
            
            # 要約を取得
            print("\n📝 要約を取得しています...")
            summary_result = browser_a.execute(
                "今確認したページの内容について、Amazon Nova Actを3-5文で要約してください。"
            )
            
            print(f"\n🔍 要約結果の型: {type(summary_result)}")
            
            if summary_result:
                # 結果を文字列に変換
                if hasattr(summary_result, 'response'):
                    result_text = summary_result.response
                    print(f"🔍 response属性を使用")
                elif hasattr(summary_result, '__str__'):
                    result_text = str(summary_result)
                    print(f"🔍 __str__()を使用")
                else:
                    result_text = repr(summary_result)
                    print(f"🔍 repr()を使用")
                
                print(f"🔍 取得したテキスト（最初の500文字）:\n{result_text[:500]}\n")
                
                # ActResultメタデータのチェック
                has_metadata = "ActResult" in result_text or "metadata" in result_text
                print(f"🔍 メタデータ含有: {has_metadata}")
                
                if not has_metadata:
                    # 正常な要約テキストとして保存
                    research_data.nova_act_info.overview = result_text.strip()
                    print(f"✅ 要約を保存しました")
                else:
                    print(f"⚠️ メタデータが含まれているため、空文字列を設定します")
                    research_data.nova_act_info.overview = ""
            else:
                print(f"⚠️ 要約結果がNullです")
                research_data.nova_act_info.overview = ""
            
            research_data.nova_act_info.additional_info = f"収集日時: {datetime.now().isoformat()}, URL: https://aws.amazon.com/jp/nova/act/"
            
            print("\n📊 保存するデータ:")
            print(f"  overview: {research_data.nova_act_info.overview[:100] if research_data.nova_act_info.overview else '(空)'}...")
            print(f"  features: {research_data.nova_act_info.features}")
            print(f"  use_cases: {research_data.nova_act_info.use_cases}")
            
            print("\n✅ 情報を記録しました")
            
            # JSONファイルに保存
            research_data.save_to_json()
            
            # 保存されたJSONファイルを確認
            print("\n🔍 保存されたJSONファイルの内容を確認:")
            import json
            with open("nova_act_research.json", 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
                print(json.dumps(saved_data, ensure_ascii=False, indent=2)[:500])
            
            orchestrator.share_data("research_data", research_data)
            
            if not wait_for_key():
                return research_data
        
        # ========== フェーズ2: フォーム入力 ==========
        print("\n" + "="*60)
        print("フェーズ2: Googleフォームに入力")
        print("="*60)
        
        research_data = orchestrator.get_shared_data("research_data")
        
        with orchestrator.create_session("ブラウザB", "https://forms.gle/RA4yez3AsU5LxbtQ6") as browser_b:
            
            browser_b.execute("このページ全体をゆっくりスクロールして、すべての質問項目を確認してください。")
            
            if not wait_for_key():
                return research_data
            
            nova_info = research_data.nova_act_info
            
            # 1つ目: 機能
            if nova_info.features:
                features_text = ", ".join(nova_info.features)
                print(f"\n📝 機能を入力: {features_text}")
                browser_b.execute("ページの一番上にある最初のテキスト入力欄をクリックしてください。")
                browser_b.execute(f"クリックした入力欄に次のテキストを入力してください: {features_text}")
                
                if not wait_for_key():
                    return research_data
            
            # 2つ目: ユースケース
            if nova_info.use_cases:
                use_cases_text = ", ".join(nova_info.use_cases)
                print(f"\n📝 ユースケースを入力: {use_cases_text}")
                browser_b.execute("ページを下にスクロールして、1つ目の入力欄の下にある次のテキスト入力欄を画面に表示してください。")
                browser_b.execute("今画面に表示されている、1つ目とは異なる2番目のテキスト入力欄をクリックしてください。")
                browser_b.execute(f"今クリックした2番目の入力欄に次のテキストを入力してください: {use_cases_text}")
                
                if not wait_for_key():
                    return research_data
            
            print("\n✅ 入力完了")
            browser_b.execute("ページの下部にある送信ボタンを探して表示してください。")
            
            if not wait_for_key():
                return research_data
        
        print("\n✅ 調査完了")
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
