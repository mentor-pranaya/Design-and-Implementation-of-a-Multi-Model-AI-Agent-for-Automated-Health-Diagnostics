from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lab-report-analyzer",
    version="3.0.0",
    author="Health Diagnostics Team",
    description="AI-powered lab report analyzer with multi-model synthesis and recommendations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pdfplumber",
        "pytesseract",
        "pdf2image",
        "Pillow",
        "reportlab",
        "streamlit",
        "supabase",
        "requests",
        "python-dotenv",
    ],
)
