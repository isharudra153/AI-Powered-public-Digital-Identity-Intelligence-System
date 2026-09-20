import re
import networkx as nx
from typing import Dict, Any


def _slug(text: Any) -> str:
    """'Quantum Computing' -> 'quantum-computing' (same every run, unlike hash())."""
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-") or "item"


class GraphBuilder:
    @staticmethod
    def build_network(target: Dict[str, Any]) -> Dict[str, Any]:
        G = nx.Graph()

        person_name = target.get("name", "Unknown")
        person_id = target.get("id") or f"person-{_slug(person_name)}"

        nodes = []
        edges = []
        seen_ids = set()

        def add_node(node: Dict[str, Any]) -> bool:
            """Add a node once. Returns False if it already exists."""
            if node["id"] in seen_ids:
                return False
            seen_ids.add(node["id"])
            nodes.append(node)
            return True

        # 1. Person Root Node
        add_node({
            "id": person_id,
            "label": person_name,
            "type": "Person",
            "metadata": {
                "headline": target.get("headline", ""),
                "location": target.get("location", "India"),
                "avatar": target.get("avatar_url", "")
            }
        })
        G.add_node(person_id)

        # 2. Public Profiles
        for prof in target.get("profiles", []):
            prof_id = f"node-{prof.get('id', _slug(prof.get('platform', 'profile')))}"

            if add_node({
                "id": prof_id,
                "label": f"{prof.get('platform', 'Profile')} ({prof.get('handle', '')})",
                "type": "Profile"
            }):
                edges.append({
                    "id": f"e-{person_id}-{prof_id}",
                    "source": person_id,
                    "target": prof_id,
                    "relation": "HAS_PROFILE",
                    "weight": prof.get("confidence", 0.95)
                })
                G.add_edge(person_id, prof_id)

        # extracted_entities must be a dictionary of lists
        entities = target.get("extracted_entities") or {}
        if not isinstance(entities, dict):
            entities = {}

        # 3. Organizations
        for org in entities.get("organizations", []):
            org_name = org.get("name") if isinstance(org, dict) else org
            if not org_name:
                continue

            org_id = f"node-org-{_slug(org_name)}"

            if add_node({
                "id": org_id,
                "label": org_name,
                "type": "Organization"
            }):
                edges.append({
                    "id": f"e-{person_id}-{org_id}",
                    "source": person_id,
                    "target": org_id,
                    "relation": "AFFILIATED_WITH",
                    "weight": 0.95
                })
                G.add_edge(person_id, org_id)

        # 4. Technologies (first 5)
        for tech in entities.get("technologies", [])[:5]:
            tech_id = f"node-tech-{_slug(tech)}"

            if add_node({
                "id": tech_id,
                "label": tech,
                "type": "Technology"
            }):
                edges.append({
                    "id": f"e-{person_id}-{tech_id}",
                    "source": person_id,
                    "target": tech_id,
                    "relation": "EXPERTISE_IN",
                    "weight": 0.85
                })
                G.add_edge(person_id, tech_id)

        return {
            "nodes": nodes,
            "edges": edges,
            "metrics": {
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }
        }