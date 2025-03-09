# Configure Cloudinary
import os
from flask import Flask, request, jsonify
import base64
import cloudinary
cloudinary.config(
    cloud_name="dimdoq0ng",
    api_key="324659127373814",
    api_secret="eUTC_Jxfvw95dkaCDN7yHEomugE"
)



def uploadImg(base64_image):
    try:
        file_to_upload = base64.b64decode(base64_image)
        upload_result = cloudinary.uploader.upload(file_to_upload)
        return upload_result.get('secure_url')
    except Exception as e:
        return None
    

##for sms
