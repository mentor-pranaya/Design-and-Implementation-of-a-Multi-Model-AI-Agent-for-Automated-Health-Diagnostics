import gradio as gr
from file_parser import parse_uploaded_file
from model import compare_report_with_normals, generate_summary


def analyze_files(report_file, normal_file):
    if report_file is None or normal_file is None:
        return "Please upload both files."

    try:
        report_data = parse_uploaded_file(report_file)
        normal_data_raw = parse_uploaded_file(normal_file)

        normal_data = {}
        for k, v in normal_data_raw.items():
            if isinstance(v, list):
                normal_data[k] = v
            else:
                normal_data[k] = [v - 1, v + 1]

        analysis = compare_report_with_normals(report_data, normal_data)
        summary = generate_summary(analysis)

        output = ""
        for param, info in analysis.items():
            output += (
                f"{param}: {info['value']} | "
                f"Range: {info.get('normal_range','N/A')} → "
                f"{info['status']}\n"
            )

        output += "\nSummary:\n" + summary
        return output

    except Exception as e:
        return f"Error: {str(e)}"


app = gr.Interface(
    fn=analyze_files,
    inputs=[
        gr.File(label="Upload Blood Report"),
        gr.File(label="Upload Normal Range File")
    ],
    outputs=gr.Textbox(lines=12, label="Analysis Result"),
    title="AI Blood Report Analyzer",
    description="Upload blood report and normal range files (PDF, Image, CSV, JSON)"
)

app.launch()
