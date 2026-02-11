import streamlit as st
import re
import smtplib
import random
from email.mime.text import MIMEText

def send_admin_code(target_email, code):
    try:
        sender = st.secrets["EMAIL_SENDER"]
        password = st.secrets["EMAIL_PASSWORD"]
        msg = MIMEText(f"Your one-time Twisted App Admin Access Code is: {code}\n\nValid for this session only.")
        msg['Subject'] = "🔐 Admin Access Requested"
        msg['From'] = sender
        msg['To'] = target_email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, target_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) if email else True

def nuclear_clean(val):
    import pandas as pd
    if pd.isna(val): return ""
    s = str(val).strip().replace('.0', '')
    return re.sub(r'\D', '', s)
