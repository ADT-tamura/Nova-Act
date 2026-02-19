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
    
    # ステップ2: Nova Proで構造化
    print("\n" + "="*60)
    print("ステップ2: Nova Proでデータを構造化")
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
        
    except Exception as e:
        print(f"\n❌ ステップ2でエラーが発生しました:\n{e}")
        import traceback
        traceback.print_exc()
        return
    
    # ステップ3: Googleフォームに入力
    print("\n" + "="*60)
    print("ステップ3: Googleフォームに入力")
    print("="*60)
    
    input("\n🔔 ステップ3を開始します。Enterキーを押してください...")
    
    try:
        from form_input import input_to_form
        input_to_form()
        
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
