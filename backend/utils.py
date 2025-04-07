import fitz  # PyMuPDF
import re
from collections import Counter


def parse_script_from_pdf(path):
    doc = fitz.open(path)
    all_lines = []
    for page in doc:
        text = page.get_text()
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                all_lines.append(line)
    return all_lines


def extract_characters(script_lines):
    """Extract character names from screenplay-style scripts."""
    characters = set()
    i = 0

    while i < len(script_lines):
        line = script_lines[i].strip()

        # Skip empty lines and scene directions
        if (not line or
            line.startswith(('INT.', 'EXT.', 'FADE', 'CUT TO', 'DISSOLVE')) or
            (line.startswith('(') and line.endswith(')'))):
            i += 1
            continue

        # Character name detection (all caps, short, not directions)
        if line.isupper() and 1 <= len(line.split()) <= 3:
            char_name = line.split("(")[0].strip()  # Remove things like (O.S.)
            characters.add(char_name)
            i += 2 if i + 1 < len(script_lines) and script_lines[i + 1].strip().startswith("(") else 1
        else:
            i += 1

    return sorted(characters)

# def extract_characters(script_lines):
#     print("in utils.py MAYA BELLO")
#     potential_chars = []
#     for line in script_lines:
#         if line.isupper() and not re.match(r'^(INT\.|EXT\.|FADE|CUT TO|DISSOLVE)', line):
#             if len(line.split()) <= 4:
#                 potential_chars.append(line)
#     most_common = Counter(potential_chars).most_common()
#     return [char for char, count in most_common]
#
#
# def extract_characters(script_lines):
#     """Identify characters in script"""
#     characters = set()
#     for line in script_lines:
#         if ":" in line:
#             char = line.split(":")[0].strip()
#             if char.isupper() and len(char.split()) < 3:
#                 characters.add(char)
#     return list(characters)