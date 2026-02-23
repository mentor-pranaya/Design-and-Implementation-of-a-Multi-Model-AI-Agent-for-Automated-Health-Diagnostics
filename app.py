import gradio as gr
import pandas as pd

from file_parser import parse_uploaded_file
from model import analyze_report, generate_summary
from gemini_agent import gemini_risk_analysis
from synthesis_agent import generate_final_health_report
from pdf_generator import generate_pdf
from qa_agent import ask_question_about_report


def full_analysis(report_file):
    if report_file is None:
        return None, None, None, " Please upload a blood report file.", None, None, 0, 0, 0, 0, 0, ""

    try:
        report_data = parse_uploaded_file(report_file)

        if not report_data:
            return None, None, None, " No parameters detected. Upload clearer PDF/image.", None, None, 0, 0, 0, 0, 0, ""

        # ---------------- MODEL 1 ----------------
        model1_analysis = analyze_report(report_data)
        model1_summary = generate_summary(model1_analysis)

        # Create a dataframe
        table_data = []
        for param, info in model1_analysis.items():
            table_data.append([
                param,
                info["value"],
                info["reference"],
                info["status"]
            ])

        df = pd.DataFrame(table_data, columns=["Parameter", "Tested Value", "Reference Range", "Status"])

        # ---------------- MODEL 2 ----------------
        model2_output = gemini_risk_analysis(model1_analysis)

        if "error" in model2_output:
            return model1_analysis, None, None, f" Gemini Error: {model2_output}", None, df, 0, 0, 0, 0, 0, ""

        risk_scores = model2_output.get("risk_scores", {})

        diabetes = risk_scores.get("diabetes", {}).get("score", 0)
        cardio = risk_scores.get("cardiovascular", {}).get("score", 0)
        kidney = risk_scores.get("kidney", {}).get("score", 0)
        liver = risk_scores.get("liver", {}).get("score", 0)
        anemia = risk_scores.get("anemia", {}).get("score", 0)

        risk_text = "## 🎯 Risk Score Dashboard\n\n"
        for risk_name, risk_info in risk_scores.items():
            risk_text += f"### {risk_name.upper()}\n"
            risk_text += f"- Score: **{risk_info.get('score')} / 100**\n"
            risk_text += f"- Level: **{risk_info.get('level')}**\n"
            risk_text += f"- Reason: {risk_info.get('reason')}\n\n"

        # ---------------- MODEL 3 ----------------
        final_report = generate_final_health_report(model1_analysis, model2_output)

        # ---------------- DISPLAY OUTPUT ----------------
        final_output = "## 📌 Model 1 Summary\n"
        final_output += f"**{model1_summary}**\n\n"

        final_output += "## 🧠 Model 2 Key Recommendations\n"
        for rec in model2_output.get("recommendations", []):
            final_output += f"- ✅ {rec}\n"

        final_output += "\n## 👨‍⚕️ Suggested Doctors\n"
        for doc in model2_output.get("doctor_suggestion", []):
            final_output += f"- 🩺 {doc}\n"

        final_output += "\n---\n"
        final_output += "⚠️ **Disclaimer:** AI analysis is for educational purposes only. Consult a doctor for medical advice."

        # Generate PDF
        pdf_path = generate_pdf(final_report)

        return (
            model1_analysis,
            model2_output,
            final_report,
            final_output,
            pdf_path,
            df,
            diabetes,
            cardio,
            kidney,
            liver,
            anemia,
            risk_text
        )

    except Exception as e:
        return None, None, None, f"❌ Error: {str(e)}", None, None, 0, 0, 0, 0, 0, ""


def question_answer(model1_data, model2_data, final_report, age, gender, lifestyle, symptoms, question):
    if not question:
        return "❌ Please type a question."

    if model1_data is None or model2_data is None or final_report is None:
        return "⚠️ Please analyze the report first."

    user_profile = {
        "age": age,
        "gender": gender,
        "lifestyle": lifestyle,
        "symptoms": symptoms
    }

    answer = ask_question_about_report(
        model1_data=model1_data,
        model2_data=model2_data,
        final_report=final_report,
        user_profile=user_profile,
        question=question
    )

    return f"## 🤖 AI Personalized Answer\n\n{answer}"


with gr.Blocks() as demo:
    gr.Markdown(
        """
        # 🧠 AI Blood Report Analyzer (Multi-Model AI Agent)

        Upload your blood report and get:
        ✅ Parameter Interpretation  
        ✅ Risk Score Dashboard  
        ✅ Personalized Recommendations  
        ✅ Downloadable PDF Report  
        ✅ Ask Questions About Report  
        """
    )

    model1_state = gr.State()
    model2_state = gr.State()
    final_report_state = gr.State()

    with gr.Tab("📄 Upload & Analyze"):
        report_file = gr.File(label="Upload Blood Report (PDF/Image/CSV/JSON)")
        analyze_btn = gr.Button("🚀 Analyze Report")

        output_markdown = gr.Markdown()
        model1_table = gr.Dataframe(label="📊 Extracted Parameter Table")

        pdf_download = gr.File(label="📥 Download PDF Report")

    with gr.Tab("📊 Risk Dashboard"):
        gr.Markdown("## Risk Scores (0-100)")

        diabetes_bar = gr.Slider(label="Diabetes Risk", minimum=0, maximum=100, interactive=False)
        cardio_bar = gr.Slider(label="Cardiovascular Risk", minimum=0, maximum=100, interactive=False)
        kidney_bar = gr.Slider(label="Kidney Risk", minimum=0, maximum=100, interactive=False)
        liver_bar = gr.Slider(label="Liver Risk", minimum=0, maximum=100, interactive=False)
        anemia_bar = gr.Slider(label="Anemia Risk", minimum=0, maximum=100, interactive=False)

        risk_explanation = gr.Markdown()

    with gr.Tab("🧾 Final Health Report"):
        final_report_box = gr.Textbox(lines=25, label="Final Synthesized Report")

    with gr.Tab("💬 Ask Questions"):
        gr.Markdown("### Ask personalized questions based on your age, gender and symptoms.")

        age_input = gr.Number(label="Age", value=25)
        gender_input = gr.Dropdown(["Male", "Female", "Other"], label="Gender", value="Male")
        lifestyle_input = gr.Textbox(label="Lifestyle (optional)", placeholder="Example: gym 4 days/week, smoker, alcohol occasionally")
        symptoms_input = gr.Textbox(label="Symptoms (optional)", placeholder="Example: fatigue, fever, headache")
        question_input = gr.Textbox(label="Ask your question", placeholder="Example: Is fasting sugar 141 dangerous for my age?")
        ask_btn = gr.Button("💡 Ask AI")

        answer_output = gr.Markdown()

    analyze_btn.click(
        fn=full_analysis,
        inputs=[report_file],
        outputs=[
            model1_state,
            model2_state,
            final_report_state,
            output_markdown,
            pdf_download,
            model1_table,
            diabetes_bar,
            cardio_bar,
            kidney_bar,
            liver_bar,
            anemia_bar,
            risk_explanation
        ]
    )

    # show final report in report tab too
    analyze_btn.click(
        fn=lambda x: x,
        inputs=[final_report_state],
        outputs=[final_report_box]
    )

    ask_btn.click(
        fn=question_answer,
        inputs=[
            model1_state, model2_state, final_report_state,
            age_input, gender_input, lifestyle_input, symptoms_input, question_input
        ],
        outputs=[answer_output]
    )

demo.launch(theme=gr.themes.Soft())

