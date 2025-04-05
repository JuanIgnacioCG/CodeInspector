import os


def display_tree(start_path='.', indent='', exclude=None, max_depth=None, current_depth=0):
    if exclude is None:
        exclude = []

    if max_depth is not None and current_depth > max_depth:
        return

    try:
        files = sorted(f for f in os.listdir(start_path) if f not in exclude)
    except FileNotFoundError:
        print(f"{indent}⚠️ Path not found: {start_path}")
        return

    for idx, file in enumerate(files):
        full_path = os.path.join(start_path, file)
        is_last = idx == len(files) - 1
        connector = '└── ' if is_last else '├── '
        print(indent + connector + file)
        if os.path.isdir(full_path):
            new_indent = indent + ('    ' if is_last else '│   ')
            display_tree(full_path, new_indent, exclude, max_depth, current_depth + 1)

if __name__ == '__main__':
    exclude_dirs = ['__pycache__', '.git', '.venv', 'build', 'dist']
    
    # Limit current directory to depth 1
    print("\n📁 Current Directory:")
    display_tree('.', exclude=exclude_dirs, max_depth=1)