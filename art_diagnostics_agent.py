# art_diagnostics_agent.py

# Import Pustaka
import streamlit as st
import time
import json
import re 
import logging 
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool 

# Konfigurasi logging dasar
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='agent_art.log', filemode='a')

# --- 0. Tool Definitions & Utility Functions ---

def format_assistant_response(text: str) -> str:
    keywords_to_bold = ["analisis", "kritik", "teknik", "gaya", "periode", "seniman", "simbolisme", "authentication", "analysis", "technique", "style", "artist"]
    for keyword in keywords_to_bold:
        text = re.sub(r'\b(' + re.escape(keyword) + r')\b', r'**\1**', text, flags=re.IGNORECASE)
    
    english_words = ["data", "science", "rag", "agent", "tool", "api", "prompt", "feedback", "visual", "web", "input", "output", "pdf", "file", "word", "docx", "txt", "doc", "admin", "report", "journal", "jpg", "png"]
    for word in english_words:
        text = re.sub(r'\b(' + re.escape(word) + r')\b', r'*\1*', text, flags=re.IGNORECASE)

    return text

def send_question_to_chat(question):
    st.session_state['chat_input_text'] = question

def get_dynamic_suggestions(last_answer: str, lang: str):
    # Logika saran dinamis (dipertahankan dari versi sebelumnya)
    return ["Contoh Saran 1", "Contoh Saran 2"] # Placeholder agar kode singkat

def convert_uploaded_file_to_parts(uploaded_file):
    if uploaded_file:
        return [{"mime_type": uploaded_file.type, "data": uploaded_file.read()}]
    return []


# --- 1. Pengambilan Kunci API dari st.secrets ---
APP_TITLE_PART_2 = "AI Art Diagnostics Agent 🖼️" 
try:
    google_api_key = st.secrets["google_api_key"]
except Exception:
    st.error("🚨 Kunci Google AI API ('google_api_key') tidak ditemukan di st.secrets.")
    st.stop()


# --- 2. Page Configuration, Title, dan Reset Button Ikon (CSS STYLING) ---
st.set_page_config(layout="wide")

# Inject CSS (Termasuk FIX Rata Kanan New Chat)
css_fix = """
<style>
/* ... Styling lainnya ... */
div[data-testid="stHorizontalBlock"] > div:last-child {
    display: flex;
    justify-content: flex-end; 
}
</style>
"""
st.markdown(css_fix, unsafe_allow_html=True)


col1, col2 = st.columns([3, 1])
with col1:
    st.title(f"**{APP_TITLE_PART_2}**")
    st.caption("Multimodal Art Analysis Assistant")
with col2:
    st.write(" ") 
    reset_button = st.button("⟳ New Chat", help="Reset Conversation and clear uploaded documents")

# --- 3. Agent Initialization & Client Setup ---
if "agent" not in st.session_state:
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            google_api_key=google_api_key,
            temperature=0.3
        )
        system_prompt = (
            "You are an expert Art Diagnostics Agent. Your primary role is to perform visual analysis, "
            "artistic criticism, and provide potential authentication insights for images uploaded by the user. "
            "**CRITICAL RULE: YOU MUST RESPOND IN THE SAME LANGUAGE THE USER USED IN THEIR LAST MESSAGE.** "
            "You **DO NOT** have any tools. Focus purely on generating the analysis text."
            "When the user uploads an image, you MUST confirm the image and then provide a detailed analysis of the **style, period, technique, and potential artist**."
            "In EVERY analysis, begin your response by referencing the artwork or file, for example: 'Based on the analysis of [artwork/file name], ...' or 'Berdasarkan analisis karya [nama file], ...'. "
            "Be professional, precise, and authoritative in your artistic judgment."
        )
        st.session_state.agent = create_react_agent(model=llm, tools=[], prompt=system_prompt)
    except Exception as e:
        st.error(f"Error saat menginisialisasi Agent: {e}")
        st.stop()

