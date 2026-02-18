import streamlit as st
import os
from datetime import datetime, timedelta
import stripe
import requests
from PIL import Image

# ────────────────────────────────────────────────
# Debug Header - always visible
# ────────────────────────────────────────────────
st.title("ClaimCards - Debug & Startup Screen")
st.markdown("This is a debug version to help fix the blank page issue.")

# Show environment info
st.subheader("Environment Check")
st.write(f"Python version: {sys.version.split()[0]}")
st.write(f"Streamlit version: {st.__version__}")

# ────────────────────────────────────────────────
# Load secrets with visibility
# ────────────────────────────────────────────────
st.subheader("Secrets Status")
supabase_url   = os.getenv("SUPABASE_URL")
supabase_key   = os.getenv("SUPABASE_KEY")
stripe_key     = os.getenv("STRIPE_SECRET_KEY")

st.write("SUPABASE_URL   :", "✅ Present" if supabase_url   else "❌ Missing")
st.write("SUPABASE_KEY   :", "✅ Present" if supabase_key   else "❌ Missing")
st.write("STRIPE_SECRET_KEY :", "✅ Present" if stripe_key else "❌ Missing")

if not supabase_url or not supabase_key:
    st.error("""
    Supabase secrets are missing.
    
    Fix: 
    1. Go to your app page → bottom-right → **Manage app**
    2. In dashboard → **Settings** → **Secrets**
    3. Paste exactly (replace values):
    