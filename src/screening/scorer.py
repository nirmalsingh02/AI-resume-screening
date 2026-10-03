from src.preprocessing.skill_extractor import extract_skills
from src.features.tfidf_matcher import calculate_text_similarity


def calculate_skill_score(resume_text, job_text):

    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_text))

    if not job_skills:
        return 0

    matched_skills = resume_skills.intersection(job_skills)

    score = (len(matched_skills) / len(job_skills)) * 100

    return score


def calculate_final_score(resume_text, job_text):

    skill_score = calculate_skill_score(
        resume_text,
        job_text
    )

    text_similarity = calculate_text_similarity(
        resume_text,
        job_text
    ) * 100

    final_score = (
        skill_score * 0.70
        +
        text_similarity * 0.30
    )

    return skill_score, text_similarity, final_score


def read_file(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


if __name__ == "__main__":

    resume_path = "data/resumes/candidate_01.txt"
    job_path = "data/job_descriptions/ml_engineer.txt"

    resume_text = read_file(resume_path)
    job_text = read_file(job_path)

    skill_score, text_score, final_score = calculate_final_score(
        resume_text,
        job_text
    )

    print("\n===== AI RESUME SCREENING =====")

    print(f"\nSkill Match:       {skill_score:.2f}%")
    print(f"Text Similarity:   {text_score:.2f}%")
    print(f"Final Score:       {final_score:.2f}%")