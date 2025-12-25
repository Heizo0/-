import requests
import time
TARGET_URL = "http://your-test-server.com/submit"  # 請替換為您要測試的目標網址改變同學的URL
FORM_FIELD_NAME = "input_text"                  
PROMPT_TO_SEND = "This is a test prompt."      
REQUEST_INTERVAL_SECONDS = 1                     
NUMBER_OF_REQUESTS = 10                          
def send_request(url, field_name, data):
    """向指定的 URL 發送 POST 請求"""
    try:
        payload = {field_name: data}
       
        # 這裡假設您的輸入框提交後會觸發 POST 請求
        response = requests.post(url, data=payload, timeout=5)
       
        # 檢查回應狀態
        if response.status_code == 200:
            print(f"✅ 成功發送！狀態碼: 200. 回應長度: {len(response.text)}")
        else:
            print(f"⚠️ 請求失敗！狀態碼: {response.status_code}")
           
    except requests.exceptions.RequestException as e:
        print(f"❌ 發生錯誤: {e}")

# 執行迴圈
print(f"開始向 {TARGET_URL} 發送 {NUMBER_OF_REQUESTS} 次請求...")

for i in range(1, NUMBER_OF_REQUESTS + 1):
    print(f"--- 第 {i} 次請求 ---")
    send_request(TARGET_URL, FORM_FIELD_NAME, f"{PROMPT_TO_SEND} {i}")
   
    # 暫停指定的秒數，實現「每秒不斷」
    if i < NUMBER_OF_REQUESTS:
        time.sleep(REQUEST_INTERVAL_SECONDS)

print("--- 請求模擬結束 ---")
