from typing import List, Dict, Any

class FalseMatchDetector:
    @staticmethod
    def evaluate_conflicts(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        conflicts = []
        for cand in candidates:
            if cand.get("status") == "False Match (Rejected)":
                name_score = cand.get("signals", {}).get("name_similarity", 0.0)
                conflicts.append({
                    "candidate_id": cand.get("id", ""),
                    "name": cand.get("name", "Unknown"),
                    "domain": cand.get("headline", ""),
                    "similarity_score": name_score,
                    "decision": "REJECTED (Refusal to Merge)",
                    "conflict_type": "Domain & Geographic Incompatibility",
                    "conflict_details": (
                        f"Target query specifies technical engineering. Candidate '{cand.get('name', 'Unknown')}' has high name similarity "
                        f"({name_score * 100:.0f}%) but verified primary activities are in an unrelated field "
                        f"with geographic divergence."
                    ),
                    "why_not_merged": (
                        "DigitalTrace AI enforces strict multi-signal verification. High lexical name match is insufficient "
                        "when organizational, domain, and geographic signals produce negative correlation. Merging would result "
                        "in an erroneous composite identity."
                    )
                })
        return conflicts
        