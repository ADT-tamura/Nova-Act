import boto3
import json

# Bedrock Runtime クライアントを作成 (リージョンは us-east-1)
client = boto3.client("bedrock-runtime", region_name="us-east-1")

# モデルID (Amazon Nova Micro)
model_id = "amazon.nova-micro-v1:0"

# メッセージの設定
prompt = "Amazon Novaについて、特徴を短く教えてください。"
messages = [{"role": "user", "content": [{"text": prompt}]}]

# 推論の実行
response = client.converse(
    modelId=model_id,
    messages=messages,
    inferenceConfig={"maxTokens": 500, "temperature": 0.7}
)

# 結果の表示
print(response['output']['message']['content'][0]['text'])