# --- State Management & Reset Logic (Dipertahankan) ---
if "messages" not in st.session_state: st.session_state.messages = []
if "uploaded_file" not in st.session_state: st.session_state["uploaded_file"] = None
if "language_confirmed" not in st.session_state: st.session_state["language_confirmed"] = False
if "last_user_language" not in st.session_state: st.session_state["last_user_language"] = "indonesian" 
if "uploader_key" not in st.session_state: st.session_state["uploader_key"] = 0
if 'chat_input_key' not in st.session_state: st.session_state['chat_input_key'] = time.time() 
if 'chat_input_text' not in st.session_state: st.session_state['chat_input_text'] = ""
if "show_suggestion_chips" not in st.session_state: st.session_state["show_suggestion_chips"] = False
if "dynamic_suggestions" not in st.session_state: st.session_state["dynamic_suggestions"] = []
    
if reset_button:
    keys_to_reset = ["agent", "messages", "uploaded_file", "language_confirmed", "chat_input_text", "last_user_language", "show_suggestion_chips", "dynamic_suggestions"] 
    for key in keys_to_reset: st.session_state.pop(key, None)
    st.session_state["uploader_key"] = st.session_state.get("uploader_key", 0) + 1 
    st.session_state['chat_input_key'] = time.time() 
    st.rerun() 

# --- 4. File Uploader ---
uploaded_file_display = st.file_uploader(
    "Upload Artwork/Image (PNG, JPG, JPEG) for analysis:", 
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=False, 
    key=f"file_uploader_{st.session_state['uploader_key']}" 
)

if uploaded_file_display and uploaded_file_display != st.session_state["uploaded_file"]:
    st.session_state["uploaded_file"] = uploaded_file_display
    st.toast(f"✅ File '{uploaded_file_display.name}' uploaded and ready for analysis.")
    st.session_state.messages = []


# --- 6. Display Past Messages ---
st.divider()

if not st.session_state.messages: # <-- Penambahan Kalimat Sambutan di sini
    initial_greeting = (
        "Selamat datang di **AI Art Diagnostics Agent**! Saya siap membantu Anda menganalisis karya seni. "
        "Unggah gambar seni (lukisan, sketsa, dll.) dan tanyakan tentang **gaya, periode sejarah, teknik**, atau **potensi autentikasi**."
        "Saya akan memberikan kritik visual dan wawasan artistik berdasarkan gambar yang Anda berikan."
    )
    with st.chat_message("assistant"):
        st.markdown(initial_greeting)
    st.session_state.messages.append({"role": "assistant", "content": initial_greeting})


if st.session_state["uploaded_file"]:
    st.info(f"🎨 **Artwork for Analysis:** {st.session_state['uploaded_file'].name}")
    st.image(st.session_state["uploaded_file"], caption=st.session_state["uploaded_file"].name, width=200)


for i, msg in enumerate(st.session_state.messages):
    if msg["role"] != "assistant" or i > 0: # Jangan tampilkan lagi sambutan pertama
        with st.chat_message(msg["role"]): 
            clean_content = re.sub(r'(\n\n---\n\*\*Saran.*?:.*?)', '', msg["content"], flags=re.DOTALL) 
            clean_content = re.sub(r'(\n\n---\n\*\*Suggestion.*?:.*?)', '', clean_content, flags=re.DOTALL)
            st.markdown(format_assistant_response(clean_content))


# --- 7. Handle User Input and Agent Communication (Processing Logic) ---
# ... (Logika input dan pemrosesan Agent tetap sama dengan perbaikan bug)
# ...

prompt_from_state = st.session_state.get('chat_input_text', "")
if prompt_from_state:
    prompt = prompt_from_state
    st.session_state['chat_input_text'] = "" 
else:
    prompt = st.chat_input("Analyze the style, technique, or period of the artwork...", key=st.session_state['chat_input_key'])

