import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from PIL import Image
import io
import base64

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="AI-Powered Tutor",
    layout="centered",
)

# ---------- CUSTOM THEME WITH DARKER PASTELS & CUSTOM STYLES ----------
st.markdown("""
    <style>
        /* Background color of the page */
        .stApp {
            background-color: #e6f2ff;  /* Soft blue-gray */
            color: #333333;
        }

        /* Customize select boxes and input boxes */
        div[data-baseweb="select"] > div {
            background-color: #cce0ff !important;
            color: #000000 !important; /* text inside select boxes */
            border-radius: 8px;
        }

        /* Customize labels for select boxes and input fields */
        label {
            color: #000000 !important;  /* Black labels */
            font-weight: bold;
            font-size: 18px !important;
        }

        /* Customize text inputs (the question box) */
        textarea {
            background-color: #cce0ff !important; /* Box color */
            color: #000000 !important;            /* Text inside the box */
            border-radius: 8px !important;
            padding: 10px !important;
            font-size: 16px !important;
        }

        /* File uploader */
        .stFileUploader {
            background-color: #cce0ff;
            border-radius: 8px;
        }

        /* Buttons */
        .stButton > button {
            background-color: #99b3ff;
            color: #333333;
            font-weight: bold;
            border-radius: 10px;
            padding: 0.5em 1em;
            border: 1px solid #666;
            transition: background-color 0.3s ease;
        }

        .stButton > button:hover {
            background-color: #809fff;
            color: #000000;
        }

        /* Info/warning/success messages */
        .stAlert {
            background-color: #ffd699;
            color: #333333;
        }

        /* Markdown header text */
        h1, h2, h3 {
            color: #333333;
        }

        /* Footer text */
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            text-align: center;
            color: #333333;
            padding: 10px 0;
            font-size: 14px;
        }

        /* Custom label for the question area */
        .question-label {
            color: #000000 !important; /* Pure black */
            font-weight: bold;
            font-size: 18px !important;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- GOOGLE API KEY ----------
GOOGLE_API_KEY = "AIzaSyBtZCzwHfujo3yevV5yc7GO8bLM1-Q7MFA"
genai.configure(api_key=GOOGLE_API_KEY)

# ---------- INITIALIZATION ----------
recognizer = sr.Recognizer()

# ---------- FUNCTIONS ----------
def get_voice_input():
    with sr.Microphone() as source:
        st.info("🎙️ Listening... Speak now.")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            st.success(f"✅ You said: {text}")
            return text
        except sr.UnknownValueError:
            st.error("❗ Sorry, I couldn't understand what you said.")
            return None
        except sr.RequestError:
            st.error("❗ Could not request results. Check your internet.")
            return None

def get_ai_response(question, grade, subject, image_data=None):
    model_name = "models/gemini-1.5-flash-latest"
    model = genai.GenerativeModel(model_name)

    full_prompt = (
        f"You are a helpful tutor for grade {grade} students in {subject}.\n"
        f"Explain in simple terms.\n"
        f"Question: {question}"
    )

    contents = [{"role": "user", "parts": [{"text": full_prompt}]}]

    if image_data:
        contents[0]["parts"].append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": image_data
            }
        })

    response = model.generate_content(contents=contents)
    return response.text

# ---------- STREAMLIT UI ----------

# Welcome Heading
st.markdown("<h1 style='text-align: center; color: #333333;'>👋 Welcome to the AI Tutor</h1>", unsafe_allow_html=True)
st.title("🎓 AI-Powered Tutor")
st.markdown("Ask anything in **Math**, **Physics**, or **Chemistry** for your grade!")

# --- Language Select ---
language = st.selectbox("🌐 Choose Language:", ["English", "Hindi", "Telugu"])

# --- Grade & Subject Select ---
grades_list = [str(grade) for grade in range(1, 13)]  # Grade 1 to 12
grade = st.selectbox("🎓 Select Grade/Level:", grades_list)
subject = st.selectbox("📚 Choose Subject:", ["Mathematics", "Physics", "Chemistry"])

# --- Image Upload ---
uploaded_file = st.file_uploader("📤 Upload an image (optional):", type=["jpg", "jpeg", "png"])
image_base64 = None

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    if image.mode != 'RGB':
        image = image.convert('RGB')

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    image_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

# --- Text Area for Questions ---
st.markdown("<label class='question-label'>✏️ Type your question:</label>", unsafe_allow_html=True)
txt_input = st.text_area(
    "",
    height=150,
    placeholder="Type your question here..."
)

# ---------- Buttons ----------
col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Get Answer"):
        if txt_input:
            st.info("💡 Fetching answer from AI Tutor...")
            answer = get_ai_response(txt_input, grade, subject, image_base64)
            st.subheader("✅ AI Answer:")
            st.write(answer)
        else:
            st.warning("⚠️ Please enter a question!")

with col2:
    if st.button("🎙️ Speak & Get Answer"):
        voice_question = get_voice_input()

        if voice_question:
            st.info("💡 Fetching answer from AI Tutor...")
            answer = get_ai_response(voice_question, grade, subject, image_base64)
            st.subheader("✅ AI Answer:")
            st.write(answer)

# ---------- Footer ----------
st.markdown("""
    <div class="footer">
        Developed by BhanuTeja ❤️ 
    </div>
""", unsafe_allow_html=True)
