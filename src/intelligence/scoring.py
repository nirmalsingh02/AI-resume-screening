def calculate_final_score(
    skill_score,
    text_similarity,
    experience_score
):
    """
    Calculate the overall candidate score.

    Weights:
    - Skills: 60%
    - Text similarity: 25%
    - Experience: 15%
    """

    final_score = (
        skill_score * 0.60
        + text_similarity * 0.25
        + experience_score * 0.15
    )

    return round(final_score, 2)


def get_recommendation(score):

    if score >= 75:
        return "🟢 STRONG MATCH"

    elif score >= 60:
        return "🟡 GOOD MATCH"

    elif score >= 45:
        return "🟠 NEEDS REVIEW"

    else:
        return "🔴 LOW MATCH"


if __name__ == "__main__":

    score = calculate_final_score(
        skill_score=69.2,
        text_similarity=61.5,
        experience_score=80
    )

    print("Final Score:", score)
    print(
        "Recommendation:",
        get_recommendation(score)
    )