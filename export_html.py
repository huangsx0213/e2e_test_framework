import os

html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Automatic Testing Framework</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            color: #333;
        }}
        .code-container {{
            background-color: #282c34;
            color: #abb2bf;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            overflow-x: auto;
        }}
        .code-container pre {{
            margin: 0;
        }}
        .class-header {{
            font-size: 1.5em;
            color: #61dafb;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <h1>API Automatic Testing Framework</h1>
    {code_blocks}
</body>
</html>
'''

code_block_template = '''<div class="code-container">
    <div class="class-header">{file_name}</div>
    <pre>{code_content}</pre>
</div>
'''

def read_files(directory='.', exclude_files=None, exclude_directories=None):
    if exclude_files is None:
        exclude_files = []
    if exclude_directories is None:
        exclude_directories = set()

    supported_extensions = ('.py', '.json', '.yaml', '.yml', '.xml')
    files_list = []
    for root, dirs, files in os.walk(directory):
        # Modify dirs in place to exclude specified directories
        dirs[:] = [d for d in dirs if d not in exclude_directories]
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(supported_extensions) and file_path not in exclude_files:
                files_list.append(file_path)
    files_list.sort()  # Sort the list of files
    return files_list

def escape_html(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def generate_code_blocks(files_list):
    code_blocks = ''
    for file_path in files_list:
        with open(file_path, 'r', encoding='utf-8') as file:
            code_content = escape_html(file.read())
            code_block = code_block_template.format(file_name=file_path, code_content=code_content)
            code_blocks += code_block + '\n'
    return code_blocks

def generate_html_file(html_content, output_file='index.html'):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_content)

if __name__ == "__main__":
    # Define files and directories to exclude
    exclude_files = [
        '.\export_html.py',
        '.\export_code.py'
        # Add more file paths as needed
    ]
    exclude_directories = {'venv', '.idea', '__pycache__', '.git'}

    files_list = read_files(exclude_files=exclude_files, exclude_directories=exclude_directories)
    code_blocks = generate_code_blocks(files_list)
    html_content = html_template.format(code_blocks=code_blocks)
    generate_html_file(html_content)
    print(f"HTML file 'code_files.html' generated successfully.")
