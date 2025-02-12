import streamlit as st
import streamlit.components.v1 as components
import openai
from openai import OpenAI  # OpenAI 클래스 가져오기
import pandas as pd
import json
import plotly.express as px
from prompts import *

# 📌 답변 초기화
is_answer = [True, True, True, True]

# 📌 Mermaid 다이어그램 생성 함수
def mermaid(code):
    """ Mermaid 다이어그램을 렌더링하는 함수 """
    components.html(
        f"""
        <div style="width:100%; overflow:auto;">
            <pre class="mermaid" style="height:auto; min-height:500px; max-height:1000px;">
                {code}
            </pre>
        </div>
        <script type="module">
            import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
            mermaid.initialize({{ startOnLoad: true, theme: "dark" }});
        </script>
        """,
        height=800,
    )

# 📌 OpenAI 응답 처리 함수 (GPT)
# @st.cache_data # 캐시 데이터 사용
def get_gpt_response(model, prompt, stream=False):
    # 세션에서 API 키 유지
    api_key = st.session_state.get("openai_api_key", "")
    
    if not api_key:
        st.error("🚨 OpenAI API 키가 입력되지 않았습니다!")
        return None
    
    # OpenAI 클라이언트 객체 생성
    client = OpenAI(api_key=api_key)

    # OpenAI GPT 모델을 호출하는 함수
    response = client.chat.completions.create(
        model=model,
        messages=prompt,
        stream=stream
    )
    return response


# 📌 Streamlit UI 설정
st.set_page_config(page_title="Dream Trip - Uway AI 진로 검사", layout="wide", page_icon="⭐️")
st.markdown(
    """
    <style>
        .main-header {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            color: #4CAF50;
            margin-bottom: 20px;
        }
        .info-box {
            background-color: #f9f9f9;
            color: #333;
            padding: 30px;
            border-radius: 10px;
            font-size: 18px;
            text-align: center;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <div class='info-box'>
        <h2>🔥너의 미래를 바꿀 가장 강력한 기회! 🔥</h2>
        <p>진로 목표 설정부터 맞춤형 가이드까지! <br>AI가 분석한 최적의 커리어 루트를 확인하고 한 걸음 먼저 나아가 보세요. 🚀</p>
    </div>
    """,
    unsafe_allow_html=True
)
st.header("Dream Trip ✈️✨", divider="rainbow")
st.info("진로 설정 → AI 맞춤 분석 → 목표 달성까지! 단 1분!\n\n네가 가야 할 길을 빠르게 탐색해보세요.", icon="✅")

# 📌 Sidebar (사용자 입력)
with st.sidebar:
    st.header("Uway - Dream Trip ✈️", divider="rainbow")

    # api session 입력 정보
    openai.api_key = st.text_input(label='OpenAI API KEY', placeholder='OpenAI API Key를 입력해주세요.', value='',type='password')
    if openai.api_key:
        st.session_state["openai_api_key"] = openai.api_key
    st.markdown("---")

    # 사용자 입력 폼
    with st.form("parameters-form"):
        st.subheader("사용자 정보")
        name = st.text_input("이름")
        job = st.text_input("희망 직업")
        age = st.slider("나이", 10, 20, 17, 1)
        col1, col2 = st.columns([1, 5])
        with col1:
            st.write("성별")
        with col2:
            gender = st.radio("", ["남성", "여성"], horizontal=True)
        school = st.selectbox("학교", ["중학교", "고등학교", "대학교"], index=1)
        mbti = st.selectbox("MBTI", [
            "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP",
            "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"])
        language = st.selectbox("언어설정", ["대한민국", "English", "日本", "中國"])

        # 버튼 스타일 적용
        st.markdown("""
            <style>
                div[data-testid="stForm"] button {
                    width: 100% !important;
                    height: 50px !important;
                    font-size: 16px !important;
                    font-weight: bold !important;
                    background-color: #ff4b4b !important;
                    color: white !important;
                    border-radius: 10px !important;
                    border: none !important;
                }
                div[data-testid="stForm"] button:hover {
                    background-color: #ff7878 !important;
                }
            </style>
        """, unsafe_allow_html=True)

        submit = st.form_submit_button("진로 여행 시작하기")


# 📌 OpenAI 프롬프트 초기 설정
gpt_prompt = [{"role": "system", "content": system_prompt}]


