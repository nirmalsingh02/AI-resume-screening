import re


SKILLS = [

    # Programming
    "python",
    "java",
    "javascript",
    "sql",
    "c",
    "c++",
    "html5",
    "css3",

    # AI / ML
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "numpy",
    "pandas",
    "matplotlib",

    # Web
    "django",
    "django rest framework",
    "flask",
    "rest api",
    "rest apis",
    "bootstrap",

    # Databases
    "mysql",
    "postgresql",
    "mongodb",
    "sqlite",

    # Tools
    "git",
    "github",
    "docker",
    "postman",

    # Concepts
    "oop",
    "mvc",
    "data structures",
    "api design",
    "authentication",
    "authorization"
]


def normalize_text(text):

    text = text.lower()

    # Convert punctuation/separators to spaces
    text = re.sub(
        r"[^a-z0-9+#.]+",
        " ",
        text
    )

    # Remove repeated spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def extract_skills(text):

    text = normalize_text(text)

    found_skills = []

    for skill in SKILLS:

        normalized_skill = normalize_text(
            skill
        )

        # Flexible whitespace matching
        words = normalized_skill.split()

        pattern = r"\b" + r"\s+".join(
            map(re.escape, words)
        ) + r"\b"

        if re.search(
            pattern,
            text
        ):

            found_skills.append(
                skill
            )

    return sorted(
        set(found_skills)
    )


if __name__ == "__main__":

    sample_text = """
    Python, Django, Django REST Framework,
    PostgreSQL, Machine Learning, Pandas,
    NumPy, Git, Docker, REST APIs
    """

    print("\nDetected Skills:\n")

    for skill in extract_skills(
        sample_text
    ):

        print("✓", skill)