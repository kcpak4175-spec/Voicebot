# Gemini VoiceBot (관철's Gemini 음성 비서)
write. kcpak

Google Gemini AI를 활용하여 음성으로 질문하고 답변을 들을 수 있는 스마트 음성 비서 웹 애플리케이션입니다. Streamlit을 기반으로 구축되었으며 음성 녹음, STT(Speech-to-Text), LLM(Gemini) 분석, TTS(Text-to-Speech) 기능을 통합하여 제공합니다.

🔗 [Live Demo 보러가기](https://voicebot-krwytikesjawztniaot7hf.streamlit.app/)

🚀 기술 스택 (Tech Stack)
- **Framework**: Streamlit
- **Language**: Python 3.x
- **AI Models**: Google Gemini (2.0 Flash, 1.5 Flash, 1.5 Pro)
- **Voice Library**: 
  - `streamlit-audiorecorder` (음성 녹음)
  - `gTTS` (Google Text-to-Speech)
  - `pydub` (오디오 데이터 처리)
- **API**: Google GenAI SDK

✨ 주요 기능 (Key Features)
- **음성 인식 및 질문 요약 (STT)**
  - 마이크를 통해 실시간으로 음성을 녹음하고 mp3 파일로 변환
  - Gemini의 멀티모달 기능을 활용하여 음성을 직접 분석하고 질문 요약 도출
- **스마트 답변 생성 (AI Assistant)**
  - Google Gemini 모델을 활용하여 질문에 대한 명확하고 짧은 한국어 답변 생성
  - 최신 Gemini 2.0 Flash 익스피리먼트 모델 지원
- **음성 답변 재생 (TTS)**
  - 생성된 텍스트 답변을 `gTTS`를 통해 음성으로 변환하여 자동 재생
- **대화 기록 관리**
  - 사용자 질문과 AI 답변을 메신저 UI 형태로 시각화
  - 세션 기반 대화 기록 저장 및 초기화 기능 제공
- **사용자 친화적 설정**
  - 사이드바를 통한 간편한 API 키 설정 및 모델 선택 기능

💻 로컬 개발 환경 설정 (Getting Started)
프로젝트를 로컬 환경에서 실행하려면 다음 단계를 따르세요.

1. **레포지토리 클론**
   ```bash
   git clone https://github.com/asia-voicebot/voicebot.git
   cd voicebot
   ```

2. **패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

3. **FFmpeg 설치 (필요시)**
   음성 처리를 위해 `FFmpeg`가 시스템에 설치되어 있어야 합니다.
   - Windows: [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)에서 다운로드 후 환경 변수 등록
   - macOS: `brew install ffmpeg`

4. **애플리케이션 실행**
   ```bash
   streamlit run Voicebot.py
   ```
   브라우저에서 `http://localhost:8501` 접속하여 확인합니다.

🌐 배포 가이드 (Deployment)
이 프로젝트는 Streamlit Cloud에 최적화되어 있습니다.

1. GitHub 레포리지토리에 코드를 푸시합니다.
2. [Streamlit Cloud](https://share.streamlit.io/)에 접속하여 레포지토리를 연결합니다.
3. **Main file path**를 `Voicebot.py`로 설정합니다.
4. **Deploy** 버튼을 누릅니다.

> [!IMPORTANT]
> **API 키 설정 가이드**
> - 이 서비스를 이용하려면 [Google AI Studio](https://aistudio.google.com/welcome)에서 발급받은 Gemini API 키가 필요합니다.
> - 실행 후 웹 화면의 왼쪽 사이드바에 해당 키를 입력해야 정상적으로 기능이 작동합니다.
