import os
import re
import json
from collections import defaultdict

TEMPLATE_DIR = '../../configs/body_templates'
OUTPUT_DIR = '../../output'


def extract_placeholders(template_content):
    # 提取{{}}中的占位符，支持嵌套
    placeholders = re.findall(r'\{\{\s*([^}]+?)\s*\}\}', template_content)
    return placeholders


def nest_keys(keys):
    nested_dict = {}
    for key in keys:
        parts = key.split('.')
        current_level = nested_dict
        for part in parts[:-1]:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]
        current_level[parts[-1]] = ""
    return nested_dict


def merge_dicts(dict1, dict2):
    for key in dict2:
        if key in dict1:
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                merge_dicts(dict1[key], dict2[key])
            else:
                dict1[key] = dict2[key]
        else:
            dict1[key] = dict2[key]
    return dict1


def generate_json_from_template(template_filename):
    template_path = os.path.join(TEMPLATE_DIR, template_filename)
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"The template file {template_filename} does not exist in {TEMPLATE_DIR}")

    with open(template_path, 'r', encoding='utf-8') as file:
        template_content = file.read()

    placeholders = extract_placeholders(template_content)
    nested_structure = {}

    for placeholder in placeholders:
        nested_dict = nest_keys([placeholder])
        nested_structure = merge_dicts(nested_structure, nested_dict)

    output_path = os.path.join(OUTPUT_DIR, f"{os.path.splitext(template_filename)[0]}_placeholders.json")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as outfile:
        json.dump(nested_structure, outfile, indent=4)

    print(f"Generated JSON file with placeholders: {output_path}")


if __name__ == "__main__":
    template_filename = 'pacs.008_out.xml'  # 你可以更改为你想指定的模板文件名
    generate_json_from_template(template_filename)