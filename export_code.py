import os

# Function to list all files with specific extensions and exclude certain directories and files
def list_files(directory, extensions, exclude_dirs, exclude_files):
    files_list = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(extensions) and file not in exclude_files:
                files_list.append(os.path.join(root, file))
    return files_list

# Function to write the content of files to a single txt file
def write_contents_to_file(files_list, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for file_path in files_list:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    f.write(f'\n--- Content of: {file_path} ---\n')
                    f.write(file.read())
                    f.write('\n')
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin1') as file:
                    f.write(f'\n--- Content of: {file_path} (read with latin1 encoding) ---\n')
                    f.write(file.read())
                    f.write('\n')

if __name__ == '__main__':
    exclude_scripts = ['__init__.py', 'export_code.py', 'export_html.py', 'gen_temp_default.py', 'web_main.py', 'web_test_executor.py', 'api_main.py']  # Replace with your actual script names
    directory_to_search = '.'
    extensions = ('.py', '.json', '.xml', '.yaml', '.html')
    exclude_directories = {'venv', '.idea', '__pycache__', '.git', 'testing_server', 'output'}

    # Listing the files
    files = list_files(directory_to_search, extensions, exclude_directories, exclude_scripts)

    # Writing the file contents to the output txt file
    output_txt_file = 'output/collected_files_content.txt'
    write_contents_to_file(files, output_txt_file)

    print(f'Content of files has been written to {output_txt_file}.')