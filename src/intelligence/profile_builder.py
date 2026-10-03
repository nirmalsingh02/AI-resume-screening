import json

from src.intelligence.pdf_reader import extract_text_from_pdf
from src.intelligence.resume_parser import build_candidate_profile


# ============================================================
# CONFIGURATION
# ============================================================

PDF_PATH = "data/resumes/Nirmal_Singh_Resume_ATS.pdf"

OUTPUT_PATH = "data/candidate_profile.json"


# ============================================================
# 1. EXTRACT TEXT FROM PDF
# ============================================================

print("\n===== PHASE 11: RESUME INTELLIGENCE =====")

print("\n[1] Reading PDF...")

resume_text = extract_text_from_pdf(PDF_PATH)

print("PDF text extracted successfully.")


# ============================================================
# 2. BUILD CANDIDATE PROFILE
# ============================================================

print("\n[2] Extracting candidate information...")

profile = build_candidate_profile(resume_text)

print("Candidate information extracted successfully.")


# ============================================================
# 3. SAVE PROFILE AS JSON
# ============================================================

print("\n[3] Saving candidate profile...")

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        profile,
        file,
        indent=4,
        ensure_ascii=False
    )

print(
    f"Profile saved to: {OUTPUT_PATH}"
)


# ============================================================
# 4. DISPLAY PROFILE
# ============================================================

print("\n===== CANDIDATE PROFILE =====")

print(
    json.dumps(
        profile,
        indent=4,
        ensure_ascii=False
    )
)

print("\n===== PHASE 11 COMPLETED =====")