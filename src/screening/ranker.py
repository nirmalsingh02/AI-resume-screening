import os

from src.screening.scorer import calculate_final_score


def read_file(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def rank_candidates(resume_folder, job_path):

    job_text = read_file(job_path)

    results = []

    for filename in os.listdir(resume_folder):

        if not filename.endswith(".txt"):
            continue

        resume_path = os.path.join(
            resume_folder,
            filename
        )

        resume_text = read_file(resume_path)

        skill_score, text_score, final_score = calculate_final_score(
            resume_text,
            job_text
        )

        results.append({
            "candidate": filename,
            "skill_score": skill_score,
            "text_score": text_score,
            "final_score": final_score
        })

    results.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    return results


if __name__ == "__main__":

    resume_folder = "data/resumes"
    job_path = "data/job_descriptions/ml_engineer.txt"

    results = rank_candidates(
        resume_folder,
        job_path
    )

    print("\n===== CANDIDATE RANKING =====\n")

    for rank, candidate in enumerate(results, start=1):

        print(
            f"{rank}. {candidate['candidate']}"
        )

        print(
            f"   Skill Match:     "
            f"{candidate['skill_score']:.2f}%"
        )

        print(
            f"   Text Similarity: "
            f"{candidate['text_score']:.2f}%"
        )

        print(
            f"   Final Score:     "
            f"{candidate['final_score']:.2f}%"
        )

        print()