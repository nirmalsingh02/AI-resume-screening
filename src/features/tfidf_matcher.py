from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_text_similarity(resume_text, job_text):

    documents = [
        resume_text,
        job_text
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    vectors = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        vectors[0],
        vectors[1]
    )[0][0]

    return similarity


def read_file(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


if __name__ == "__main__":

    resume_path = "data/resumes/candidate_01.txt"
    job_path = "data/job_descriptions/ml_engineer.txt"

    resume_text = read_file(resume_path)
    job_text = read_file(job_path)

    similarity = calculate_text_similarity(
        resume_text,
        job_text
    )

    percentage = similarity * 100

    print("\n===== TF-IDF RESUME MATCHING =====")

    print(f"\nText Similarity: {percentage:.2f}%")