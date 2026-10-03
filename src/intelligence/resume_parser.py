import re

from src.preprocessing.skill_extractor import extract_skills


# ============================================================
# 1. EXTRACT NAME
# ============================================================

def extract_name(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if lines:
        return lines[0]

    return "Unknown"


# ============================================================
# 2. EXTRACT EMAIL
# ============================================================

def extract_email(text):

    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

    match = re.search(pattern, text)

    if match:
        return match.group()

    return "Not found"


# ============================================================
# 3. EXTRACT PHONE
# ============================================================

def extract_phone(text):

    pattern = r"\+?\d[\d\s\-]{8,}\d"

    match = re.search(pattern, text)

    if match:
        return match.group().strip()

    return "Not found"


# ============================================================
# 4. EXTRACT EXPERIENCE
# ============================================================

def extract_experience(text):

    # Look for explicit experience statements
    patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience)?",
        r"(\d+(?:\.\d+)?)\+?\s*years?"
    ]

    values = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text.lower()
        )

        for value in matches:

            try:
                values.append(float(value))
            except ValueError:
                pass

    if values:
        return max(values)

    # Student/internship style resume
    if "student" in text.lower():
        return 0

    return 0


# ============================================================
# 5. EXTRACT EDUCATION
# ============================================================

def extract_education(text):

    education = []

    lines = text.splitlines()

    inside_education = False

    for line in lines:

        line = line.strip()

        if not line:
            continue

        lower = line.lower()

        if "education" in lower:
            inside_education = True
            continue

        if inside_education:

            if any(
                section in lower
                for section in [
                    "core competencies",
                    "technical skills",
                    "projects",
                    "professional summary"
                ]
            ):
                break

            education.append(line)

    return education


# ============================================================
# 6. EXTRACT PROJECTS
# ============================================================

def extract_projects(text):

    projects = []

    lines = text.splitlines()

    inside_projects = False
    current_project = ""

    for line in lines:

        line = line.strip()

        if not line:
            continue

        lower = line.lower()

        if "projects" in lower:

            inside_projects = True
            continue

        if inside_projects:

            if lower.startswith("education"):

                break

            if "core competencies" in lower:

                break

            # Detect project title
            if "—" in line or " - " in line:

                if current_project:
                    projects.append(
                        current_project
                    )

                current_project = line

            else:

                if current_project:
                    current_project += " " + line

    if current_project:
        projects.append(
            current_project
        )

    return projects


# ============================================================
# 7. EXTRACT CORE COMPETENCIES
# ============================================================

def extract_competencies(text):

    lines = text.splitlines()

    competencies = []

    inside = False

    for line in lines:

        line = line.strip()

        if not line:
            continue

        lower = line.lower()

        if "core competencies" in lower:

            inside = True
            continue

        if inside:

            if line:
                competencies.extend(
                    [
                        item.strip()
                        for item in line.split(",")
                    ]
                )

    return competencies


# ============================================================
# 8. BUILD COMPLETE PROFILE
# ============================================================

def build_candidate_profile(text):

    profile = {

        "name": extract_name(text),

        "email": extract_email(text),

        "phone": extract_phone(text),

        "skills": extract_skills(text),

        "experience": extract_experience(text),

        "education": extract_education(text),

        "projects": extract_projects(text),

        "competencies": extract_competencies(text)
    }

    return profile


# ============================================================
# 9. TEST
# ============================================================

if __name__ == "__main__":

    from src.intelligence.pdf_reader import (
        extract_text_from_pdf
    )

    pdf_path = (
        "data/resumes/"
        "Nirmal_Singh_Resume_ATS.pdf"
    )

    resume_text = extract_text_from_pdf(
        pdf_path
    )

    profile = build_candidate_profile(
        resume_text
    )

    print("\n")
    print("=" * 60)
    print("           AI RESUME INTELLIGENCE")
    print("=" * 60)

    print("\nNAME:")
    print(profile["name"])

    print("\nEMAIL:")
    print(profile["email"])

    print("\nPHONE:")
    print(profile["phone"])

    print("\nSKILLS:")

    for skill in profile["skills"]:
        print("✓", skill)

    print("\nEXPERIENCE:")
    print(profile["experience"], "years")

    print("\nEDUCATION:")

    for item in profile["education"]:
        print("•", item)

    print("\nPROJECTS:")

    for project in profile["projects"]:
        print("•", project)

    print("\nCORE COMPETENCIES:")

    for item in profile["competencies"]:
        print("✓", item)

    print("\n" + "=" * 60)