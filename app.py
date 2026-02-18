import streamlit as st
import os
from datetime import datetime, timedelta
import stripe
import requests
from PIL import Image

# ────────────────────────────────────────────────
# Minimal safety check
# ────────────────────────────────────────────────
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    st.error("Supabase secrets missing - add them in Manage app → Settings → Secrets")
    st.stop()

# Connect to Supabase
from st_supabase_connection import SupabaseConnection
conn = st.connection("supabase", type=SupabaseConnection)

st.set_page_config(page_title="ClaimCards", layout="wide")

# Sidebar
page = st.sidebar.selectbox("Go to", ["Home", "Login / Sign Up", "Create a Sale", "Browse Sales"])

# Home
if page == "Home":
    st.title("Welcome to ClaimCards")
    st.write("Log in to create or claim trading card sales.")

# Login / Sign Up
elif page == "Login / Sign Up":
    st.header("Login / Sign Up")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pw")
            if st.button("Login"):
                if not email or not password:
                    st.warning("Please enter email and password.")
                else:
                    with st.spinner("Logging in..."):
                        try:
                            response = conn.auth.sign_in_with_password({"email": email, "password": password})
                            if response.user:
                                st.session_state.user = response.user
                                st.success("Logged in successfully!")
                                # Force refresh with delay to let session state settle
                                import time
                                time.sleep(1)  # 1 second delay
                                st.rerun()
                        else:
                            st.error("Login failed – check credentials.")
                    except Exception as e:
                        st.error(f"Login error: {str(e)}")

    with tab2:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pw")
        if st.button("Create Account"):
            try:
                conn.auth.sign_up({"email": email, "password": password})
                st.success("Account created. Check email to confirm.")
            except Exception as e:
                st.error(f"Sign-up error: {str(e)}")

# Create a Sale
elif page == "Create a Sale":
    if "user" not in st.session_state:
        st.warning("Please log in first")
    else:
        st.header("Create a New Claim Sale")

        title = st.text_input("Title (e.g. 2024 Topps Chrome Set)")
        grid_size = st.selectbox("Number of cards", [1, 2, 3, 4, 6, 9])
        hours = st.selectbox("Claim window (hours)", [24, 48, 72])
        price_per_card = st.number_input("Price per card ($)", min_value=0.01, step=0.01)

        image = st.file_uploader(f"Upload your {grid_size}-card grid image", type=["jpg", "png", "jpeg"])

        if st.button("Post Sale") and image and title:
            with st.spinner("Uploading and posting sale..."):
                try:
                    # Convert uploaded file to bytes
                    image_bytes = image.getvalue()

                    user_id = st.session_state.user.id
                    image_path = f"grids/{user_id}/{image.name}"
                    
                    # Upload to Supabase storage
                    conn.client.storage.from_("claimcards").upload(
                        image_path,
                        image_bytes,
                        {"content-type": image.type}
                    )
                    image_url = conn.client.storage.from_("claimcards").get_public_url(image_path)

                    # Create the post record
                    expiration = (datetime.now() + timedelta(hours=hours)).isoformat()
                    post_response = conn.table("posts").insert({
                        "user_id": user_id,
                        "title": title,
                        "image_url": image_url,
                        "claim_window_hours": hours,
                        "expiration": expiration,
                        "grid_size": grid_size,
                        "price_per_card": price_per_card
                    }).execute()

                    post_id = post_response.data[0]["id"]

                    # Create segments
                    for i in range(1, grid_size + 1):
                        conn.table("segments").insert({
                            "post_id": post_id,
                            "segment_number": i,
                            "claimed": False
                        }).execute()

                    st.success("Sale posted successfully!")
                    st.image(image_url, caption="Your uploaded grid")

                except Exception as e:
                    st.error(f"Error creating sale: {str(e)}")
# Browse Sales
elif page == "Browse Sales":
    st.header("Browse Sales")
    try:
        posts = conn.table("posts").select("*").execute().data or []
        if not posts:
            st.info("No sales yet.")
        for post in posts:
            st.subheader(post["title"])
            st.image(post["image_url"], use_column_width=True)
            st.write(f"Price per card: ${post['price_per_card']}")
            st.write(f"Expires: {post['expiration']}")
    except Exception as e:
        st.error(f"Load error: {str(e)}")