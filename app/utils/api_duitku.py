import hashlib
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Gunakan URL Sandbox (Testing) selama masa pengembangan
DUITKU_API_URL = "https://api-prod.duitku.com/webapi/api/merchant/v2/inquiry"

def create_invoice(order_id, amount, payment_method, product_details, customer_email="tester@pixietopup.my.id", customer_phone="08123456789"):
    """Mengirim request ke Duitku untuk membuat link pembayaran"""
    merchant_code = os.getenv('DUITKU_MERCHANT_CODE')
    api_key = os.getenv('DUITKU_API_KEY')
    
    # Ambil Base URL aplikasi dari .env (Otomatis hapus garis miring di akhir jika ada)
    app_base_url = os.getenv('APP_BASE_URL', 'http://127.0.0.1:5000').rstrip('/')

    # Rumus Signature Duitku: MD5(merchantCode + orderId + paymentAmount + apiKey)
    sign_str = f"{merchant_code}{order_id}{int(amount)}{api_key}"
    signature = hashlib.md5(sign_str.encode()).hexdigest()

    payload = {
        "merchantCode": merchant_code,
        "paymentAmount": int(amount),
        "paymentMethod": payment_method,
        "merchantOrderId": order_id,
        "productDetails": product_details,
        "additionalParam": "",
        "merchantUserInfo": "",
        "customerVaName": "PixeTopup Customer",
        "email": customer_email,
        "phoneNumber": customer_phone,
        "itemDetails": [{
            "name": product_details,
            "price": int(amount),
            "quantity": 1
        }],
        # URL sekarang mengambil secara dinamis dari file .env
        "callbackUrl": f"{app_base_url}/api/callback/duitku",
        "returnUrl": f"{app_base_url}/success",
        "signature": signature,
        "expiryPeriod": 60 
    }

    try:
        response = requests.post(DUITKU_API_URL, json=payload)
        return response.json()
    except Exception as e:
        return {"statusCode": "99", "statusMessage": str(e)}
