import streamlit as st
from extractor import extract
from model1 import interpret

st.set_page_config(page_title="Automated Health Diagnostics- Model 1")
st.title("Automated Health Diagnostics – Model 1")

uploaded_file = st.file_uploader(
    "Upload file (PDF / Image / CSV / JSON)",
    type=["pdf", "png", "jpg", "jpeg", "csv", "json"]
)

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()
    data = extract(uploaded_file, file_type)

    if not data:
        st.warning("No medical parameters detected.")
    else:
        st.subheader("Model-1 Output")

        for item in data:
            result = interpret(item["Test"], item["Value"])
            st.write(f"**{item['Test']}** : {item['Value']} → **{result}**")
