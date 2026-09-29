import os
import time
import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(page_title="Smart Frame Stylist", layout="centered", page_icon="👓")

st.title("👓 Smart Frame Stylist")
st.caption("AI-ಚಾಲಿತ ಫ್ರೇಮ್ ಶಿಫಾರಸು ಮತ್ತು ಟ್ರಯಲ್ ಅಸಿಸ್ಟೆಂಟ್")

api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key ನಮೂದಿಸಿ:", type="password")

if not api_key:
    st.warning("ದಯವಿಟ್ಟು Gemini API Key ನೀಡಿ.")
    st.stop()

client = genai.Client(api_key=api_key)

# 503 ದೋಷ ಬಂದರೆ ತನ್ನಷ್ಟಕ್ಕೆ ತಾನೇ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸುವ ಫಂಕ್ಷನ್
def call_gemini_safe(contents):
    # ಎರಡು ಲಭ್ಯವಿರುವ ಮಾಡೆಲ್‌ಗಳು
    models = ['gemini-2.5-flash', 'gemini-3.8-flash']
    for model_name in models:
        for attempt in range(3):  # 3 ಬಾರಿ ಪ್ರಯತ್ನಿಸುತ್ತದೆ
            try:
                return client.models.generate_content(
                    model=model_name,
                    contents=contents
                )
            except Exception as e:
                err_str = str(e)
                if "503" in err_str or "UNAVAILABLE" in err_str:
                    time.sleep(2)  # 2 ಸೆಕೆಂಡ್ ಕಾದು ಮತ್ತೆ ರನ್ ಮಾಡುತ್ತದೆ
                    continue
                else:
                    break
    # ಎಲ್ಲವೂ ವಿಫಲವಾದರೆ ಮಾತ್ರ ಕೊನೆಯ ಎರರ್
    raise Exception("ಸರ್ವರ್ ಅತ್ಯಂತ ಬ್ಯುಸಿಯಾಗಿದೆ, ದಯವಿಟ್ಟು 10 ಸೆಕೆಂಡ್ ನಂತರ ಮತ್ತೊಮ್ಮೆ ಕ್ಲಿಕ್ ಮಾಡಿ.")

tab1, tab2 = st.tabs([" ಹಂತ 1: ಮುಖದ ವಿಶ್ಲೇಷಣೆ & ಆಯ್ಕೆ", " ಹಂತ 2: ಟ್ರಯಲ್ ಫೋಟೋ ಹೋಲಿಕೆ"])

with tab1:
    st.subheader("ಗ್ರಾಹಕರ ವಿವರ ಮತ್ತು ಫೋಟೋ")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("ವಯಸ್ಸು (Age):", min_value=5, max_value=100, value=20)
        gender = st.selectbox("ಲಿಂಗ (Gender):", ["ಹೆಣ್ಣು (Female)", "ಗಂಡು (Male)", "ಇತರ (Other)"])
    with col2:
        profession = st.text_input("ಉದ್ಯೋಗ (Profession):", value="Engineering student")

    customer_photo = st.file_uploader("ಗ್ರಾಹಕರ ಫೋಟೋ ಅಪ್ಲೋಡ್ ಮಾಡಿ", type=["jpg", "png", "jpeg"], key="cust_face")

    if customer_photo:
        st.image(Image.open(customer_photo), caption="ಅಪ್ಲೋಡ್ ಮಾಡಿದ ಫೋಟೋ", width=250)

    if st.button("ಫ್ರೇಮ್ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ (Analyze)", type="primary"):
        if not customer_photo:
            st.error("ದಯವಿಟ್ಟು ಗ್ರಾಹಕರ ಫೋಟೋ ಅಪ್ಲೋಡ್ ಮಾಡಿ.")
        else:
            with st.spinner("AI ಪರಿಶೀಲಿಸುತ್ತಿದೆ, ದಯವಿಟ್ಟು ಕಾಯಿರಿ..."):
                try:
                    img = Image.open(customer_photo)
                    prompt = f"""
                    ನೀವು ಅನುಭವಿ ಆಪ್ಟೋಮೆಟ್ರಿಸ್ಟ್ ಮತ್ತು ಐವೇರ್ ಸ್ಟೈಲಿಸ್ಟ್.
                    ಗ್ರಾಹಕರ ವಿವರ:
                    - ವಯಸ್ಸು: {age}
                    - ಲಿಂಗ: {gender}
                    - ಉದ್ಯೋಗ: {profession}

                    ಕಾರ್ಯ:
                    1. ಮುಖದ ಆಕಾರ (Face Shape) ಮತ್ತು ಸ್ಕಿನ್ ಟೋನ್ (Skin Tone) ತಿಳಿಸಿ.
                    2. ಅವರ ಮುಖ ಮತ್ತು ಕೆಲಸಕ್ಕೆ ಸರಿಹೊಂದುವ 3 ಅತ್ಯುತ್ತಮ ಫ್ರೇಮ್ ಶೈಲಿಗಳನ್ನು (Shape, Color, Material) ಸೂಚಿಸಿ.
                    3. ಪ್ರತಿಯೊಂದಕ್ಕೂ ಕಾರಣ (Reasoning) ನೀಡಿ.
                    ಮಾಹಿತಿಯನ್ನು ಸ್ಪಷ್ಟವಾಗಿ ಕನ್ನಡದಲ್ಲೇ ನೀಡಿ.
                    """
                    
                    response = call_gemini_safe([img, prompt])
                    st.success("ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣಗೊಂಡಿದೆ!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"ದೋಷ: {e}")

with tab2:
    st.subheader("ಟ್ರಯಲ್ ಫ್ರೇಮ್‌ಗಳ ಹೋಲಿಕೆ")
    trial_photos = st.file_uploader("ಟ್ರಯಲ್ ಫೋಟೋಗಳು (ಗರಿಷ್ಠ 4):", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key="trials")

    if trial_photos:
        cols = st.columns(len(trial_photos))
        for idx, photo in enumerate(trial_photos):
            with cols[idx]:
                st.image(Image.open(photo), caption=f"ಆಯ್ಕೆ #{idx+1}", use_container_width=True)

    if st.button("ಯಾವುದು ಅತ್ಯುತ್ತಮ? (Find Best Fit)", type="primary"):
        if not trial_photos or len(trial_photos) < 2:
            st.error("ಕನಿಷ್ಠ 2 ಫೋಟೋಗಳನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ.")
        else:
            with st.spinner("AI ಬೆಸ್ಟ್ ಫ್ರೇಮ್ ಆಯ್ಕೆಮಾಡುತ್ತಿದೆ..."):
                try:
                    images_payload = [Image.open(p) for p in trial_photos]
                    compare_prompt = """
                    ಇಲ್ಲಿ ಗ್ರಾಹಕರು ವಿವಿಧ ಕನ್ನಡಕಗಳನ್ನು ಧರಿಸಿರುವ ಫೋಟೋಗಳಿವೆ.
                    ಮುಖದ ಅಗಲ, ಹುಬ್ಬು ಮತ್ತು ಕಣ್ಣಿನ ಸ್ಥಾನ ನೋಡಿ ಅತ್ಯುತ್ತಮವಾದ 1 ಫ್ರೇಮ್ ಯಾವುದು ಎಂದು ನೇರವಾಗಿ ತಿಳಿಸಿ ಕಾರಣ ನೀಡಿ.
                    """
                    response = call_gemini_safe(images_payload + [compare_prompt])
                    st.success("ಹೋಲಿಕೆ ಸಿದ್ಧವಾಗಿದೆ!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"ದೋಷ: {e}")
