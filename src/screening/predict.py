import joblib

from src.preprocessing.skill_extractor import extract_skills
from src.features.tfidf_matcher import calculate_text_similarity


# ============================================================
# 1. READ FILE
# ============================================================

def read_file(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# ============================================================
# 2. CALCULATE SKILL MATCH
# ============================================================

def calculate_skill_score(resume_text, job_text):

    resume_skills = set(
        extract_skills(resume_text)
    )

    job_skills = set(
        extract_skills(job_text)
    )

    if not job_skills:
        return 0

    matched_skills = (
        resume_skills.intersection(job_skills)
    )

    score = (
        len(matched_skills)
        / len(job_skills)
    ) * 100

    return score


# ============================================================
# 3. EXTRACT EXPERIENCE
# ============================================================

def extract_experience(resume_text):

    import re

    pattern = r"(\d+)\s*(?:years?|yrs?)"

    matches = re.findall(
        pattern,
        resume_text.lower()
    )

    if matches:
        return max(
            int(years)
            for years in matches
        )

    return 0


# ============================================================
# 4. LOAD MODEL
# ============================================================

model = joblib.load(
    "models/resume_classifier.pkl"
)

print("\nModel loaded successfully!")


# ============================================================
# 5. FILE PATHS
# ============================================================

resume_path = (
    "data/resumes/candidate_01.txt"
)

job_path = (
    "data/job_descriptions/ml_engineer.txt"
)


# ============================================================
# 6. READ RESUME + JOB DESCRIPTION
# ============================================================

resume_text = read_file(
    resume_path
)

job_text = read_file(
    job_path
)


# ============================================================
# 7. FEATURE ENGINEERING
# ============================================================

skill_score = calculate_skill_score(
    resume_text,
    job_text
)

text_similarity = (
    calculate_text_similarity(
        resume_text,
        job_text
    )
)

experience = extract_experience(
    resume_text
)


# ============================================================
# 8. CREATE FEATURE DATA
# ============================================================

features = [[
    skill_score,
    text_similarity,
    experience
]]


# ============================================================
# 9. ML PREDICTION
# ============================================================

prediction = model.predict(
    features
)[0]


probability = model.predict_proba(
    features
)[0]


# ============================================================
# 10. DISPLAY RESULT
# ============================================================

print("\n")
print("=" * 50)
print("       AI RESUME SCREENING RESULT")
print("=" * 50)

print(
    f"\nSkill Match:       {skill_score:.2f}%"
)

print(
    f"Text Similarity:   "
    f"{text_similarity * 100:.2f}%"
)

print(
    f"Experience:        "
    f"{experience} years"
)


print("\nML Prediction:")

if prediction == 1:

    print("🟢 SUITABLE")

else:

    print("🔴 NOT SUITABLE")


print(
    f"\nNot Suitable Probability: "
    f"{probability[0] * 100:.2f}%"
)

print(
    f"Suitable Probability:     "
    f"{probability[1] * 100:.2f}%"
)

print("=" * 50)