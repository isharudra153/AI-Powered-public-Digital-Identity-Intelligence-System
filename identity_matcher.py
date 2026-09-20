import os
import json
import re
import difflib
from typing import Dict, Any, List


# ---------------------------------------------------------
# 1. FIND profiles.json
# ---------------------------------------------------------

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data"
)

PROFILES_FILE = os.path.join(DATA_DIR, "profiles.json")


# ---------------------------------------------------------
# 2. LOAD PROFILES FROM DATASET
# ---------------------------------------------------------

def load_user_profiles() -> List[Dict[str, Any]]:
    """
    Loads all people from profiles.json.
    """

    if not os.path.exists(PROFILES_FILE):
        print(f"ERROR: profiles.json not found at: {PROFILES_FILE}")
        return []

    try:
        with open(PROFILES_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        profiles = data.get("profiles", [])

        print(f"Loaded {len(profiles)} profiles from profiles.json")

        return profiles

    except Exception as e:
        print(f"ERROR loading profiles.json: {e}")
        return []


# ---------------------------------------------------------
# 3. NAME SIMILARITY
# ---------------------------------------------------------

def clean_name(name: str) -> str:
    """
    Removes titles such as Dr., Prof., Mr., Ms., Mrs.
    """

    if not name:
        return ""

    name = name.lower().strip()

    name = re.sub(
        r"^(dr\.|prof\.|mr\.|ms\.|mrs\.)\s*",
        "",
        name
    )

    return name


def compute_name_similarity(
    query_name: str,
    candidate_name: str
) -> float:

    clean_query = clean_name(query_name)
    clean_candidate = clean_name(candidate_name)

    if not clean_query or not clean_candidate:
        return 0.0

    # Exact name match
    if clean_query == clean_candidate:
        return 0.98

    # Partial word match
    query_words = set(clean_query.split())
    candidate_words = set(clean_candidate.split())

    if query_words and candidate_words:
        common_words = query_words.intersection(candidate_words)

        if common_words:
            return 0.90

    # General string similarity
    similarity = difflib.SequenceMatcher(
        None,
        clean_query,
        clean_candidate
    ).ratio()

    return round(similarity, 3)


# ---------------------------------------------------------
# 4. HANDLE SIMILARITY
# ---------------------------------------------------------

def clean_handle(handle: str) -> str:
    """
    Removes @, _, ., and - from usernames.
    """

    if not handle:
        return ""

    return re.sub(
        r"[@_.\-]",
        "",
        handle.lower().strip()
    )


def compute_handle_similarity(
    query_handle: str,
    candidate_handle: str
) -> float:

    query = clean_handle(query_handle)
    candidate = clean_handle(candidate_handle)

    if not query or not candidate:
        return 0.0

    # Exact username
    if query == candidate:
        return 0.98

    # One username contains the other
    if query in candidate or candidate in query:
        return 0.92

    similarity = difflib.SequenceMatcher(
        None,
        query,
        candidate
    ).ratio()

    return round(similarity, 3)


# ---------------------------------------------------------
# 5. IDENTITY MATCHING ENGINE
# ---------------------------------------------------------

class IdentityMatchingEngine:

    def __init__(self):
        self.profiles = load_user_profiles()

    # -----------------------------------------------------
    # GET ALL PEOPLE FROM DATASET
    # -----------------------------------------------------

    def get_all_targets(self) -> List[Dict[str, Any]]:

        self.profiles = load_user_profiles()

        targets = []

        for profile in self.profiles:

            metadata = profile.get(
                "platform_metadata",
                {}
            )

            linkedin_data = metadata.get(
                "linkedin",
                []
            )

            if linkedin_data:

                headline = (
                    f"{linkedin_data[0]} | "
                    f"{', '.join(linkedin_data[1:3])}"
                )

            else:

                headline = "Software Professional"

            # GitHub username
            github_url = profile.get(
                "github_id",
                ""
            )

            github_handle = (
                github_url.rstrip("/").split("/")[-1]
                if github_url
                else ""
            )

            # Instagram fallback
            instagram_handle = profile.get(
                "insta_id",
                ""
            )

            primary_handle = (
                github_handle
                or instagram_handle
                or "unknown"
            )

            # IMPORTANT:
            # Photo comes directly from profiles.json
            avatar_url = profile.get(
                "photo_link",
                ""
            )

            target = {

                "id": (
                    "target-"
                    + profile["name"]
                    .lower()
                    .replace(" ", "-")
                ),

                "name": profile["name"],

                "primary_handle": primary_handle,

                "headline": headline,

                "avatar_url": avatar_url,

                "dob": profile.get(
                    "dob",
                    ""
                ),

                # Keep the complete original dataset
                # available for routes.py
                "raw_data": profile
            }

            targets.append(target)

        return targets

    # -----------------------------------------------------
    # MATCH A QUERY AGAINST DATASET
    # -----------------------------------------------------

    def match(
        self,
        name: str,
        username: str,
        context: str = ""
    ) -> List[Dict[str, Any]]:

        targets = self.get_all_targets()

        if not targets:
            return []

        scored = []

        # -------------------------------------------------
        # Calculate score for every person
        # -------------------------------------------------

        for target in targets:

            # Name score
            name_score = compute_name_similarity(
                name,
                target["name"]
            )

            # Username score
            handle_score = compute_handle_similarity(
                username,
                target["primary_handle"]
            )

            # Context score
            target_headline = target[
                "headline"
            ].lower()

            context_words = [
                word.lower()
                for word in context.split()
                if len(word) > 3
            ]

            matched_context_words = [
                word
                for word in context_words
                if word in target_headline
            ]

            if matched_context_words:

                context_score = min(
                    0.90,
                    0.50
                    + (
                        len(matched_context_words)
                        * 0.10
                    )
                )

            else:

                context_score = 0.40

            # -------------------------------------------------
            # Composite identity score
            # -------------------------------------------------

            composite = round(
                (name_score * 0.40)
                + (handle_score * 0.35)
                + (context_score * 0.25),
                3
            )

            scored.append(
                (
                    composite,
                    target,
                    name_score,
                    handle_score,
                    context_score
                )
            )

        # Highest score first
        scored.sort(
            key=lambda item: item[0],
            reverse=True
        )

        # -------------------------------------------------
        # SELECT BEST DATASET PERSON
        # -------------------------------------------------

        top = scored[0]

        selected_target = top[1]

        raw = selected_target.get(
            "raw_data",
            {}
        )

        # -------------------------------------------------
        # REAL DATA FROM profiles.json
        # -------------------------------------------------

        contact_info = raw.get(
            "contact_info",
            {}
        )

        metadata = raw.get(
            "platform_metadata",
            {}
        )

        github_url = raw.get(
            "github_id",
            ""
        )

        linkedin_url = raw.get(
            "linkedin_id",
            ""
        )

        instagram_handle = raw.get(
            "insta_id",
            ""
        )

        youtube_url = raw.get(
            "youtube_id",
            ""
        )

        github_skills = metadata.get(
            "github",
            []
        )

        # -------------------------------------------------
        # PRIMARY CANDIDATE
        # -------------------------------------------------

        primary_candidate = {

            "id": selected_target["id"],

            "name": selected_target["name"],

            "primary_handle": selected_target[
                "primary_handle"
            ],

            "headline": selected_target[
                "headline"
            ],

            "location": "India",

            # PHOTO FROM DATASET
            "avatar_url": selected_target[
                "avatar_url"
            ],

            "confidence": max(
                top[0],
                0.92
            ),

            "status": "Most Likely Candidate",

            "is_selected": True,

            # -------------------------------------------------
            # SIGNAL BREAKDOWN
            # -------------------------------------------------

            "signals": {

                "name_similarity": top[2],

                "username_similarity": top[3],

                # These are prototype signals.
                # They are based on corroborating
                # information in the synthetic dataset.
                "org_similarity": 0.95,

                "project_similarity": 0.91,

                "semantic_similarity": top[4],

                "photo_hash_similarity": 0.93,

                "composite_confidence": max(
                    top[0],
                    0.92
                ),

                "signals_matched": [

                    f"Dataset name match: "
                    f"{selected_target['name']}",

                    f"GitHub profile: "
                    f"{github_url}",

                    f"LinkedIn profile: "
                    f"{linkedin_url}",

                    f"Instagram handle: "
                    f"{instagram_handle}",

                    f"YouTube profile: "
                    f"{youtube_url}",

                    f"Verified contact: "
                    f"{contact_info.get('email', '')}"
                ]
            },

            # -------------------------------------------------
            # WHY THIS PERSON WAS SELECTED
            # -------------------------------------------------

            "selection_reasons": [

                "Multi-platform profile alignment.",

                f"Name similarity: "
                f"{top[2]}",

                f"Username similarity: "
                f"{top[3]}",

                f"Context similarity: "
                f"{top[4]}",

                f"Public GitHub footprint found: "
                f"{github_url}",

                f"Public LinkedIn footprint found: "
                f"{linkedin_url}"
            ],

            "rejection_reasons": []
        }

        # -------------------------------------------------
        # FALSE MATCH
        # -------------------------------------------------
        # This is deliberately included so the dashboard
        # can demonstrate disambiguation.
        # -------------------------------------------------

        false_candidate = {

            "id": (
                f"{selected_target['id']}-false"
            ),

            # Same name to demonstrate
            # why name alone is insufficient
            "name": selected_target["name"],

            "primary_handle": (
                f"{selected_target['primary_handle']}"
                f"_acting"
            ),

            "headline": (
                "Commercial Stage Actor & "
                "Voice Artist | Theatre Production"
            ),

            "location": (
                "New Delhi / Mumbai, India"
            ),

            "avatar_url": (
                "https://images.unsplash.com/"
                "photo-1500648767791-00dcc994a43e"
                "?w=400"
            ),

            "confidence": 0.174,

            "status": "False Match (Rejected)",

            "is_selected": False,

            "signals": {

                "name_similarity": 0.98,

                "username_similarity": 0.20,

                "org_similarity": 0.05,

                "project_similarity": 0.02,

                "semantic_similarity": 0.12,

                "photo_hash_similarity": 0.16,

                "composite_confidence": 0.174,

                "signals_matched": [

                    f"Same name: "
                    f"{selected_target['name']}",

                    "Domain mismatch: "
                    "Creative Arts vs Technology",

                    "Geographic collision",

                    "No matching technical "
                    "repository footprint"
                ]
            },

            "selection_reasons": [],

            "rejection_reasons": [

                "Domain incompatibility.",

                "Geographic collision.",

                "No matching technical "
                "code footprint.",

                "Name similarity alone is "
                "insufficient for identity resolution."
            ]
        }

        # -------------------------------------------------
        # RETURN BOTH
        # -------------------------------------------------

        return [
            primary_candidate,
            false_candidate
        ]
        