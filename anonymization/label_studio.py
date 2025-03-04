import json
import re
import random

def tag2labelstudio(path):
    with open(path) as f:
        data = json.load(f)
        
    label_studio_data = []

    for dialog_id, dialog in data.items():
        for i, turn in enumerate(dialog):
            parsed_text = tag2annot(turn)
            label_studio_data.append({
                "data": {"text": parsed_text["text"], "id": f"{dialog_id}_{i}_{path}", "mistake":False},
                #"annotations":parsed_text["annotations"],
                "predictions":parsed_text["annotations"]
                })
    
    filename = path.split("/")[-1]
    with open(f"labelstudio/{filename}", "w") as f:
        data = json.dump(label_studio_data, f, ensure_ascii=False)
        
def tag2annot(text):
        # Regular expression to find entities (supporting multi-word entities)
        pattern = re.compile(r'<(.*?)>(.*?)</\1>', re.DOTALL)
        
        # Initialize the result dictionary
        result = {"text": "", "annotations": [{"id": random.randint(0, int(1e6)), "result": []}]}  # Start with an empty text
        
        # Find all matches and process them
        last_index = 0
        entity_count = {}  # To track unique entities
        orig_text = text  # Keep the original text for reference
        
        for match in pattern.finditer(text):
            entity_type = match.group(1)
            entity_value = match.group(2).strip()  # Remove leading/trailing whitespace
            
            # Add non-entity text to the result text
            result["text"] += orig_text[last_index:match.start()] + entity_value
            
            # Calculate start and end positions of the entity in the clean text without tags
            start = len(result["text"]) - len(entity_value)  # Start position in the clean text
            end = len(result["text"])  # End position in the clean text
            
            # Create a unique key for the entity
            entity_key = (entity_value, entity_type)
            if entity_key not in entity_count:
                entity_count[entity_key] = len(entity_count) + 1
            
            # Add the entity annotation to the result
            result["annotations"][0]["result"].append({
                    "value": {
                        "start": start,
                        "end": end,
                        "text": entity_value,
                        "labels": [entity_type]
                    },
                    "id": "".join(random.choice("abcdefghijklmnopqrstuvxyz") for _ in range (10)),
                    "from_name": "label",
                    "to_name": "text",
                    "type": "labels",
                    "origin": "manual"
        }
            )

            
            # Update last index
            last_index = match.end()
        
        # Add the remaining text to the result
        result["text"] += orig_text[last_index:]
        
        return result


for path in [
    "raw/deepseek_addresses.json",
    "raw/gpt4o_addresses.json",
    "raw/gemini_addresses.json",
]:
    tag2labelstudio(path)