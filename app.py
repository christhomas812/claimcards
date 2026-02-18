import streamlit as st
import os
from datetime import datetime, timedelta
import stripe
import requests
from PIL import Image

# ────────────────────────────────────────────────
# Safety check (keep this forever - it's small)
# ────────────────────────────────────────────────
if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
    st.error("Supabase secrets missing - check Settings → Secrets in Manage app")
    st.stop()

# Connect to Supabase
from st_supabase_connection import SupabaseConnection
conn = st.connection("supabase", type=SupabaseConnection)

st.set_page_config(page_title="ClaimCards", layout="wide")

# Sidebar navigation
page = st.sidebar.selectbox("Go to", ["Home", "Login / Sign Up", "Create a Sale", "Browse Sales"])

# ────────────────────────────────────────────────
# Home
# ────────────────────────────────────────────────
if page == "Home":
    st.title("Welcome to ClaimCards")
    st.markdown("""
    Buy and sell trading cards using interactive claim grids!
    
    - Log in to create or claim cards
    - Browse open sales below
    """)

# ────────────────────────────────────────────────
# Login / Sign Up
# ────────────────────────────────────────────────
elif page == "Login / Sign Up":
    st.header("Login / Sign Up")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

  with tab1:
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_pw")
    
    if st.button("Login"):
        if not email or not password:
            st.warning("Please enter both email and password.")
        else:
            with st.spinner("Logging in..."):
                try:
                    response = conn.auth.sign_in_with_password({"email": email, "password": password})
                    
                    if response.user:
                        st.session_state.user = response.user
                        st.success("Logged in successfully!")
                        
                        # Force page refresh after a tiny delay (fixes rerun timing issue)
                        import time
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Login failed – check your email and password.")
                
                except Exception as e:
                    st.error(f"Login error: {str(e)}")
                    st.info("Tip: Make sure your account is confirmed (check email/spam).")

    with tab2:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pw")
        if st.button("Create Account"):
            try:
                conn.auth.sign_up({"email": email, "password": password})
                st.success("Account created! Check your email to confirm (including spam folder).")
            except Exception as e:
                st.error(f"Sign-up error: {str(e)}")

# ────────────────────────────────────────────────
# Create a Sale
# ────────────────────────────────────────────────
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
            with st.spinner("Uploading image and creating sale..."):
                try:
                    # Upload image using conn.client.storage
                    user_id = st.session_state.user.id
                    image_path = f"grids/{user_id}/{image.name}"
                    conn.client.storage.from_("claimcards").upload(image_path, image.getbuffer(), {"content-type": image.type})
                    image_url = conn.client.storage.from_("claimcards").get_public_url(image_path)

                    # Create post
                    expiration = (datetime.now() + timedelta(hours=hours)).isoformat()
                    post = conn.table("posts").insert({
                        "user_id": user_id,
                        "title": title,
                        "image_url": image_url,
                        "claim_window_hours": hours,
                        "expiration": expiration,
                        "grid_size": grid_size,
                        "price_per_card": price_per_card
                    }).execute()

                    post_id = post.data[0]["id"]

                    # Create segments
                    for i in range(1, grid_size + 1):
                        conn.table("segments").insert({
                            "post_id": post_id,
                            "segment_number": i,
                            "claimed": False
                        }).execute()

                    st.success("Sale posted successfully!")
                    st.image(image_url, caption="Your grid")
                except Exception as e:
                    st.error(f"Error creating sale: {str(e)}")
# ────────────────────────────────────────────────
# Browse Sales (simple version - we'll improve later)
# ────────────────────────────────────────────────
elif page == "Browse Sales":
    st.header("Browse Open Sales")

    try:
        posts = conn.table("posts").select("*").execute().data or []
        if not posts:
            st.info("No sales yet. Be the first to create one!")
        for post in posts:
            st.subheader(post["title"])
            st.image(post["image_url"], use_column_width=True)
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
            with st.spinner("Uploading image and creating sale..."):
                try:
                    # Upload image
                    user_id = st.session_state.user.id
                    image_path = f"gr
            grid_size = post["grid_size"]
            cols_per_row = min(3, grid_size)
            rows = (grid_size + cols_per_row - 1) // cols_per_row

            for r in range(rows):
                cols = st.columns(cols_per_row)
                for c in range(cols_per_row):
                    seg_num = r * cols_per_row + c + 1
                    if seg_num > grid_size:
                        break
                    with cols[c]:
                        seg = conn.table("segments").select("*").eq("post_id", post["id"]).eq("segment_number", seg_num).single().execute().data
                        if seg["claimed"]:
                            st.button(f"#{seg_num} Claimed", disabled=True)
                        else:
                            if st.button(f"Claim #{seg_num} - ${post['price_per_card']}"):
                                st.info("Claim logic coming soon")
                            if st.button(f"Offer on #{seg_num}"):
                                st.info("Offer logic coming soon")
    except Exception as e:
        st.error(f"Error loading sales: {str(e)}")