# 📌 사용자 입력 처리
if submit and name and job:
    new_gpt_prompt = gpt_prompt.copy()
    new_user_prompts = user_prompts.copy()

    # 🚀 1단계: 꿈의 여행지
    if is_answer[0]:
        st.subheader(f"{name}님의 꿈을 향한 맞춤 여행지 🌈", divider=True)
        answer1 = st.empty()

        with st.spinner("꿈으로 향하는 여행지 티켓을 발행 중이에요..."):
            new_gpt_prompt.append({
                "role": "user",
                "content": new_user_prompts[0] % (name, age, gender, job, school, language, mbti)
            })

            # ✅ `stream=True` 사용하여 스트리밍 응답 처리
            gpt_response1 = get_gpt_response("gpt-4o-mini", new_gpt_prompt, stream=True)

            collected_messages = []
            full_response = ""

            for chunk in gpt_response1:
                if isinstance(chunk, tuple):  # 🔥 튜플인 경우 첫 번째 요소 사용
                    chunk = chunk[0]

                if hasattr(chunk, "choices") and hasattr(chunk.choices[0], "delta") and hasattr(chunk.choices[0].delta, "content"):
                    content = chunk.choices[0].delta.content
                    if content is not None:  # 🔥 None 값 방지
                        collected_messages.append(content)
                    full_response = "".join(collected_messages)

                    # ✅ 실시간으로 UI 업데이트
                    answer1.markdown(f"🤖 {full_response}")

            new_gpt_prompt.append({"role": "assistant", "content": full_response})
            

    # 🚀 2단계: 꿈으로 가는 로드맵
    if is_answer[1]:
        st.subheader(f"{name}님의 꿈으로 향하는 로드맵 🗺️🌟", divider=True)
        with st.spinner("꿈으로 향하는 로드맵을 그리는 중이에요..."):
            new_gpt_prompt.append({
                "role": "user",
                "content": new_user_prompts[1] % (name, age, gender, job, school, language, mbti),
            })

            gpt_response2 = get_gpt_response("gpt-4o-mini", new_gpt_prompt, stream=False)
            gpt_response2 = gpt_response2.choices[0].message.content

            # Mermaid 다이어그램 파싱 및 렌더링
            start_keyword, end_keyword = "```mermaid", "```"
            if start_keyword in gpt_response2 and end_keyword in gpt_response2:
                mermaid_content = gpt_response2.split(start_keyword)[-1].split(end_keyword)[0].strip()
            else:
                mermaid_content = gpt_response2

            mermaid(mermaid_content)


    # 🚀 3단계: 직업 분석 결과
    if is_answer[2]:
        st.subheader(f"AI가 분석한 {job} 🔍👨‍💼", divider=True)
    with st.spinner("꿈으로 향하는 능력치를 계산하는 중이에요..."):
        new_gpt_prompt.append({"role": "user", "content": new_user_prompts[2]})

        gpt_response3 = get_gpt_response("gpt-4o-mini", new_gpt_prompt, stream=False)

        if not gpt_response3 or not gpt_response3.choices or not gpt_response3.choices[0].message.content:
            st.error("❌ OpenAI 응답이 비어 있습니다. 다시 시도해주세요.")
        else:
            gpt_response3 = gpt_response3.choices[0].message.content

            try:
                # 🔍 JSON 부분만 추출 (응답 내 텍스트 제거)
                json_start = gpt_response3.find("{")
                json_end = gpt_response3.rfind("}") + 1
                json_data = gpt_response3[json_start:json_end]

                list_content = json.loads(json_data)

                # 🔍 'score' 키 확인 후 변환
                if "score" not in list_content:
                    st.error("❌ OpenAI 응답에서 'score' 데이터가 없습니다.")
                    st.write("🔍 OpenAI 응답 (디버깅):", list_content)
                else:
                    df = pd.DataFrame({
                        "r": list_content["score"],
                        "theta": ["직업적합도", "난이도", "소요비용", "소요기간", "예상수입", "업무강도"]
                    })
                    fig = px.line_polar(df, r="r", theta="theta", line_close=True)
                    fig.update_traces(fill="toself")
                    st.write(fig)
                    st.markdown(list_content["description"])

            except json.JSONDecodeError as e:
                st.error(f"❌ JSON 변환 실패: {e}")
                st.write("🔍 OpenAI 응답 내용:", gpt_response3)  # 디버깅 출력


    # 🚀 4단계: AI가 그린 미래 모습
    if is_answer[3]:
        st.subheader(f"AI가 그린 {name}님의 미래 모습 🤖🔮", divider=True)
        with st.spinner("미래의 당신을 그리는 중이에요..."):
            # 세션에서 API 키 유지
            api_key = st.session_state.get("openai_api_key", "")
            if not api_key:
                st.error("🚨 OpenAI API 키가 입력되지 않았습니다!")

            # OpenAI 클라이언트 객체 생성
            client = OpenAI(api_key=api_key)

            # DALL-E 이미지 생성
            dalle_response = client.images.generate(
                prompt = (
                    f"A cartoon-style illustration of a person working as a {job}. The character is {gender} and is depicted in a lively, expressive manner. The background includes relevant elements that represent their profession, creating a visually engaging scene."
                )
            )
            st.image(dalle_response.data[0].url)

    st.button("친구에게 공유하기")