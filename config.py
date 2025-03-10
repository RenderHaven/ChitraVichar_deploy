# Configure Cloudinary
import os
from flask import Flask, request, jsonify
import base64
import cloudinary
import cloudinary.uploader
cloudinary.config(
    cloud_name="dlvg9hkax",
    api_key="433946728882916",
    api_secret="mSix-JVm0Y0rmxzNbkt3M2K-toE"
)



def uploadImg(base64_image):
    try:
        file_to_upload = base64.b64decode(base64_image)
        upload_result = cloudinary.uploader.upload(file_to_upload)
        return upload_result.get('secure_url')
    except Exception as e:
        print(e)
        return None
    

##for sms
