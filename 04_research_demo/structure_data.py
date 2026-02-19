"""Amazon Nova Proを使って生テキストを構造化するスクリプト"""
import os
import json
from datetime import datetime
import boto3

from data_manager import ResearchData


def structure_with_nova(raw_text: str) -> ResearchData:
    """Amazon BedrockのNova Proを使ってテキストを構造化"""
    
    # Bedrockクライアントを作成
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1'
    )
    
    prompt = f"""以下はAmazon Nova Actの公式ページから取得した情報です。
この情報を以下のJSON形式に構造化してください：

{{
  "overview": "概要を3-5文で",
  "features": ["機能1", "機能2", "機能3"],
  "use_cases": ["ユースケース1", "ユースケース2", "ユースケース3"]
}}

取得した情報:
{raw_text}

JSON形式のみを出力してください。説明は不要です。"""
    
    print("\n🤖 Amazon BedrockのNova Proで構造化しています...")
    
    # Bedrock APIリクエスト（Nova用）
    request_body = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "inferenceConfig": {
            "max_new_tokens": 1024,
            "temperature": 0.7
        }
    }
    
    response = bedrock_runtime.converse(
        modelId="us.amazon.nova-pro-v1:0",
        messages=request_body["messages"],
        inferenceConfig=request_body["inferenceConfig"]
    )
    
    # レスポンスを解析
    response_text = response['output']['message']['content'][0]['text']
    
    print(f"\n📝 Nova Proの応答:\n{response_text}\n")
    
    # JSONをパース
    try:
        # コードブロックを削除
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        data = json.loads(response_text)
        
        # ResearchDataに変換
        research_data = ResearchData()
        research_data.nova_act_info.overview = data.get("overview", "")
        research_data.nova_act_info.features = data.get("features", [])
        research_data.nova_act_info.use_cases = data.get("use_cases", [])
        research_data.nova_act_info.additional_info = f"収集日時: {datetime.now().isoformat()}, URL: https://aws.amazon.com/jp/nova/act/"
        
        return research_data
        
    except json.JSONDecodeError as e:
        print(f"⚠️ JSONのパースに失敗しました: {e}")
        print(f"応答テキスト: {response_text}")
        return None


def main():
    """メイン処理"""
    
    # 生テキストを読み込み
    try:
        with open("raw_summary.txt", 'r', encoding='utf-8') as f:
            raw_text = f.read()
        print(f"📖 raw_summary.txt を読み込みました")
    except FileNotFoundError:
        print(f"❌ raw_summary.txt が見つかりません")
        print(f"先に python collect_info.py を実行してください")
        return
    
    # Nova Proで構造化
    research_data = structure_with_nova(raw_text)
    
    if research_data:
        # JSONファイルに保存
        research_data.save_to_json()
        
        print("\n📊 構造化されたデータ:")
        print(f"  overview: {research_data.nova_act_info.overview}")
        print(f"  features: {research_data.nova_act_info.features}")
        print(f"  use_cases: {research_data.nova_act_info.use_cases}")
        
        print("\n✅ 構造化が完了しました！")
        print(f"📄 次のステップ: python research_demo.py を実行してフォーム入力してください")
    else:
        print("\n❌ 構造化に失敗しました")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ エラーが発生しました:\n{e}")
        import traceback
        traceback.print_exc()
