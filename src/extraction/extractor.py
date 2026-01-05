import re

def extract_rbc(text):
    lines = text.split('\n')
    result = {}
    rbc_keywords = ['RBC', 'R.B.C','Red Blood Cells', 'Red Blood Cell Count']
    for i in range(len(lines)):
        line = lines[i].strip()
        # Step 1: detect RBC anchor
        if any(keyword.lower() in line.lower() for keyword in rbc_keywords):

