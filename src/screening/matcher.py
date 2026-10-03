from src.preprocessing.skill_extractor import extract_skills


def calculate_match_score(resume_text, job_text):
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_text))

    matched_skills = resume_skills.intersection(job_skills)
    missing_skills = job_skills - resume_skills

    if len(job_skills) == 0:
        score = 0
    else:
        score = (len(matched_skills) / len(job_skills)) * 100

    return score, matched_skills, missing_skills


def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


if __name__ == "__main__":

    resume_path = "data/resumes/candidate_01.txt"
    job_path = "data/job_descriptions/ml_engineer.txt"

    resume_text = read_file(resume_path)
    job_text = read_file(job_path)

    score, matched, missing = calculate_match_score(
        resume_text,
        job_text
    )

    print("\n===== AI RESUME SCREENING =====")

    print(f"\nMatch Score: {score:.2f}%")

    print("\nMatched Skills:")
    for skill in sorted(matched):
        print("✓", skill)

    print("\nMissing Skills:")
    for skill in sorted(missing):
        print("✗", skill)