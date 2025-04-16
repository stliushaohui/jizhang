import requests

# url = "https://yizhixiaoyuer.cn/api/add"
url = " http://127.0.0.1:5000/api/add"

data = {
  "username": "lsh11",
  "password": "bn123456",
  "type": "expense",
  "amount": 12.5,
  "note": "饮料",
  "date": "2025-04-16"
}


response = requests.post(url, json=data)  # ✅ 改这里！

print("状态码:", response.status_code)
try:
    print("返回结果:", response.json())
except Exception as e:
    print("无法解析为 JSON，返回内容为：", response.text)
