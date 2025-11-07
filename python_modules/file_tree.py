"""
File tree generation utilities for Codebase Genius.
Generates structured representations of repository file trees.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional


# Directories and files to ignore
IGNORE_PATTERNS = {
    '.git', '.svn', '.hg',  # Version control
    'node_modules', '__pycache__', '.pytest_cache',  # Dependencies/cache
    '.venv', 'venv', 'env',  # Virtual environments
    '.idea', '.vscode', '.vs',  # IDE files
    'dist', 'build', '.eggs', '*.egg-info',  # Build artifacts
    '.DS_Store', 'Thumbs.db',  # OS files
    '*.pyc', '*.pyo', '*.pyd',  # Python bytecode
}


def should_ignore(path: str) -> bool:
    """
    Check if a path should be ignored.
    
    Args:
        path: File or directory path
        
    Returns:
        bool indicating if path should be ignored
    """
    path_parts = Path(path).parts
    for part in path_parts:
        if part in IGNORE_PATTERNS or part.startswith('.'):
            # Check if it's a hidden file/dir (but allow .github, .gitignore, etc. in root)
            if len(path_parts) > 1 and part.startswith('.'):
                return True
            if part in IGNORE_PATTERNS:
                return True
    return False


def generate_file_tree(repo_path: str, max_depth: int = 10) -> Dict:
    """
    Generate a structured file tree representation of a repository.
    
    Args:
        repo_path: Path to the repository root
        max_depth: Maximum depth to traverse
        
    Returns:
        dict representing the file tree structure
    """
    tree = {
        'name': os.path.basename(repo_path),
        'type': 'directory',
        'path': repo_path,
        'children': []
    }
    
    def build_tree(current_path: str, current_node: Dict, depth: int = 0):
        if depth >= max_depth:
            return
        
        try:
            items = sorted(os.listdir(current_path))
            for item in items:
                item_path = os.path.join(current_path, item)
                
                if should_ignore(item_path):
                    continue
                
                if os.path.isdir(item_path):
                    child = {
                        'name': item,
                        'type': 'directory',
                        'path': item_path,
                        'children': []
                    }
                    build_tree(item_path, child, depth + 1)
                    current_node['children'].append(child)
                else:
                    file_ext = os.path.splitext(item)[1]
                    child = {
                        'name': item,
                        'type': 'file',
                        'path': item_path,
                        'extension': file_ext,
                        'size': os.path.getsize(item_path) if os.path.exists(item_path) else 0
                    }
                    current_node['children'].append(child)
        except PermissionError:
            pass  # Skip directories we can't access
    
    build_tree(repo_path, tree)
    return tree


def get_file_tree_string(tree: Dict, prefix: str = "", is_last: bool = True) -> str:
    """
    Convert file tree dict to a string representation.
    
    Args:
        tree: File tree dictionary
        prefix: Prefix for tree visualization
        is_last: Whether this is the last child
        
    Returns:
        String representation of the file tree
    """
    connector = "└── " if is_last else "├── "
    result = prefix + connector + tree['name'] + "\n"
    
    if tree['type'] == 'directory' and tree['children']:
        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(tree['children']):
            is_last_child = (i == len(tree['children']) - 1)
            result += get_file_tree_string(child, new_prefix, is_last_child)
    
    return result


def find_readme(repo_path: str) -> Optional[str]:
    """
    Find README file in repository.
    
    Args:
        repo_path: Path to repository root
        
    Returns:
        Path to README file or None
    """
    readme_names = ['README.md', 'README.rst', 'README.txt', 'README', 'readme.md']
    
    for name in readme_names:
        readme_path = os.path.join(repo_path, name)
        if os.path.exists(readme_path):
            return readme_path
    
    return None


def get_entry_point_files(repo_path: str) -> List[str]:
    """
    Find entry point files (main.py, app.py, etc.) in repository.
    
    Args:
        repo_path: Path to repository root
        
    Returns:
        List of entry point file paths
    """
    entry_points = []
    entry_patterns = ['main.py', 'app.py', 'run.py', 'server.py', 'index.py', 'main.jac']
    
    for root, dirs, files in os.walk(repo_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d))]
        
        for file in files:
            if file in entry_patterns:
                entry_points.append(os.path.join(root, file))
    
    return entry_points


