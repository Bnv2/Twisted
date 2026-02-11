import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
import io

def upload_to_drive(file_obj, filename, folder_id):
    creds_info = st.secrets["connections"]["gsheets"]
    creds = service_account.Credentials.from_service_account_info(
        creds_info, 
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': filename, 'parents': [folder_id]}
    file_content = file_obj.getvalue()
    media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype='image/jpeg', resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')
