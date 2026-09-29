import os
import io
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

# ಇಮೇಜ್ ಗಾತ್ರವನ್ನು ವೇಗವಾಗಿ ಕಳುಹಿಸಲು ಕಂಪ್ರೆಸ್ ಮಾಡುವ ಫಂಕ್ಷನ್ (Fast processing)
def prepare_image(uploaded_file):
    img = Image.open(uploaded_file)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    # ರೆಸಲ್ಯೂಶನ್ 800px ಗೆ ಇಳಿಸುವುದು - ಇದು ಅತಿ ವೇಗವಾಗಿ API ಗೆ ಹೋಗಲು ನೆರವಾಗುತ್ತದೆ
    img.thumbnail((800, 800))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=80)
    buffer.seek(0)
    return Image.open(buffer)

tab1, tab2 = st.tabs([" ಹಂತ 1: ಮುಖದ ವಿಶ್ಲೇಷಣೆ & ಆಯ್ಕೆ", " ಹಂತ 2: ಟ್ರಯಲ್ ಫೋಟೋ ಹೋಲಿಕೆ"])

# ----------------- ಹಂತ 1 -----------------
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
        st.image(customer_photo, caption="ಅಪ್ಲೋಡ್ ಮಾಡಿದ ಫೋಟೋ", width=250)

    if st.button("ಫ್ರೇಮ್ ಶಿಫಾರಸುಗಳನ್ನು ಪಡೆಯಿರಿ (Analyze)", type="primary"):
        if not customer_photo:
            st.error("ದಯವಿಟ್ಟು ಗ್ರಾಹಕರ ಫೋಟೋ ಅಪ್ಲೋಡ್ ಮಾಡಿ.")
        else:
            with st.spinner("AI ವಿಶ್ಲೇಷಿಸುತ್ತಿದೆ... (ಕೆಲವೇ ಸೆಕೆಂಡುಗಳು)"):
                try:
                    optimized_img = prepare_image(customer_photo)
                    prompt = f"""
                    ನೀವು ಅನುಭವಿ ಆಪ್ಟೋಮೆಟ್ರಿಸ್ಟ್ ಮತ್ತು ಐವೇರ್ ಸ್ಟೈಲಿಸ್ಟ್.
                    ಗ್ರಾಹಕ: ವಯಸ್ಸು {age}, {gender}, ವೃತ್ತಿ: {profession}.

                    ಕಾರ್ಯ:
                    1. ಮುಖದ ಆಕಾರ ಮತ್ತು ಸ್ಕಿನ್ ಟೋನ್ ತಿಳಿಸಿ.
                    2. ಅವರಿಗೆ ಸೂಕ್ತವಾದ 3 ಫ್ರೇಮ್ ಶೈಲಿಗಳನ್ನು (Shape, Color, Material) ಸೂಚಿಸಿ ಮತ್ತು ಸಂಕ್ಷಿಪ್ತವಾಗಿ ಕಾರಣ ನೀಡಿ.
                    ಮಾಹಿತಿಯನ್ನು ಕನ್ನಡದಲ್ಲೇ ಸ್ಪಷ್ಟ ಬುಲೆಟ್ ಪಾಯಿಂಟ್‌ಗಳಲ್ಲಿ ನೀಡಿ.
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=[optimized_img, prompt]
                    )
                    st.success("ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣಗೊಂಡಿದೆ!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"ದೋಷ: {e}")

# ----------------- ಹಂತ 2 -----------------
with tab2:
    st.subheader("ಟ್ರಯಲ್ ಫ್ರೇಮ್‌ಗಳ ಹೋಲಿಕೆ")
    trial_photos = st.file_uploader("ಟ್ರಯಲ್ ಫೋಟೋಗಳು (ಗರಿಷ್ಠ 4):", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key="trials")

    if trial_photos:
        cols = st.columns(len(trial_photos))
        for idx, photo in enumerate(trial_photos):
            with cols[idx]:
                st.image(photo, caption=f"ಆಯ್ಕೆ #{idx+1}", use_container_width=True)

    if st.button("ಯಾವುದು ಅತ್ಯುತ್ತಮ? (Find Best Fit)", type="primary"):
        if not trial_photos or len(trial_photos) < 2:
            st.error("ಕನಿಷ್ಠ 2 ಫೋಟೋಗಳನ್ನು ಅಪ್ಲೋಡ್ ಮಾಡಿ.")
        else:
            with st.spinner("AI ಅತ್ಯುತ್ತಮ ಫ್ರೇಮ್ ಆಯ್ಕೆಮಾಡುತ್ತಿದೆ..."):
                try:
                    optimized_list = [prepare_image(p) for p in trial_photos]
                    compare_prompt = """
                    ಇಲ್ಲಿ ಗ್ರಾಹಕರು ವಿವಿಧ ಕನ್ನಡಕಗಳನ್ನು ಧರಿಸಿರುವ ಫೋಟೋಗಳಿವೆ.
                    ಮುಖದ ಅಗಲ ಮತ್ತು ಕಣ್ಣಿನ ಸ್ಥಾನ ನೋಡಿ ಅತ್ಯುತ್ತಮವಾದ 1 ಫ್ರೇಮ್ ಯಾವುದು ಎಂದು ನೇರವಾಗಿ ತಿಳಿಸಿ ಕಾರಣ ನೀಡಿ.
                    """
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=optimized_list + [compare_prompt]
                    )
                    st.success("ಹೋಲಿಕೆ ಸಿದ್ಧವಾಗಿದೆ!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"ದೋಷ: {e}")
