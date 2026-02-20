import requests
import streamlit as st


DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"


st.set_page_config(page_title="Health Report AI", layout="wide")

if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "report" not in st.session_state:
    st.session_state.report = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


st.title("Health Report AI")

backend_url = st.sidebar.text_input("Backend URL", DEFAULT_BACKEND_URL)


def _render_report(report: dict) -> None:
    if not report:
        st.info("No report available yet. Upload a file to start analysis.")
        return

    st.subheader("Summary")
    st.write(report.get("summary", ""))

    st.subheader("Risks")
    risks = report.get("risks", [])
    if not risks:
        st.write("No elevated risks detected.")
    else:
        for risk in risks:
            domain = risk.get("domain", "unknown")
            level = risk.get("risk_level", "")
            severity = risk.get("severity_score")
            if severity not in (None, ""):
                st.write(f"- {domain}: {level} (severity {severity})")
            else:
                st.write(f"- {domain}: {level}")

    st.subheader("Recommendations")
    recs = report.get("recommendations", [])
    if not recs:
        st.write("No recommendations were generated.")
    else:
        for rec in recs:
            st.write(f"- {rec}")

    st.subheader("Disclaimer")
    st.write(report.get("disclaimer", ""))


with st.expander("Upload and Analyze", expanded=True):
    col1, col2 = st.columns([2, 1])

    with col1:
        upload_file = st.file_uploader(
            "Upload a report (PDF, JPG, PNG, JSON)",
            type=["pdf", "jpg", "jpeg", "png", "json"],
        )

    with col2:
        age = st.number_input("Age", min_value=0, max_value=120, value=0, step=1)
        gender = st.selectbox("Gender", options=["", "female", "male", "other"])

    medical_history = st.text_area("Medical history", placeholder="e.g., hypertension")
    lifestyle = st.text_area("Lifestyle", placeholder="e.g., sedentary, smoker")

    analyze_clicked = st.button("Analyze Report", type="primary")

    if analyze_clicked:
        if upload_file is None:
            st.error("Please upload a report file.")
        else:
            with st.spinner("Analyzing report..."):
                files = {
                    "file": (
                        upload_file.name,
                        upload_file.getvalue(),
                        upload_file.type or "application/octet-stream",
                    )
                }
                data = {}
                if age:
                    data["age"] = str(age)
                if gender:
                    data["gender"] = gender
                if medical_history:
                    data["medical_history"] = medical_history
                if lifestyle:
                    data["lifestyle"] = lifestyle

                try:
                    response = requests.post(
                        f"{backend_url}/analyze",
                        files=files,
                        data=data,
                        timeout=120,
                    )
                    payload = response.json()
                except requests.RequestException as exc:
                    st.error(f"Request failed: {exc}")
                else:
                    if payload.get("status") != "success":
                        st.error(payload.get("error") or "Analysis failed.")
                    else:
                        data = payload.get("data", {})
                        st.session_state.session_id = data.get("session_id")
                        st.session_state.report = data.get("report")
                        st.session_state.chat_history = []
                        st.success("Report analyzed successfully.")


st.divider()

_render_report(st.session_state.report or {})

st.divider()

st.subheader("Chat")
if st.session_state.session_id is None:
    st.info("Analyze a report to start chatting.")
else:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input("Ask about risks, recommendations, or severity")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        f"{backend_url}/chat",
                        json={
                            "session_id": st.session_state.session_id,
                            "message": prompt,
                        },
                        timeout=60,
                    )
                    payload = response.json()
                except requests.RequestException as exc:
                    st.error(f"Chat request failed: {exc}")
                else:
                    answer = payload.get("answer", "No response received.")
                    confidence = payload.get("confidence", "unknown")
                    st.write(f"{answer}\n\nConfidence: {confidence}")
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": f"{answer}\n\nConfidence: {confidence}"}
                    )
