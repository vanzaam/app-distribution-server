import os
import mimetypes

def is_text_file(filepath):
    """Проверяет, является ли файл текстовым на основе его MIME-типа или расширения."""
    mime_type, _ = mimetypes.guess_type(filepath)
    return (mime_type and mime_type.startswith('text')) or filepath.endswith('.template')

def get_project_structure(project_dir, output_file):
    """Возвращает план проекта (список папок и файлов)."""
    structure = []
    for root, dirs, files in os.walk(project_dir, topdown=True):
        dirs[:] = [d for d in dirs if d != '.git']  # Исключаем .git
        relative_root = os.path.relpath(root, project_dir)
        if relative_root == '.':
            relative_root = 'root'
        structure.append(f"Папка: {relative_root}")
        for file in files:
            if file != os.path.basename(output_file) and file != 'chart.umd.min.js':
                filepath = os.path.join(root, file)
                if is_text_file(filepath):
                    structure.append(f"  Файл: {os.path.join(relative_root, file)}")
    return "\n".join(structure)

def combine_files(project_dir, output_file):
    """Собирает содержимое всех текстовых файлов в один output_file с разделителями."""
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Добавляем план проекта в начало
        outfile.write("=== План проекта ===\n")
        outfile.write(get_project_structure(project_dir, output_file))
        outfile.write("\n====================\n\n")

        for root, dirs, files in os.walk(project_dir, topdown=True):
            dirs[:] = [d for d in dirs if d != '.git']
            for filename in files:
                if filename == os.path.basename(output_file) or filename == 'chart.umd.min.js':
                    continue
                
                filepath = os.path.join(root, filename)
                relative_path = os.path.relpath(filepath, project_dir)
                
                if is_text_file(filepath):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            outfile.write(f"\n\n===== File: {relative_path} =====\n\n")
                            outfile.write(content)
                    except UnicodeDecodeError:
                        print(f"Warning: {relative_path} is not a valid UTF-8 text file, skipping.")
                    except Exception as e:
                        print(f"Error reading {relative_path}: {e}")
                else:
                    print(f"Skipping non-text file: {relative_path}")

def split_file(input_file, output_file, num_parts=5):
    """Разбивает файл на заданное количество частей с полным содержимым файлов, сохраняя контекст."""
    with open(input_file, 'r', encoding='utf-8') as infile:
        content = infile.read()
    
    file_starts = [0]
    current_pos = 0
    while True:
        next_start = content.find("\n\n===== File: ", current_pos)
        if next_start == -1:
            break
        file_starts.append(next_start)
        current_pos = next_start + 1
    file_starts.append(len(content))

    # Распределяем файлы на 5 частей
    total_files = len(file_starts) - 1
    files_per_part = max(1, total_files // num_parts)  # Минимум 1 файл на часть
    parts = []
    for i in range(num_parts):
        start_idx = i * files_per_part
        end_idx = min((i + 1) * files_per_part, total_files) if i < num_parts - 1 else total_files
        if start_idx < total_files:
            parts.append((file_starts[start_idx], file_starts[end_idx]))

    for i, (start, end) in enumerate(parts, 1):
        part_content = content[start:end]
        total_parts = len(parts)
        next_part_info = f"Часть {i} из {total_parts}. " + \
                        (f"Следующая часть ({i+1}) содержит файлы с {os.path.relpath(project_directory, os.getcwd())}/..." 
                         if i < total_parts else "Это последняя часть.")
        output_part = f"combined_part_{chr(ord('a') + i - 1)}.txt"
        with open(output_part, 'w', encoding='utf-8') as outfile:
            outfile.write(part_content)
            outfile.write("\n\n=== Информация о частях ===\n")
            outfile.write(next_part_info)
            outfile.write("\n\n=== План проекта ===\n")
            outfile.write(get_project_structure(project_directory, output_file))
            outfile.write("\n====================\n")
        print(f"Created {output_part} (size: {len(part_content)} symbols)")

if __name__ == "__main__":
    # Укажите путь к директории проекта
    project_directory = "."  # Текущая директория, можно заменить на нужный путь
    output_filename = "combined.txt"
    
    # Проверяем, существует ли директория
    if not os.path.isdir(project_directory):
        print(f"Error: Directory {project_directory} does not exist.")
        exit(1)
    
    print(f"Combining files from {project_directory} into {output_filename}...")
    combine_files(project_directory, output_filename)
    print(f"Done! Output written to {output_filename}")
    
    print(f"Splitting {output_filename} into 5 parts...")
    split_file(output_filename, output_filename, num_parts=5)  # Указываем 5 частей
    print("Splitting completed!")