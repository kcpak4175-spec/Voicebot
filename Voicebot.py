import streamlit as st
from audiorecorder import audiorecorder
from google import genai
import os
from datetime import datetime
from gtts import gTTS
import base64
import io
import time
import sys

# [중요] FFmpeg 경로 수동 지정 (에러 방지용)
# 만약 여전히 FFmpeg 에러가 난다면 아래 주석을 풀고 실제 경로를 입력하세요.
# from pydub import AudioSegment
# AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"

##### 기능 구현 함수 #####

def STT_and_Ask(audio_data, client, model_name):
    """음성을 텍스트로 변환하고 Gemini에 질문하여 답변을 받습니다."""
    temp_audio_path = None
    uploaded_file = None
    
    try:
        audio_bio = io.BytesIO()
        audio_data.export(audio_bio, format="mp3")
        audio_bytes = audio_bio.getvalue()
        
        temp_audio_path = f"temp_audio_{int(time.time())}.mp3"
        with open(temp_audio_path, "wb") as f:
            f.write(audio_bytes)
        
        uploaded_file = client.files.upload(file=temp_audio_path)
        
        while uploaded_file.state == "PROCESSING":
            time.sleep(1)
            uploaded_file = client.files.get(name=uploaded_file.name)
        
        if uploaded_file.state == "FAILED":
            raise ValueError("파일 업로드 실패")
        
        prompt = "이 음성을 듣고 질문을 텍스트로 요약한 뒤, 그에 대한 답변을 한국어로 작성해줘. 형식: [질문 요약: ...] [답변: ...]. 답변은 25단어 내외로 짧게 해줘."
        
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, uploaded_file]
        )
        
        return response.text if response and response.text else "응답을 받지 못했습니다."
            
    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg.upper() or "api key" in error_msg.lower():
            return None, "❌ API 키가 유효하지 않습니다. 다시 확인해주세요."
        elif "quota" in error_msg.lower():
            return None, "❌ API 할당량을 초과했습니다. 잠시 후 다시 시도해주세요."
        elif "404" in error_msg or "not found" in error_msg.lower():
            return None, f"❌ 모델을 찾을 수 없습니다: {model_name}\n\n올바른 모델 이름인지 확인해주세요."
        elif "permission" in error_msg.lower() or "403" in error_msg:
            return None, "❌ API 키 권한이 부족합니다. API 키 설정을 확인해주세요."
        else:
            return None, f"❌ 오류가 발생했습니다: {error_msg}"
    
    finally:
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        if uploaded_file:
            try: client.files.delete(name=uploaded_file.name)
            except: pass

def parse_response(response_text):
    """Gemini 응답에서 질문과 답변을 분리합니다."""
    try:
        if "[질문 요약:" in response_text and "[답변:" in response_text:
            question = response_text.split("[질문 요약:")[1].split("]")[0].strip()
            answer = response_text.split("[답변:")[1].split("]")[0].strip()
            return question, answer
    except:
        pass
    return "음성 질문", response_text

def TTS(text):
    """텍스트를 음성으로 변환하여 재생합니다."""
    filename = f"output_{int(time.time())}.mp3"
    try:
        if text and not text.startswith("❌"):
            tts = gTTS(text=text, lang="ko")
            tts.save(filename)
            with open(filename, "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                md = f'<audio autoplay="True"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
                st.markdown(md, unsafe_allow_html=True)
    finally:
        if os.path.exists(filename):
            time.sleep(1) # 재생 시간을 벌어주기 위해 살짝 대기
            os.remove(filename)

##### 메인 UI 함수 #####
def main():
    st.set_page_config(page_title="Gemini 음성 비서", layout="wide")

    if "chat" not in st.session_state:
        st.session_state["chat"] = []
    if "check_reset" not in st.session_state:
        st.session_state["check_reset"] = False
    if "play_tts" not in st.session_state:
        st.session_state["play_tts"] = False

    st.header("🎙️ 관철's Gemini 음성 비서")
    st.markdown("---")

    with st.sidebar:
        st.subheader("⚙️ 설정")
        api_key = st.text_input("GEMINI API 키 입력", placeholder="AIza...", type="password")

        if api_key:
            st.success("API 키 입력됨 ✅")
        
        st.markdown("[🔗 Gemini API 키 발급/확인](https://aistudio.google.com/welcome)")
        
        st.markdown("---")

        model_options = {
            "Gemini 2.0 Flash (권장)": "gemini-2.0-flash-exp",
            "Gemini 1.5 Flash": "gemini-1.5-flash",
            "Gemini 1.5 Pro": "gemini-1.5-pro"
        }
        selected_model = st.radio("모델 선택", options=list(model_options.keys()))
        model_id = model_options[selected_model]
        
        if st.button("🔄 대화 기록 초기화", use_container_width=True):
            st.session_state["chat"] = []
            st.session_state["check_reset"] = True
            st.rerun()

    if not api_key:
        st.warning("⚠️ 사이드바에서 API 키를 입력해 주세요.")
        st.info("💡 Google AI Studio에서 무료로 API 키를 발급받을 수 있습니다.")        
        return

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"❌ 클라이언트 초기화 실패: {str(e)}")
        st.info("💡 API 키를 확인해주세요.")
        return

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎤 질문하기")
        audio = audiorecorder("🎤 클릭하여 녹음 시작/종료", "🛑 녹음 중... 다시 클릭하세요")
        
        if len(audio) > 0:
            if not st.session_state["check_reset"]:
                st.audio(audio.export().read())
                if st.button("🚀 Gemini에게 질문하기", use_container_width=True):
                    with st.spinner("🤔 Gemini 분석 중..."):
                        response_text = STT_and_Ask(audio, client, model_id)
                        question, answer = parse_response(response_text)
                        now = datetime.now().strftime("%H:%M")
                        st.session_state["chat"].append(("user", now, question))
                        st.session_state["chat"].append(("bot", now, answer))
                        st.session_state["play_tts"] = True
                        st.rerun()
            else:
                st.session_state["check_reset"] = False

    with col2:
        st.subheader("💬 대화 기록")
        for sender, time_str, message in st.session_state["chat"]:
            if sender == "user":
                st.write(f'<div style="display:flex;align-items:center;margin-bottom:10px;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time_str}</div></div>', unsafe_allow_html=True)
            else:
                st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;margin-bottom:10px;"><div style="font-size:0.8rem;color:gray;margin-right:8px;">{time_str}</div><div style="background-color:#E9E9EB;border-radius:12px;padding:8px 12px;color:black;max-width:80%;">{message}</div></div>', unsafe_allow_html=True)
        
        if st.session_state["play_tts"] and st.session_state["chat"]:
            TTS(st.session_state["chat"][-1][2])
            st.session_state["play_tts"] = False

# [독립 실행 로직] 터미널에서 'python app.py'로 직접 실행 가능하게 함
if __name__ == "__main__":
    import subprocess
    if "streamlit" in sys.modules:
        main()
    else:
        # 이 파일 자체를 스트림릿으로 재실행함

        subprocess.run(["streamlit", "run", sys.argv[0]])
