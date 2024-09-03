import requests
import json
import os

def generate_pdf():
    url = "http://38.108.68.174:3001/generate-pdf"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "url": "https://grafana.project.yaguang2021.win/d/bdwqxyz9f8l4wa/creatingly-reports?orgId=1"
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(response.text)

    return response.json()

def download_pdf(pdf_url):
    response = requests.get(pdf_url)
    
    if response.status_code == 200:
        filename = os.path.basename(pdf_url)
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"PDF downloaded successfully: {filename}")
        return filename
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")
        return None

def send_to_telegram(file_path, bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    
    with open(file_path, 'rb') as file:
        files = {'document': file}
        data = {'chat_id': chat_id}
        
        response = requests.post(url, data=data, files=files)
    
    if response.status_code == 200:
        print("File sent successfully to Telegram.")
    else:
        print(f"Failed to send file to Telegram. Status code: {response.status_code}")
        print(f"Response: {response.text}")

# Telegram Bot configuration
BOT_TOKEN = "7252767905:AAFqlDhkFPgMbZsNaDAMRY2PuM8FIEfkooA"
CHAT_ID = "278739468"

# Generate PDF and get the URL
result = generate_pdf()
pdf_url = result.get('pdfUrl')

if pdf_url:
    print(f"PDF URL: {pdf_url}")
    filename = download_pdf(pdf_url)
    if filename:
        send_to_telegram(filename, BOT_TOKEN, CHAT_ID)
else:
    print("PDF URL not found in the response.")