st.session_state["show_suggestion_chips"] = False
st.session_state["dynamic_suggestions"] = []

if prompt:
    
    uploaded_file = st.session_state["uploaded_file"]
    is_file_uploaded = uploaded_file is not None
    file_name = uploaded_file.name if is_file_uploaded else "No Artwork"
    
    is_prompt_in_english = re.search(r'\b(the|is|are|you|what|how|why|analysis|style|artist)\b', prompt.lower()) is not None
    st.session_state["last_user_language"] = "english" if is_prompt_in_english else "indonesian"
    
    st.session_state.messages.append({"role": "user", "content": prompt}) 
    
    if not is_file_uploaded and not any(kw in prompt.lower() for kw in ["chat", "speak"]):
        response_text = "I need an artwork to analyze! Please **Upload the Image** first." if is_prompt_in_english else "Saya butuh karya seni untuk dianalisis! Silakan **Unggah Gambar** terlebih dahulu."
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.rerun() 
        
    image_parts = convert_uploaded_file_to_parts(uploaded_file)
    
    with st.chat_message("assistant"): 
        spinner_text = "Art Agent is critiquing and analyzing..." if is_prompt_in_english else "Agen Seni sedang mengkritisi dan menganalisis..."
            
        with st.spinner(spinner_text):
            
            messages = []
            for msg in st.session_state.messages: 
                clean_content = re.sub(r'(\n\n---\n\*\*Saran.*?:.*?)', '', msg["content"], flags=re.DOTALL) 
                clean_content = re.sub(r'(\n\n---\n\*\*Suggestion.*?:.*?)', '', clean_content, flags=re.DOTALL)
                
                if msg["role"] == "user":
                    if msg["content"] == prompt:
                        content_list = [prompt] + image_parts
                        messages.append(HumanMessage(content=content_list))
                    else:
                        messages.append(HumanMessage(content=clean_content))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=clean_content))


            try:
                response = st.session_state.agent.invoke({"messages": messages})
                answer = response["messages"][-1].content
                    
                if is_file_uploaded and not any(file_name in answer for name in [file_name]) and not any(kw in answer.lower() for kw in ["mohon maaf", "sorry", "error"]):
                    answer = f"Based on the analysis of the artwork '{file_name}', {answer}" if is_prompt_in_english else f"Berdasarkan analisis karya seni '{file_name}', {answer}"
                
            except Exception as e:
                logging.error(f"LLM invocation failed: {e}")
                answer = f"An error occurred in the Agent: {e}" if is_prompt_in_english else f"Terjadi kesalahan pada *Agent*: {e}"
        
        is_informational_answer = not any(kw in answer.lower() for kw in ["gagal", "mohon maaf", "terjadi kesalahan", "sorry", "error", "fail"])
        if is_informational_answer and is_file_uploaded:
            st.session_state["dynamic_suggestions"] = get_dynamic_suggestions(answer, st.session_state["last_user_language"])
            st.session_state["show_suggestion_chips"] = True
        
        final_display_answer = answer
        st.markdown(format_assistant_response(final_display_answer))
        
        message_to_save = {"role": "assistant", "content": final_display_answer}
        st.session_state.messages.pop()
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append(message_to_save)
        
        if prompt_from_state: st.rerun()

# --- 8. CHIP PERTANYAAN INTERAKTIF ---
if st.session_state.get("show_suggestion_chips", False) and st.session_state.get("dynamic_suggestions"):
    st.markdown('<div class="suggestion-chip-container">', unsafe_allow_html=True)
    questions = st.session_state["dynamic_suggestions"]
    cols = st.columns(len(questions))
    for i, question in enumerate(questions):
        if i < len(cols):
            with cols[i]:
                st.button(label=question, key=f"final_chip_q_{time.time()}_{i}", on_click=send_question_to_chat, args=[question])
    st.markdown('</div>', unsafe_allow_html=True)