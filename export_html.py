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
        .code-container, .directory-container {{
            background-color: #282c34;
            color: #abb2bf;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            overflow-x: auto;
            position: relative;
        }}
        .code-container pre, .directory-container pre {{
            margin: 0;
        }}
        .class-header, .directory-header {{
            font-size: 1.5em;
            color: #61dafb;
            margin-bottom: 10px;
        }}
        .copy-button, .return-button {{
            position: absolute;
            right: 20px;
            top: 20px;
            background-color: #61dafb;
            color: #282c34;
            border: none;
            padding: 5px 10px;
            cursor: pointer;
            border-radius: 3px;
            margin-left: 5px;
        }}
        .return-button {{
            right: 100px;
        }}
        .directory a {{
            color: #98c379;
            text-decoration: none;
        }}
        .directory a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <h1>E2E Automatic Testing Framework</h1>
    <div class="directory-container">
        <div class="directory-header">File Directory</div>
        <pre class="directory">{file_structure}</pre>
    </div>
    {code_blocks}
    <script>
        function copyToClipboard(button) {{
            const codeContainer = button.parentElement;
            const code = codeContainer.querySelector('pre').innerText;
            navigator.clipboard.writeText(code).then(() => {{
                button.innerText = 'Copied!';
                setTimeout(() => {{ button.innerText = 'Copy'; }}, 2000);
            }});
        }}
        function returnToDirectory() {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
    </script>
</body>
</html>
'''

code_block_template = '''<div class="code-container" id="{file_id}">
    <div class="class-header">{file_name}</div>
    <button class="copy-button" onclick="copyToClipboard(this)">Copy</button>
    <button class="return-button" onclick="returnToDirectory()">Return</button>
    <pre>{code_content}</pre>
</div>
'''

def read_files(directory='.', exclude_files=None, exclude_directories=None):
    if exclude_files is None:
        exclude_files = []
    if exclude_directories is None:
        exclude_directories = set()

    # Convert exclude_files to absolute paths
    exclude_files = [os.path.abspath(file) for file in exclude_files]

    supported_extensions = ('.py', '.json', '.yaml', '.html', '.xml')
    files_list = []
    for root, dirs, files in os.walk(directory):
        # Modify dirs in place to exclude specified directories
        dirs[:] = [d for d in dirs if d not in exclude_directories]
        for file in files:
            file_path = os.path.abspath(os.path.join(root, file))
            if file.endswith(supported_extensions) and file_path not in exclude_files:
                files_list.append(file_path)
    files_list.sort()  # Sort the list of files
    return files_list

def escape_html(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def generate_code_blocks_and_links(files_list):
    code_blocks = ''
    for file_path in files_list:
        file_id = file_path.replace('\\', '_').replace('/', '_').replace('.', '_')
        with open(file_path, 'r', encoding='utf-8') as file:
            code_content = escape_html(file.read())
            code_block = code_block_template.format(file_id=file_id, file_name=file_path, code_content=code_content)
            code_blocks += code_block + '\n'
    return code_blocks

def generate_file_structure(files_list, directory='.', prefix=''):
    file_structure = ''
    files_set = set(files_list)
    for root, dirs, files in os.walk(directory):
        level = root.replace(directory, '').count(os.sep)
        indent = '│   ' * level + '├── ' if level > 0 else ''
        subindent = '│   ' * (level + 1) + '├── '
        folder_name = os.path.basename(root)
        if any(os.path.abspath(os.path.join(root, f)) in files_set for f in files):  # Check if directory has any included files
            file_structure += f'{indent}{folder_name}/\n'
            for f in files:
                file_path = os.path.abspath(os.path.join(root, f))
                if file_path in files_set:
                    file_id = file_path.replace('\\', '_').replace('/', '_').replace('.', '_')
                    file_structure += f'{subindent}<a href="#{file_id}">{f}</a>\n'
    return file_structure

def generate_html_file(html_content, output_file='report/index.html'):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_content)

if __name__ == "__main__":
    # Define files and directories to exclude
    exclude_files = [
        'export_html.py',
        'export_code.py'
        # Add more file paths as needed
    ]
    exclude_directories = {'venv', '.idea', '__pycache__', '.git', 'report'}

    files_list = read_files(exclude_files=exclude_files, exclude_directories=exclude_directories)
    code_blocks = generate_code_blocks_and_links(files_list)
    file_structure = generate_file_structure(files_list, directory='.')
    html_content = html_template.format(file_structure=file_structure, code_blocks=code_blocks)
    generate_html_file(html_content)
    print(f"HTML file 'report/index.html' generated successfully.")