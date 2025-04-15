import requests
import json

url = "http://yizhixiaoyuer.cn/api/add"  # 如果部署在线上，请改成你的域名，例如 https://yizhixiaoyuer.cn/api/add

headers = {
    "Content-Type": "application/json"
}

data = {
    "token": "lsh88nihao",  # 替换为你在 app.py 中配置的 token
    "type": "expense",          # 或 "income"
    "amount": 88.5,
    "note": "测试 - 买零食",
    "date": "2025-04-15"
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print("状态码:", response.status_code)
print("返回结果:", response.json())
data = {
    "token": "lsh88nihao",
    "type": "expense",
    "amount": 88.5,
    "note": "测试 - 买零食",
    "date": "2025-04-15"
}
