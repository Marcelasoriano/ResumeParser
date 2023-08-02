import re
from flask import Flask, render_template, request, jsonify
import configparser
from docx import Document
from PyPDF2 import PdfReader

app = Flask(__name__)
config = configparser.ConfigParser()
config.read('config.cfg')
config_file_path = config.get('config', 'config_file_path').strip('"')

class ResumeParser:
    def __init__(self, resume, skills_file="skills.txt", custom_regex=None):
        self.resume = resume
        self.custom_regex = custom_regex
        self.skills_file = skills_file
        self.data = {}

    def load_skills(self, skills_file):
        with open(skills_file) as file:
            skills = file.readlines()
        skills = [skill.strip().lower() for skill in skills]
        return skills

    def extract_name(self, text):
        name_regex = r"Name: ([A-Za-z ]+)"
        match = re.search(name_regex, text)
        if match:
            return match.group(1)
        else:
            return "Unknown"

    def extract_email(self, text):
        email_regex = r"Email: ([\w.-]+@[\w.-]+)"
        match = re.search(email_regex, text)
        if match:
            return match.group(1)
        else:
            return "Unknown"

    def extract_skills(self, text):
        skills = self.load_skills(self.skills_file)
        found_skills = [skill for skill in skills if skill in text.lower()]
        return found_skills

def read_docx(file):
    doc = Document(file)
    text = " ".join([paragraph.text for paragraph in doc.paragraphs])
    return text

def read_pdf(file):
    reader = PdfReader(file)
    text = " ".join([reader.pages[i].extract_text() for i in range(len(reader.pages))])
    return text

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/parse_resume", methods=['POST'])
def parse_resume():
    parsed_info = {
        'Name': '',
        'Email': '',
        'skills': []
    }
    file = request.files['file']
    if file:
        filename = file.filename
        if filename.endswith(".txt"):
            resume_content = file.read().decode('latin-1')
        elif filename.endswith(".docx"):
            resume_content = read_docx(file)
        elif filename.endswith(".pdf"):
            resume_content = read_pdf(file)
        else:
            return "Unsupported file format"

        parser = ResumeParser(resume_content)
        parsed_info['Name'] = parser.extract_name(resume_content)
        parsed_info['Email'] = parser.extract_email(resume_content)
        parsed_info['skills'] = parser.extract_skills(resume_content)

    return jsonify(parsed_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
