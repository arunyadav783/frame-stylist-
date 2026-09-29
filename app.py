import os
import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(page_title="Smart Frame Stylist", layout="centered", page_icon="👓")

st.title("👓 Smart Frame Stylist")
st.caption("AI-ಚಾಲಿತ ಫ್ರೇಮ್ ಶಿಫಾರಸು ಮತ್ತು ಟ್ರಯಲ್ ಅಸಿಸ್ಟೆಂಟ್")

# API Key ಅನ್ನು Render Environment Variables ನಿಂದ ಪಡೆಯುವುದು
api_key = os.environ.get("GEMINI_API_KEY", "")

if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key ನಮೂದಿಸಿ:", type="password")

if not api_key:
    st.warning("ದಯವಿಟ್ಟು ಮುಂದುವರಿಯಲು Google Gemini API Key ನೀಡಿ.")
    st.stop()

client = genai.Client(api_key=api_key)

tab1, tab2 = st.tabs([" ಹಂತ 1: ಮುಖದ ವಿಶ್ಲೇಷಣೆ & ಆಯ್ಕೆ", " ಹಂತ 2: ಟ್ರಯಲ್ ಫೋಟೋ ಹೋಲಿಕೆ"])

with tab1:
    st.subheader("ಗ್ರಾಹಕರ ವಿವರ ಮತ್ತು ಫೋಟೋ")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("ವಯಸ್ಸು (Age):", min_value=5, max_value=100, value=28)
        gender = st.selectbox("ಲಿಂಗ (Gender):", ["ಗಂಡು (Male)", "ಹೆಣ್ಣು (Female)", "ಇತರ (Other)"])
    with col2:
        profession = st.text_input("ಉದ್ಯೋಗ (Profession):", placeholder="ಉದಾ: ಸಾಫ್ಟ್‌ವೇರ್ ಇಂಜಿನಿಯರ್, ಟೀಚರ್...")

    customer_photo = st.file_uploader("ಗ್ರಾಹಕರ ಫೋಟೋ ಅಪ್ಲೋಡ್ ಮಾಡಿ (Face Photo)", type=["jpg", "png", "jpeg"], key="cust_face")

    if customer_photo:
        st.image(Image.open(customer_photo), caption="ಅಪ್ಲೋಡ್ ಮಾಡಿದ ಫೋಟೋ", width=250)

    if st.button("ಫ್ರೇಮ್ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ (Analyze)", type="primary"):
        if not customer_photo:
            st.error("ದಯವಿಟ್ಟು ಗ್ರಾಹಕರ ಫೋಟೋ ಅಪ್ಲೋಡ್ ಮಾಡಿ.")
        else:
            with st.spinner("AI ಮುಖದ ಆಕಾರ ಮತ್ತು ಸ್ಕಿನ್ ಟೋನ್ ವಿಶ್ಲೇಷಿಸುತ್ತಿದೆ..."):
                try:
                    img = Image.open(customer_photo)
                    prompt = f"""
                    ನೀವು ಅನುಭವಿ ಆಪ್ಟೋಮೆಟ್ರಿಸ್ಟ್ ಮತ್ತು ಐವೇರ್ ಸ್ಟೈಲಿಸ್ಟ್.
                    ಗ್ರಾಹಕರ ವಿವರ:
                    - ವಯಸ್ಸು: {age}
                    - ಲಿಂಗ: {gender}
                    - ಉದ್ಯೋಗ: {profession}

                    ಕಾರ್ಯ:
                    1. ಫೋಟೋ ನೋಡಿ ಮುಖದ ಆಕಾರ (Face Shape) ಮತ್ತು ಸ್ಕಿನ್ ಟೋನ್ (Skin Tone) ನಿಖರವಾಗಿ ತಿಳಿಸಿ.
                    2. ಅವರ ಉದ್ಯೋಗ ಮತ್ತು ಮುಖಲಕ್ಷಣಗಳಿಗೆ ಹೊಂದುವಂತೆ 3 ವಿಭಿನ್ನ ಅತ್ಯುತ್ತಮ ಫ್ರೇಮ್ ಆಯ್ಕೆಗಳನ್ನು (Frame Shape, Material, Color Palette) ಸೂಚಿಸಿ.
                    3. ಪ್ರತಿಯೊಂದು ಫ್ರೇಮ್ ಆಯ್ಕೆಗೂ ವಿವರವಾದ ಕಾರಣ (Reasoning) ನೀಡಿ.
                    ಮಾಹಿತಿಯನ್ನು ಸ್ಪಷ್ಟವಾಗಿ ಕನ್ನಡದಲ್ಲೇ ಬುಲೆಟ್ ಪಾಯಿಂಟ್ಸ್ ರೂಪದಲ್ಲಿ ನೀಡಿ.
                    """
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[img, prompt]
                    )
                    st.success("ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣಗೊಂಡಿದೆ!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"ದೋಷ ಸಂಭವಿಸಿದೆ: {e}")

with tab2:
    st.subheader("ಟ್ರಯಲ್ ಫ್ರೇಮ್‌ಗಳ ಹೋಲಿಕೆ")
    st.write("ಗ್ರಾಹಕರು ವಿವಿಧ ಕನ್ನಡಕಗಳನ್ನು ಹಾಕಿಕೊಂಡಿರುವ 3 ಅಥವಾ 4 ಫೋಟೋಗಳನ್ನು ಒಟ್ಟಿಗೆ ಅಪ್ಲೋಡ್ ಮಾಡಿ.")

    trial_photos = st.file_uploader(
        "ಟ್ರಯಲ್ ಫೋಟೋಗಳನ್ನು ಆಯ್ಕೆಮಾಡಿ (ಗರಿಷ್ಠ 4):",
        type=["jpg", "png", "jpeg"],
        accept_multiple_files=True,
        key="trials"
    )

    if trial_photos:
        cols = st.columns(len(trial_photos))
        for idx, photo in enumerate(trial_photos):
            with cols[idx]:
                st.image(Image.open(photo), caption=f"ಆಯ್ಕೆ #{idx+1}", use_container_width=True)

    if st.button("ಯಾವುದು ಅತ್ಯುತ್ತಮ? (Find Best Fit)", type="primary"):
        if not trial_photos or len(trial_photos) < 2:
            st.error("ದಯವಿಟ್ಟು ಹೋಲಿಕೆ ಮಾಡಲು ಕನಿಷ್ಠ 2 ಅಥವಾ 3-4 ಫೋಟೋಗಳನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ.")
        else:
            with st.spinner("AI ಎಲ್ಲಾ ಫೋಟೋಗಳನ್ನು ಹೋಲಿಸಿ ಬೆಸ್ಟ್ ಫ್ರೇಮ್ ಆಯ್ಕೆಮಾಡುತ್ತಿದೆ..."):
                try:
                    images_payload = [Image.open(p) for p in trial_photos]
                    compare_prompt = f"""
                    ಇಲ್ಲಿ ಗ್ರಾಹಕರು ವಿವಿಧ ಕನ್ನಡಕಗಳನ್ನು ಧರಿಸಿರುವ ಒಟ್ಟು {len(trial_photos)} ಫೋಟೋಗಳಿವೆ.
                    ಕಾರ್ಯ:
                    1. ಪ್ರತಿಯೊಂದು ಫ್ರೇಮ್ ಅವರ ಮುಖದ ಅಗಲ, ಕಣ್ಣಿನ ಸ್ಥಾನ, ಮತ್ತು ಹುಬ್ಬುಗಳ ರೇಖೆಗೆ ಹೇಗೆ ಹೊಂದಿಕೆಯಾಗುತ್ತದೆ ಎಂದು ಪರೀಕ್ಷಿಸಿ.
                    2. ಈ ಎಲ್ಲದರಲ್ಲಿ 'ಅತ್ಯುತ್ತಮವಾದ 1 ಫ್ರೇಮ್ (Single Best Fit)' ಯಾವುದು ಎಂದು ನೇರವಾಗಿ ಘೋಷಿಸಿ.
                    3. ಕಾರಣವನ್ನು ಸ್ಪಷ್ಟವಾಗಿ ಕನ್ನಡದಲ್ಲಿ ತಿಳಿಸಿ.
                    """
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=images_payload + [compare_prompt]
                    )
                    st.success("ಹೋಲಿಕೆ ಸಿದ್ಧವಾಗಿದೆ!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"ದೋಷ ಸಂಭವಿಸಿದೆ: {e}")
