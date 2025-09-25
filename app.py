import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
import re
import io
import matplotlib.pyplot as plt


# --- Configure Tesseract if needed ---
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# --- Fake detection scoring function ---
def score_profile(profile):
    score = 0
    reasons = []

    # Rule 1: Follower/Following ratio
    if profile["following"] > 0:
        ratio = profile["followers"] / profile["following"]
        if ratio < 0.1:
            score += 2
            reasons.append("Suspicious follower/following ratio")

    # Rule 2: Few posts
    if profile["posts"] < 5:
        score += 2
        reasons.append("Very few posts")

    # Rule 3: No profile picture
    if profile["profile_pic"].lower() == "no":
        score += 2
        reasons.append("No profile picture")

    # Rule 4: Empty bio
    if not profile["bio_text"] or len(str(profile["bio_text"]).strip()) < 10:
        score += 1
        reasons.append("Empty or too short bio")

    return score, reasons


# --- Sidebar for mode selection ---
st.sidebar.title("🕵 Fake Profile Detector")
mode = st.sidebar.radio(
    "Choose detection mode:",
    ("CSV Upload", "Manual Input", "Username/Link Input", "Screenshot Upload")
)

st.title("🕵 Fake Profile Detector")

# ====================
# MODE 1: CSV Upload
# ====================
if mode == "CSV Upload":
    st.header("📂 Upload CSV of Profiles")

    # --- Create a sample CSV ---
    sample_data = pd.DataFrame({
        "username": ["john_doe", "spam_account123", "coolgirl99", "fakebot01", "nature_lover"],
        "followers": [150, 5, 2000, 12, 340],
        "following": [100, 600, 500, 2000, 150],
        "posts": [50, 1, 120, 0, 35],
        "bio_text": [
            "Love photography and travel.",
            "",
            "Fashion | Lifestyle | Blogger",
            "Click this link to win $$$",
            "Sharing my hiking adventures."
        ],
        "profile_pic": ["yes", "no", "yes", "no", "yes"]
    })

    # Convert DataFrame to CSV in memory
    csv_buffer = io.StringIO()
    sample_data.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode()

    # Download button
    st.download_button(
        label="⬇ Download Sample CSV",
        data=csv_bytes,
        file_name="sample_profiles.csv",
        mime="text/csv"
    )

    # --- Upload section ---
    uploaded_file = st.file_uploader("Or upload your own CSV file", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("### Uploaded Profiles")
        st.dataframe(df)

        results = []
        labels = []
        for _, row in df.iterrows():
            score, reasons = score_profile(row)
            results.append({"username": row["username"], "score": score, "reasons": reasons})
            labels.append("Suspicious" if score >= 4 else "Normal")

        st.write("### Detection Results")
        for r in results:
            st.subheader(r["username"])
            st.write(f"Score: {r['score']}")
            for reason in r["reasons"]:
                st.write("- " + reason)
            if r["score"] >= 4:
                st.error("🚨 Suspicious account")
            else:
                st.success("✅ Looks normal")

        # --- Chart visualization ---
        st.write("### 📊 Summary Visualization")

        summary = pd.Series(labels).value_counts()

        fig, ax = plt.subplots()
        summary.plot(kind="bar", ax=ax)
        ax.set_title("Suspicious vs Normal Accounts")
        ax.set_ylabel("Number of Accounts")
        ax.set_xlabel("Category")
        st.pyplot(fig)


# ====================
# MODE 2: Manual Input
# ====================
elif mode == "Manual Input":
    st.header("✍ Manually Enter Profile Info")

    with st.form("manual_form"):
        username = st.text_input("Username")
        followers = st.number_input("Followers", min_value=0, step=1)
        following = st.number_input("Following", min_value=0, step=1)
        posts = st.number_input("Posts", min_value=0, step=1)
        bio_text = st.text_area("Bio")
        profile_pic = st.radio("Profile Picture?", ["yes", "no"])

        submitted = st.form_submit_button("Check Profile")

    if submitted:
        profile = {
            "username": username,
            "followers": followers,
            "following": following,
            "posts": posts,
            "bio_text": bio_text,
            "profile_pic": profile_pic
        }

        score, reasons = score_profile(profile)

        st.subheader(f"Results for {username}")
        st.write(f"Score: {score}")
        for reason in reasons:
            st.write("- " + reason)

        if score >= 4:
            st.error("🚨 Suspicious account")
        else:
            st.success("✅ Looks normal")


# ====================
# MODE 3: Username/Link Input
# ====================
elif mode == "Username/Link Input":
    st.header("🔗 Test by Username/Link")

    username = st.text_input("Enter a profile username or link")
    if st.button("Check Profile"):
        if username:
            # Mock profile (replace with real API calls if available)
            fake_profile = {
                "username": username,
                "followers": 10,
                "following": 500,
                "posts": 1,
                "bio_text": "",
                "profile_pic": "no"
            }

            score, reasons = score_profile(fake_profile)

            st.subheader(f"Results for {username}")
            st.write(f"Score: {score}")
            for reason in reasons:
                st.write("- " + reason)

            if score >= 4:
                st.error("🚨 Suspicious account")
            else:
                st.success("✅ Looks normal")
        else:
            st.warning("Please enter a username or link")


# ====================
# MODE 4: Screenshot Upload
# ====================
elif mode == "Screenshot Upload":
    st.header("🖼 Upload Profile Screenshot")

    uploaded_img = st.file_uploader("Upload profile screenshot", type=["jpg", "jpeg", "png"])

    if uploaded_img:
        image = Image.open(uploaded_img)
        st.image(image, caption="Uploaded Profile", use_column_width=True)

        extracted_text = pytesseract.image_to_string(image)
        st.subheader("Extracted Text")
        st.text(extracted_text)

        score = 0
        reasons = []

        # Rule 1: Few posts
        if re.search(r"0 posts|1 post", extracted_text.lower()):
            score += 2
            reasons.append("Very few posts detected")

        # Rule 2: Followers
        match_followers = re.search(r"(\d+)\s*followers", extracted_text.lower())
        if match_followers:
            followers = int(match_followers.group(1))
            if followers < 50:
                score += 2
                reasons.append("Very few followers")

        # Rule 3: Following
        match_following = re.search(r"(\d+)\s*following", extracted_text.lower())
        if match_following:
            following = int(match_following.group(1))
            if following > 1000 and (match_followers and followers < 50):
                score += 2
                reasons.append("Follows many accounts but has few followers")

        # Rule 4: Empty bio
        if "bio" not in extracted_text.lower() and len(extracted_text.strip()) < 30:
            score += 1
            reasons.append("Bio seems empty or missing")

        st.subheader("Fake Profile Score")
        st.write(f"Score: {score}")

        for r in reasons:
            st.write("- " + r)

        if score >= 4:
            st.error("🚨 Suspicious account")
        else:
            st.success("✅ Looks normal")