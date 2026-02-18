import streamlit as st
import os
from datetime import datetime, timedelta
import stripe
import requests
from PIL import Image

# Debug Header
st.title("ClaimCards - Debug Mode")
st.markdown("Debug version to find why the page was blank.")

# Environment info
st.subheader("Environment")
st.write(f"Streamlit version: {st.__version__}")

# Secrets check
st.subheader("Secrets Status")
supabase_url   = os.getenv("SUPABASE_URL")
supabase_key   = os.getenv("SUPABASE_KEY")
stripe_key     = os.getenv("STRIPE_SECRET_KEY")

st.write("SUPABASE_URL present:", "Yes" if supabase_url else "**No**")
st.write("SUPABASE_KEY present:", "Yes" if supabase_key else "**No**")
st.write("STRIPE_SECRET_KEY present:", "Yes" if stripe_key else "**No**")

if not supabase_url or not supabase_key:
    st.error(
        "Supabase secrets are missing!\n\n"
        "How to fix:\n"
        "1. On this page → bottom-right corner → click 'Manage app'\n"
        "2. In the dashboard → click 'Settings'\n"
        "3. Look for 'Secrets' section\n"
        "4. Paste this (replace with your real values):\n\n"
        'SUPABASE_URL = "https://your-project-ref.supabase.co"\n'
        'SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-anon-public-key-here"\n'
        'STRIPE_SECRET_KEY = "sk_test_your-test-key-here"\n\n'
        "5. Click Save → then Reboot the app → refresh this page"
    )
    st.stop()

st.success("Secrets look good — trying to connect to Supabase...")

# Connection test
try:
    from st_supabase_connection import SupabaseConnection
    conn = st.connection(
        "supabase",
        type=SupabaseConnection,
        url=supabase_url,
        key=supabase_key
    )
    st.success("Supabase connected successfully!")
except Exception as e:
    st.error(f"Connection failed: {str(e)}")
    st.info("Common fixes: wrong anon key, bad URL, or Supabase project not set up.")
    st.stop()

# If we get here, core setup works — show basic app
st.divider()
st.success("Core setup passed! You can now add login/sales features.")
st.write("Next step: add secrets if missing, then reboot the app.")