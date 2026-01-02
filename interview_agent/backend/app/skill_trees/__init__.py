from app.skill_trees.coding import CODING_SKILL_TREE
from app.skill_trees.system_design import SYSTEM_DESIGN_SKILL_TREE
from app.skill_trees.ml import ML_SKILL_TREE


SKILL_TREES = {
    "coding": CODING_SKILL_TREE,
    "system_design": SYSTEM_DESIGN_SKILL_TREE,
    "ml": ML_SKILL_TREE
}


def get_skill_tree(domain: str) -> dict:
    """Get the skill tree for a given domain."""
    return SKILL_TREES.get(domain, {})


def get_all_skills(domain: str) -> list:
    """Get a flat list of all skills in a domain."""
    tree = get_skill_tree(domain)
    skills = []

    def traverse(node, path=""):
        if isinstance(node, dict):
            for key, value in node.items():
                new_path = f"{path}/{key}" if path else key
                if isinstance(value, dict) and "skills" in value:
                    # Leaf node with skills
                    for skill in value["skills"]:
                        skills.append({
                            "domain": domain,
                            "topic": path.split("/")[0] if "/" in path else key,
                            "subtopic": key if "/" in new_path else None,
                            "skill": skill
                        })
                else:
                    traverse(value, new_path)

    traverse(tree)
    return skills


__all__ = [
    "SKILL_TREES",
    "get_skill_tree",
    "get_all_skills",
    "CODING_SKILL_TREE",
    "SYSTEM_DESIGN_SKILL_TREE",
    "ML_SKILL_TREE"
]
