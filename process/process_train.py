import json
import numpy as np
from collections import defaultdict

class FloatEncoder(json.JSONEncoder):
    def iterencode(self, o, _one_shot=False):
        # Override the float format to limit to 6 decimal places
        def format_float(obj):
            if isinstance(obj, float):
                return format(obj, ".6f")  # Limit to 6 decimal places
            return json.JSONEncoder.default(self, obj)
        
        return super(FloatEncoder, self).iterencode(o, _one_shot)

# Read the JSON file
with open('dataset/train_list.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Dictionary to store total_score values grouped by prompt
prompt_scores = defaultdict(list)

# Process the data
for item in data:
    # Calculate the average of total_score
    total_score_avg = np.mean(item["total_score"])
    
    # Calculate the average for each element in element_score
    element_score_avg = {
        key: round(np.mean(values),6) for key, values in eval(item["element_score"]).items()
    }
    
    # Add averages to the current item
    item["total_score"] = round(total_score_avg,6)
    item["element_score"] = element_score_avg
    item["promt_meaningless"] = round(np.mean(item["promt_meaningless"]),6)
    item["split_confidence"] = round(np.mean(item["split_confidence"]),6)
    item["attribute_confidence"] = round(np.mean(item["attribute_confidence"]),6)
    
    # Store total_score_avg grouped by prompt for variance calculation
    prompt_scores[item["prompt"]].append(round(total_score_avg,6))

# Calculate the variance of total_score_avg for each prompt and add it to the data
for item in data:
    # breakpoint()
    prompt_variance = np.var(prompt_scores[item["prompt"]],ddof=1)
    item["var"] = prompt_variance

# Save the updated data into a single JSON file
with open('dataset/train.json', 'w', encoding='utf-8') as output_file:
    json.dump(data, output_file, ensure_ascii=False, indent=4, cls=FloatEncoder)

