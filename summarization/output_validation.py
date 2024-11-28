from typing import Union, List


def validate_keywords(keywords:Union[str, List[str]]) -> bool:
    if isinstance(keywords, str):
        kw_list = keywords.split(",")
    else:
        kw_list = keywords
    if len(kw_list) == 0:
        return False, "No keywords found"
    if len(kw_list) > 10:
        return False, f"Expected 3-7 keywords, got {len(kw_list)}"
    return True, "Keywords are valid"

def validate_structured_summary(summary) -> bool:
    if not isinstance(summary, list):
        return False, f"Summary is {type(summary)}, expected List"
    if len(summary) == 0:
        return False, "Summary is empty"
    for i, item in enumerate(summary):
        if not isinstance(item, dict):
            return False, f"Summary item {i} is {type(item)}, expected Dict"
        if "topic" not in item:
            return False, f"Summary item {i} does not contain 'topic' key"
        if not isinstance(item["topic"], str):
            return False, f"Summary item {i} has 'topic' key with {type(item['topic'])} value, expected str"
        if item["topic"] == "":
            return False, f"Summary item {i} has empty 'topic' key"
        if "points" not in item:
            return False, f"Summary item {i} does not contain 'points' key"
        if not isinstance(item["points"], list):
            return False, f"Summary item {i} has 'points' key with {type(item['points'])} value, expected List"
        for j, point in enumerate(item["points"]):
            if not isinstance(point, str):
                return False, f"Summary item {i} has 'points' key with {type(point)} value at {j} position, expected str"
            if point == "":
                return False, f"Summary item {i} has empty string at {j} position in 'points' key"
    return True, "Summary is valid"