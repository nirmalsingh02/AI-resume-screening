import json

from src.intelligence.pdf_reader import extract_text_from_pdf
from src.preprocessing.skill_extractor import extract_skills
from src.features.tfidf_matcher import calculate_text_similarity


# ============================================================
# CONFIGURATION
# ============================================================

RESUME_PATH = (
    "data/resumes/Nirmal_Singh_Resume_ATS.pdf"
)

JOB_PATH = (
    "data/job_descriptions/ml_engineer.txt"
)


# ============================================================
# 1. READ TEXT FILE
# ============================================================

def read_text_file(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ============================================================
# 2. CALCULATE SKILL MATCH
# ============================================================

def calculate_skill_match(
    resume_text,
    job_text
):

    resume_skills = set(
        extract_skills(resume_text)
    )

    job_skills = set(
        extract_skills(job_text)
    )

    matched_skills = (
        resume_skills
        .intersection(job_skills)
    )

    missing_skills = (
        job_skills
        - resume_skills
    )

    if job_skills:

        skill_score = (
            len(matched_skills)
            / len(job_skills)
        ) * 100

    else:

        skill_score = 0

    return (
        skill_score,
        matched_skills,
        missing_skills
    )


# ============================================================
# 3. CALCULATE FINAL MATCH SCORE
# ============================================================

def calculate_final_score(
    skill_score,
    text_similarity
):

    text_score = (
        text_similarity * 100
    )

    final_score = (
        skill_score * 0.60
        +
        text_score * 0.40
    )

    return final_score


# ============================================================
# 4. LOAD RESUME
# ============================================================

print("\n===== PHASE 12: JOB MATCHING =====")

print("\nReading resume...")

resume_text = extract_text_from_pdf(
    RESUME_PATH
)

print("Resume loaded successfully.")


# ============================================================
# 5. LOAD JOB DESCRIPTION
# ============================================================

print("\nReading job description...")

job_text = read_text_file(
    JOB_PATH
)

print("Job description loaded successfully.")


# ============================================================
# 6. SKILL MATCHING
# ============================================================

print("\nAnalyzing skills...")

(
    skill_score,
    matched_skills,
    missing_skills
) = calculate_skill_match(
    resume_text,
    job_text
)


# ============================================================
# 7. TF-IDF SIMILARITY
# ============================================================

print("Calculating text similarity...")

text_similarity = (
    calculate_text_similarity(
        resume_text,
        job_text
    )
)


# ============================================================
# 8. FINAL SCORE
# ============================================================

final_score = calculate_final_score(
    skill_score,
    text_similarity
)


# ============================================================
# 9. RECOMMENDATION
# ============================================================

if final_score >= 75:

    recommendation = "STRONG MATCH"

elif final_score >= 60:

    recommendation = "GOOD MATCH"

elif final_score >= 45:

    recommendation = "PARTIAL MATCH"

else:

    recommendation = "LOW MATCH"


# ============================================================
# 10. DISPLAY RESULT
# ============================================================

print("\n")
print("=" * 60)
print("          AI RESUME ↔ JOB MATCHING")
print("=" * 60)

print(
    f"\nSkill Match:       "
    f"{skill_score:.2f}%"
)

print(
    f"Text Similarity:   "
    f"{text_similarity * 100:.2f}%"
)

print(
    f"Final Match Score: "
    f"{final_score:.2f}%"
)

print(
    f"\nRecommendation: "
    f"{recommendation}"
)


print("\nMatched Skills:")

if matched_skills:

    for skill in sorted(matched_skills):

        print("✓", skill)

else:

    print("None")


print("\nMissing Skills:")

if missing_skills:

    for skill in sorted(missing_skills):

        print("✗", skill)

else:

    print("None")


print("\n" + "=" * 60)