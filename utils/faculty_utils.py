from fuzzywuzzy import fuzz
from config import FACULTY_DATASET_PATH
from .file_utils import load_json_file

def match_faculty_with_topics(main_topics, faculty_data, threshold=90, top_n=5):
    faculty_scores = []

    for faculty in faculty_data:
        expertise = faculty.get("expertise", [])

        # Initialize the match score
        match_score = 0

        for topic in main_topics:
            # Compare each topic with the expertise list using fuzzywuzzy
            best_match_score = max(fuzz.partial_ratio(topic.lower(), exp.lower()) for exp in expertise)
            match_score += best_match_score

        # Normalize the satisfaction rate and rating
        satisfaction_score = float(faculty.get("satisfaction_rate", "0%").replace("%", "")) / 100.0
        rating_score = faculty.get("rating", 0) / 5.0
        max_price = 300
        price_score = 1 - (faculty.get("session_price", max_price) / max_price)

        # Weighted score
        total_score = (0.7 * match_score) + (0.1 * rating_score) + (0.15 * satisfaction_score) + (0.05 * price_score)
        faculty_scores.append((faculty, total_score))

    # Filter and sort faculties by score
    filtered_sorted = sorted(
        [(fac, score) for fac, score in faculty_scores if score >= threshold],
        key=lambda x: x[1], reverse=True
    )

    # Return only top N
    top_matches = [fac for fac, _ in filtered_sorted[:top_n]]
    return top_matches 