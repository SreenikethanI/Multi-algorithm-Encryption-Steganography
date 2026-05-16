from pathlib import Path
import tempfile
from multi_algo_enc_stego import embed, extract
import streamlit as st

st.set_page_config(
    page_title="Data Obfuscation & Security",
    page_icon="🔐",
    layout="centered",
    menu_items={
        "Get Help": "https://github.com/SreenikethanI/Multi-algorithm-Encryption-Steganography/",
        "About": "This app demonstrates data obfuscation and security using multi-algorithm encryption and audio steganography. Developed by Sreenikethan Iyer.\n\nGitHub: https://github.com/SreenikethanI/Multi-algorithm-Encryption-Steganography/"
    }
)

PHASE_ENCODE_FREQ = 5000
CHUNK_SIZE = 1024
HOP_LENGTH = CHUNK_SIZE // 4
LSB_LAYERS = 1
ECC_LENGTH = 16

st.markdown("""
<style>
    /* Main Background */
    [data-testid="stAppViewContainer"] {
        background-color: #050810;
        background-image:
            linear-gradient(rgba(0, 255, 204, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 204, 0.05) 1px, transparent 1px);
        background-size: 35px 35px;
        background-position: center center;
    }

    /* Transparent Header */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(10, 15, 25, 0.8);
        border-radius: 8px;
        padding: 5px;
        border: 1px solid rgba(0, 255, 204, 0.2);
    }
    .stTabs [data-baseweb="tab"] {
        color: #a0aec0 !important;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        color: #00ffcc !important;
    }

    /* Inputs & Textareas */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: rgba(0, 0, 0, 0.6) !important;
        color: #00ffcc !important;
        border: 1px solid rgba(0, 255, 204, 0.3) !important;
        border-radius: 5px;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border: 1px solid #00ffcc !important;
        box-shadow: 0 0 5px rgba(0, 255, 204, 0.5) !important;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #00ffcc 0%, #0066ff 100%) !important;
        font-weight: 800 !important;
        border: none !important;
        box-shadow: 0 0 10px rgba(0, 255, 204, 0.4) !important;
        transition: 0.3s ease-in-out !important;
        border-radius: 6px;
        width: 100%;
    }
    .stButton>button p {
        color: #000000 !important;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.8) !important;
        transform: scale(1.02);
    }

    /* Drag & Drop Upload Box */
    [data-testid="stFileUploadDropzone"] {
        background-color: rgba(10, 20, 30, 0.7) !important;
        border: 2px dashed #00ffcc !important;
        border-radius: 10px;
        transition: all 0.3s;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        background-color: rgba(0, 255, 204, 0.1) !important;
        border-color: #ffffff !important;
    }

    /* Typography adjustments */
    h1, h2, h3, p, label {
        color: #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #00ffcc; font-size: 2.2rem;'>Data Obfuscation and Security</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #a0aec0; font-size: 1.1rem; margin-bottom: 2rem;'>using Multi-Algorithm Encryption and Audio Steganography</h3>", unsafe_allow_html=True)

tab1, tab2 = st.tabs([":material/encrypted_add_circle: Encode", ":material/encrypted_minus_circle: Decode"])

#region Tab 1: Encode
with tab1:
    st.write("[Click here](https://github.com/SreenikethanI/Multi-algorithm-Encryption-Steganography/tree/main/demo%20samples) to download a sample cover audio, for you to try out.")

    cover_audio = st.file_uploader("Upload cover audio (.wav only):", type=["wav"], key="cover")
    secret_text = st.text_area("Enter payload to obfuscate:")
    password = st.text_input("Encryption key / Password:", type="password", key="pass_embed")

    st.write("") # spacer
    if st.button("ENCODE", disabled=not (cover_audio and secret_text and password)):
        assert cover_audio is not None # for Typing purposes
        with st.spinner("Encoding...", show_time=True):

            # save uploaded audio to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_cover:
                temp_cover.write(cover_audio.read())
                temp_cover_path = Path(temp_cover.name)

            # create a temporary file for the output stego audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_stego:
                temp_stego_path = Path(temp_stego.name)

            try:
                embed(
                    plaintext=secret_text.encode("utf-8"),
                    k1=password.encode("utf-8"),
                    cover_audio_path=temp_cover_path,
                    output_path=temp_stego_path,
                    freq=PHASE_ENCODE_FREQ,
                    chunk_size=CHUNK_SIZE,
                    hop_length=HOP_LENGTH,
                    lsb_layers=LSB_LAYERS,
                    ecc_length=ECC_LENGTH,
                    debug_out=False
                )

                st.success(":material/check_circle: Payload successfully encrypted and embedded!")

                with temp_stego_path.open("rb") as f:
                    st.download_button(
                        label="Download (.wav)",
                        data=f,
                        file_name="stego_audio.wav",
                        mime="audio/wav"
                    )
            except Exception as e:
                st.error(":material/error: An error occurred. Please ensure your inputs are valid and try again.")
            finally:
                temp_cover_path.unlink(missing_ok=True)
                temp_stego_path.unlink(missing_ok=True)

#endregion

#region Tab 2: Decode
with tab2:
    stego_audio = st.file_uploader("Upload stego audio (.wav only):", type=["wav"], key="stego")
    password_ext = st.text_input("Decryption key / Password:", type="password", key="pass_ext")

    st.write("") # spacer
    if st.button("DECODE", disabled=not (stego_audio and password_ext)):
        assert stego_audio is not None # for Typing purposes
        with st.spinner("Decoding...", show_time=True):

            # save uploaded stego audio to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_stego:
                temp_stego.write(stego_audio.read())
                temp_stego_path = Path(temp_stego.name)

            try:
                extracted_bytes = extract(
                    stego_audio_path=temp_stego_path,
                    k1=password_ext.encode("utf-8"),
                    freq=PHASE_ENCODE_FREQ,
                    chunk_size=CHUNK_SIZE,
                    hop_length=HOP_LENGTH,
                    lsb_layers=LSB_LAYERS,
                    ecc_length=ECC_LENGTH,
                    debug_out=False
                )

                st.success(":material/check_circle: Payload successfully extracted and decrypted!")

                st.code(extracted_bytes.decode("utf-8", errors="ignore"), language="text")

            except ValueError:
                st.error(":material/error: Decoding failed, either due to invalid key or a corrupted audio file.")
            except Exception as e:
                st.error(":material/error: An error occurred. Please ensure your inputs are valid and try again.")
            finally:
                # clean up temp files
                temp_stego_path.unlink(missing_ok=True)

#endregion
