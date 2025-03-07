from typing import List, Union
from warnings import warn


def validate(obj, validate_fn):
    isvalid, message = validate_fn(obj)
    if not isvalid:
        warn(message)


def validate_list_structure(list_structure: Union[str, List[str]]) -> bool:
    if isinstance(list_structure, str):
        output_list = list_structure.split(",")
    else:
        output_list = list_structure
    if len(output_list) == 0:
        return False, "No list output found"
    # TODO: подумать нужна ли вообще такая проверка
    # if len(output_list) > 10:
    #     return False, f"Expected 3-7 elements in list output, got {len(output_list)}"
    return True, "list output are valid"


def validate_json_structure(output) -> bool:
    if not isinstance(output, list):
        return False, f"output is {type(output)}, expected List"
    if len(output) == 0:
        return False, "output is empty"
    for i, item in enumerate(output):
        if not isinstance(item, dict):
            return False, f"output item {i} is {type(item)}, expected Dict"
        if "topic" not in item:
            return False, f"output item {i} does not contain 'topic' key"
        if not isinstance(item["topic"], str):
            return (
                False,
                f"output item {i} has 'topic' key with {type(item['topic'])} value, expected str",
            )
        if item["topic"] == "":
            return False, f"output item {i} has empty 'topic' key"
        if "points" not in item:
            return False, f"output item {i} does not contain 'points' key"
        if isinstance(item["points"], list):
            for j, point in enumerate(item["points"]):
                if not isinstance(point, str):
                    return (
                        False,
                        f"output item {i} has 'points' key with {type(point)} value at {j} position, expected str",
                    )
                if point == "":
                    return (
                        False,
                        f"output item {i} has empty string at {j} position in 'points' key",
                    )
        elif not isinstance(item["points"], str):
            return (
                False,
                f"output item {i} has 'points' key with {type(item['points'])} value, expected List or str",
            )
        elif item["points"] == "":
            return False, f"output item {i} has empty string in 'points' key"
    return True, "output is valid"

if __name__ == "__main__":
    import json

    def test_validation_functions():
        with open("test_results.json", "r", encoding="utf-8") as f:
            test_data = json.load(f)

        # Тестирование validate_json_structure
        json_validation_result = validate_json_structure(test_data["structured_summary"]["content"])
        print("Тест validate_json_structure:", json_validation_result)

        # Тестирование validate_list_structure
        list_validation_result = validate_list_structure(test_data["keywords"]["content"])
        print("Тест validate_list_structure:", list_validation_result)
    
    test_validation_functions()