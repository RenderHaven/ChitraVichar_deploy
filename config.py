# Configure Cloudinary
import os
from flask import Flask, request, jsonify
import base64
import cloudinary
import cloudinary.uploader
import time,json,random,requests

OTP_FILE = "otp_store.json"
cloudinary.config(
    cloud_name="dlvg9hkax",
    api_key="433946728882916",
    api_secret="mSix-JVm0Y0rmxzNbkt3M2K-toE"
)

def verify_widget_token(jwt_token):
    url = "https://control.msg91.com/api/v5/widget/verifyAccessToken"
    payload = {
        "authkey": "444162AojpM5TtIQ7067f64aeeP1",
        "access-token": jwt_token
    }
    response = requests.post(url, json=payload)
    return response.json()

def uploadImg(base64_image):
    try:
        file_to_upload = base64.b64decode(base64_image.split(',')[-1])
        upload_result = cloudinary.uploader.upload(file_to_upload)
        return upload_result.get('secure_url')
    except Exception as e:
        print(e)
        return None

def load_otps():
    try:
        with open(OTP_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_otps(otps):
    with open(OTP_FILE, "w") as file:
        json.dump(otps, file)


def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_request(phone, otp):
    """Sends OTP using your notification API"""

    url = "https://api.notificationapi.com/15yug2unemeofmslzf6l8muj3k/sender"
    headers = {
        "authorization": "Basic MTV5dWcydW5lbWVvZm1zbHpmNmw4bXVqM2s6N2h4bDFlajVmMmJnNmsyczRxdXBvMmF4MGc2bTI3Nzk2YjN6amI3Y3o5MDhzY2g3bGtraWZtb3VnMQ==",
        "content-type": "application/json"
    }
    
    payload = {
        "notificationId": "otp",
        "user": {
            "id": "chitravichar.in@gmail.com",
            "email": "chitravichar.in@gmail.com",
            "number": '+91'+phone  # Dynamic phone number
        },
        "mergeTags": {
            "comment": f"{otp}"  # Sending OTP
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    print(response)
    return response.json()

def send_otp(phone):

    otp = generate_otp()
    timestamp = int(time.time())
    otps = load_otps()
    otps[phone] = {"otp": otp, "timestamp": timestamp}
    save_otps(otps)
    
    send_otp_request(phone,otp)

    return jsonify({"message": "OTP sent successfully", "otp": otp})

def verify_otp(phone,user_otp):
    print(user_otp)
    otps = load_otps()
    if phone in otps:
        stored_otp, timestamp = otps[phone]["otp"], otps[phone]["timestamp"]
        if stored_otp == user_otp and int(time.time()) - timestamp < 300:
            del otps[phone]  # Delete OTP after successful verification
            save_otps(otps)
            return True
        else:
            return False
    else:
        return False
