import re


def extract_experience_years(text):
    """
    Extract explicit professional experience from resume text.

    Examples detected:
        2 years of experience
        2+ years experience
        1.5 years of experience
        Experience: 3 years
    """

    text = text.lower()

    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+of\s+experience",
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+experience",
        r"experience\s*[:\-]\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            return float(
                match.group(1)
            )

    return 0.0


def calculate_experience_score(
    candidate_years,
    required_min=0,
    required_max=2
):
    """
    Convert candidate experience into a score from 0-100.
    """

    if candidate_years >= required_max:

        return 100.0

    if candidate_years < required_min:

        return 0.0

    if required_max == required_min:

        return 100.0

    score = (
        (candidate_years - required_min)
        /
        (required_max - required_min)
    ) * 100

    return round(
        score,
        2
    )


if __name__ == "__main__":

    test_resume = """
    Python Developer with 2 years
    of experience in Django and REST APIs.
    """

    years = extract_experience_years(
        test_resume
    )

    score = calculate_experience_score(
        years,
        required_min=0,
        required_max=2
    )

    print("\n===== EXPERIENCE EXTRACTION =====")

    print(
        f"Experience: {years} years"
    )

    print(
        f"Experience Score: {score}%"
    )