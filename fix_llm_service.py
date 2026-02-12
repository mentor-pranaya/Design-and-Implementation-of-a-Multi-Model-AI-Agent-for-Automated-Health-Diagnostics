import os

file_path = r"c:\Users\rakes\Downloads\blood report ai\src\llm\llm_service.py"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Line 125 (0-indexed is 124)
# The corrupt line is at index 124
lines[124] = "                if line and (line[0].isdigit() or line.startswith(('•', '-', '*'))):\n"

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("Successfully fixed llm_service.py")
