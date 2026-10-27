import streamlit as st
import os
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from frontend.utils.api_client import APIClient
from frontend.components.sidebar import render_sidebar
from frontend.components.chat_view import render_chat_messages
from frontend.components.file_preview import render_artifact_download_card

# Page Configuration
st.set_page_config(
    page_title="Multimodal AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for seamless non-blinking UI and clean styling
st.markdown("""
<style>
    /* Prevent Streamlit darkening/blinking during interactions */
    .stApp {
        transition: none !important;
    }
    div[data-testid="stAppViewBlockContainer"] {
        opacity: 1 !important;
    }
    [data-testid="stStatusWidget"] {
        visibility: hidden;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 0.8rem;
    }
    .stDownloadButton button {
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "active_conv_id" not in st.session_state:
    st.session_state["active_conv_id"] = None
if "pending_image" not in st.session_state:
    st.session_state["pending_image"] = None
if "pending_audio" not in st.session_state:
    st.session_state["pending_audio"] = None

api_client = APIClient()

# Render Sidebar
sidebar_selections = render_sidebar(api_client)
active_conv_id = sidebar_selections.get("conversation_id")
attached_file_ids = sidebar_selections.get("attached_file_ids", [])
force_web_search = sidebar_selections.get("force_web_search")

# Main Header
st.title("🤖 Multimodal AI Chatbot")
st.caption("Ask questions, generate artwork, upload images or documents, create study notes, or chat for stress-relief.")

# Multimodal Attachment Bar (Expandable drawer)
with st.expander("📎 Attach Media (Image or Audio for Visual/Audio Analysis)", expanded=False):
    col_img, col_aud = st.columns(2)
    with col_img:
        img_file = st.file_uploader("Upload Image (PNG, JPG, WEBP)", type=["png", "jpg", "jpeg", "webp"], key="img_uploader")
        if img_file is not None:
            st.session_state["pending_image"] = {
                "bytes": img_file.getvalue(),
                "mime": img_file.type,
                "name": img_file.name
            }
            st.image(st.session_state["pending_image"]["bytes"], caption=f"Attached: {img_file.name}", width=200)

    with col_aud:
        aud_file = st.file_uploader("Upload Audio (WAV, MP3, M4A)", type=["wav", "mp3", "m4a"], key="aud_uploader")
        if aud_file is not None:
            st.session_state["pending_audio"] = {
                "bytes": aud_file.getvalue(),
                "mime": aud_file.type,
                "name": aud_file.name
            }
            st.audio(st.session_state["pending_audio"]["bytes"], format=aud_file.type)

# Active attachment summary
active_attachments = []
if st.session_state.get("pending_image"):
    active_attachments.append(f"🖼️ Image: {st.session_state['pending_image']['name']}")
if st.session_state.get("pending_audio"):
    active_attachments.append(f"🎙️ Audio: {st.session_state['pending_audio']['name']}")
if attached_file_ids:
    active_attachments.append(f"📑 {len(attached_file_ids)} Document(s) Selected")

if active_attachments:
    st.info("Active with next message: " + " • ".join(active_attachments))

# Render Message History
render_chat_messages(st.session_state["messages"], api_client)

# Chat Input Box
user_prompt = st.chat_input("Type your message (e.g. 'Generate an image of a cosmic nebula', 'Create notes on DBMS', 'Feeling stressed')...")

if user_prompt:
    # 1. Extract and consume pending media
    img_data = st.session_state.get("pending_image")
    aud_data = st.session_state.get("pending_audio")
    
    img_bytes = img_data["bytes"] if img_data else None
    img_mime = img_data["mime"] if img_data else None
    aud_bytes = aud_data["bytes"] if aud_data else None
    aud_mime = aud_data["mime"] if aud_data else None

    # Reset pending attachments for subsequent messages
    st.session_state["pending_image"] = None
    st.session_state["pending_audio"] = None

    # 2. Add and display user message immediately
    user_meta = {
        "has_image": bool(img_bytes),
        "has_audio": bool(aud_bytes),
        "attached_files_count": len(attached_file_ids)
    }
    user_msg_dict = {
        "role": "user",
        "content": user_prompt,
        "metadata": user_meta
    }
    st.session_state["messages"].append(user_msg_dict)
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_prompt)
        if img_bytes:
            st.image(img_bytes, width=250)
        if aud_bytes:
            st.audio(aud_bytes)

    # 3. Call Backend API and display assistant response without darkening rerun
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Processing multimodal context, RAG & response..."):
            resp = api_client.send_chat(
                message=user_prompt,
                conversation_id=active_conv_id,
                file_ids=attached_file_ids,
                image_bytes=img_bytes,
                image_mime=img_mime,
                audio_bytes=aud_bytes,
                audio_mime=aud_mime,
                enable_web_search=force_web_search,
                enable_rag=True
            )

        if "error" in resp:
            st.error(resp["error"])
        else:
            ans_text = resp.get("response", "")
            conv_id = resp.get("conversation_id")
            st.session_state["active_conv_id"] = conv_id

            meta_data = {
                "citations": resp.get("citations", []),
                "web_sources": resp.get("web_sources", []),
                "artifacts": resp.get("artifacts", []),
                "emotional_support_active": resp.get("emotional_support_active", False)
            }

            # Render content
            if meta_data.get("emotional_support_active"):
                st.caption("💚 *Empathetic Support Mode Active*")
            st.markdown(ans_text)

            # Render Citations if any
            citations = meta_data.get("citations", [])
            if citations:
                with st.expander(f"📚 Retrieved Document Sources ({len(citations)})", expanded=False):
                    for c in citations:
                        st.markdown(f"**{c.get('filename')}** (Chunk {c.get('chunk_index')}) — *Score: {c.get('score')}*")
                        st.caption(c.get("snippet", ""))

            # Render Web Sources if any
            web_sources = meta_data.get("web_sources", [])
            if web_sources:
                with st.expander(f"🌐 Web Search References ({len(web_sources)})", expanded=False):
                    for w in web_sources:
                        st.markdown(f"[{w.get('title')}]({w.get('url')})")
                        st.caption(w.get("snippet", ""))

            # Render Artifacts (Generated Images, Documents)
            artifacts = meta_data.get("artifacts", [])
            if artifacts:
                for art in artifacts:
                    render_artifact_download_card(art, api_client)

            # Store in session state
            asst_msg_dict = {
                "role": "assistant",
                "content": ans_text,
                "metadata": meta_data
            }
            st.session_state["messages"].append(asst_msg_dict)
