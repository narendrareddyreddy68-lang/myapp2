import streamlit as st
import fitz  # PyMuPDF
import re

# -------------------------
# Skills Database
# -------------------------
SKILLS_DB = [
    "Python", "SQL", "Machine Learning", "Deep Learning",
    "Data Analysis", "Pandas", "NumPy", "Power BI",
    "TensorFlow", "Excel"
]

# -------------------------
# Job Roles
# -------------------------
JOB_ROLES = {
    "Data Scientist": {
        "Python", "Machine Learning", "Deep Learning",
        "Pandas", "NumPy", "SQL", "TensorFlow"
    },
    "Data Analyst": {
        "Python", "SQL", "Power BI", "Pandas", "Data Analysis", "Excel"
    },
    "Backend Developer": {
        "Python", "SQL"
    },
    "Cloud Engineer": {
        "Python"
    }
}

# -------------------------
# Extract PDF Text (USING FITZ)
# -------------------------
def extract_pdf_text(file):
    text = ""

    try:
        pdf = fitz.open(stream=file.read(), filetype="pdf")

        for page in pdf:
            text += page.get_text() + "\n"

    except Exception as e:
        st.error(f"PDF reading error: {e}")
        return ""

    return text.strip()

# -------------------------
# Extract Skills
# -------------------------
def extract_skills(text):
    text = text.lower()
    found = set()

    for skill in SKILLS_DB:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text):
            found.add(skill)

    return sorted(found)

# -------------------------
# Score Calculation
# -------------------------
def calculate_score(skills):
    if not SKILLS_DB:
        return 0

    return round((len(skills) / len(SKILLS_DB)) * 100, 2)

# -------------------------
# Job Matching
# -------------------------
def match_jobs(candidate_skills):
    candidate_set = set(candidate_skills)
    results = []

    for role, required in JOB_ROLES.items():
        matched = candidate_set & required
        missing = required - candidate_set

        match_percent = round((len(matched) / len(required)) * 100, 2)

        results.append({
            "role": role,
            "match_percent": match_percent,
            "matched": matched,
            "missing": missing
        })

    return sorted(results, key=lambda x: x["match_percent"], reverse=True)

# -------------------------
# UI
# -------------------------
st.set_page_config(page_title="Resume Analyzer", layout="wide")

st.title("📄 Resume Analyzer (Fixed Version)")
st.write("Upload a PDF resume to analyze skills and job match.")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf"])

if uploaded_file:

    text = extract_pdf_text(uploaded_file)

    if not text:
        st.warning("No text found in PDF. Try another file.")
        st.stop()

    st.subheader("Extracted Text Preview")
    st.text_area("Text", text[:3000], height=250)

    skills = extract_skills(text)

    st.subheader("Detected Skills")

    if skills:
        st.success(", ".join(skills))
    else:
        st.warning("No skills detected.")

    score = calculate_score(skills)

    st.subheader("Resume Score")
    st.progress(min(int(score), 100))
    st.metric("Score", f"{score}%")

    st.subheader("Job Matching")

    matches = match_jobs(skills)

    for m in matches:
        with st.expander(f"{m['role']} — {m['match_percent']}% match"):

            st.write("**Matched Skills:**")
            st.write(", ".join(m["matched"]) if m["matched"] else "None")

            st.write("**Missing Skills:**")
            st.write(", ".join(m["missing"]) if m["missing"] else "None")

            st.progress(min(int(m["match_percent"]), 100))