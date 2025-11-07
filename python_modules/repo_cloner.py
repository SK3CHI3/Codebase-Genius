"""
Repository cloning utilities for Codebase Genius.
Handles cloning GitHub repositories to temporary directories.
"""

import os
import tempfile
import shutil
from pathlib import Path
from git import Repo, GitCommandError
import requests
from urllib.parse import urlparse


def validate_github_url(url: str) -> dict:
    """
    Validate that a URL is a valid GitHub repository URL.
    
    Args:
        url: GitHub repository URL
        
    Returns:
        dict with 'valid' (bool) and 'error' (str) keys
    """
    try:
        parsed = urlparse(url)
        if parsed.netloc not in ['github.com', 'www.github.com']:
            return {'valid': False, 'error': 'URL must be a GitHub repository'}
        
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) < 2:
            return {'valid': False, 'error': 'Invalid GitHub URL format'}
        
        # Check if repository is accessible
        api_url = f"https://api.github.com/repos/{path_parts[0]}/{path_parts[1]}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 404:
            return {'valid': False, 'error': 'Repository not found or is private'}
        elif response.status_code != 200:
            return {'valid': False, 'error': f'GitHub API error: {response.status_code}'}
        
        return {'valid': True, 'error': None, 'owner': path_parts[0], 'repo': path_parts[1]}
    except Exception as e:
        return {'valid': False, 'error': f'Error validating URL: {str(e)}'}


def clone_repository(repo_url: str, output_dir: str = None) -> dict:
    """
    Clone a GitHub repository to a temporary directory.
    
    Args:
        repo_url: GitHub repository URL
        output_dir: Optional directory to clone into (defaults to temp directory)
        
    Returns:
        dict with 'success' (bool), 'path' (str), 'error' (str), 'repo_name' (str)
    """
    try:
        # Validate URL first
        validation = validate_github_url(repo_url)
        if not validation['valid']:
            return {
                'success': False,
                'error': validation['error'],
                'path': None,
                'repo_name': None
            }
        
        # Determine output directory
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix='codebase_genius_')
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        # Extract repo name from URL
        parsed = urlparse(repo_url)
        repo_name = parsed.path.strip('/').split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        
        clone_path = os.path.join(output_dir, repo_name)
        
        # Clone repository
        try:
            Repo.clone_from(repo_url, clone_path)
            return {
                'success': True,
                'path': clone_path,
                'error': None,
                'repo_name': repo_name,
                'owner': validation.get('owner'),
                'repo': validation.get('repo')
            }
        except GitCommandError as e:
            return {
                'success': False,
                'error': f'Git clone error: {str(e)}',
                'path': None,
                'repo_name': repo_name
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'path': None,
            'repo_name': None
        }


def cleanup_repository(path: str) -> bool:
    """
    Remove a cloned repository directory.
    
    Args:
        path: Path to the repository directory
        
    Returns:
        bool indicating success
    """
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
        return True
    except Exception as e:
        print(f"Error cleaning up repository: {e}")
        return False


