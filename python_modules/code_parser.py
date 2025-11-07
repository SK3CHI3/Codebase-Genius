"""
Code parsing utilities using Tree-sitter for Codebase Genius.
Parses Python and Jac code to extract classes, functions, and relationships.
"""

import os
from typing import Dict, List, Optional
from tree_sitter import Language, Parser

# Try to import tree-sitter languages
try:
    import tree_sitter_python as tspython
    PYTHON_LANGUAGE = Language(tspython.language())
    PYTHON_AVAILABLE = True
except ImportError:
    PYTHON_AVAILABLE = False
    PYTHON_LANGUAGE = None

# For Jac, we'll need a custom parser or use a simpler approach
# For now, we'll use a basic regex-based parser for Jac


class CodeParser:
    """Parser for extracting code structure from source files."""
    
    def __init__(self):
        self.python_parser = None
        if PYTHON_AVAILABLE:
            self.python_parser = Parser(PYTHON_LANGUAGE)
    
    def parse_python_file(self, file_path: str) -> Dict:
        """
        Parse a Python file and extract structure.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            dict with classes, functions, imports, and relationships
        """
        if not PYTHON_AVAILABLE or not self.python_parser:
            return self._parse_python_simple(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source_code = f.read()
            
            tree = self.python_parser.parse(bytes(source_code, 'utf8'))
            root_node = tree.root_node
            
            result = {
                'file_path': file_path,
                'module_name': os.path.splitext(os.path.basename(file_path))[0],
                'classes': [],
                'functions': [],
                'imports': [],
                'relationships': []
            }
            
            self._extract_python_structure(root_node, source_code, result)
            return result
            
        except Exception as e:
            # Fallback to simple parsing
            return self._parse_python_simple(file_path)
    
    def _extract_python_structure(self, node, source_code: str, result: Dict):
        """Recursively extract structure from Python AST."""
        if node.type == 'class_definition':
            class_name = self._get_node_text(node.child_by_field_name('name'), source_code)
            bases = []
            if node.child_by_field_name('superclasses'):
                for child in node.child_by_field_name('superclasses').children:
                    if child.type == 'identifier':
                        bases.append(self._get_node_text(child, source_code))
            
            class_info = {
                'name': class_name,
                'line_start': node.start_point[0] + 1,
                'line_end': node.end_point[0] + 1,
                'bases': bases,
                'methods': []
            }
            
            # Extract methods
            for child in node.children:
                if child.type == 'block':
                    for stmt in child.children:
                        if stmt.type == 'function_definition':
                            method_name = self._get_node_text(
                                stmt.child_by_field_name('name'), source_code
                            )
                            class_info['methods'].append({
                                'name': method_name,
                                'line_start': stmt.start_point[0] + 1,
                                'line_end': stmt.end_point[0] + 1
                            })
            
            result['classes'].append(class_info)
            
        elif node.type == 'function_definition':
            func_name = self._get_node_text(node.child_by_field_name('name'), source_code)
            # Only add top-level functions (not methods)
            if node.parent and node.parent.type != 'class_definition':
                result['functions'].append({
                    'name': func_name,
                    'line_start': node.start_point[0] + 1,
                    'line_end': node.end_point[0] + 1
                })
        
        elif node.type == 'import_statement' or node.type == 'import_from_statement':
            import_text = self._get_node_text(node, source_code)
            result['imports'].append(import_text)
        
        # Recursively process children
        for child in node.children:
            self._extract_python_structure(child, source_code, result)
    
    def _get_node_text(self, node, source_code: str) -> str:
        """Extract text from a node."""
        if node is None:
            return ""
        start_byte = node.start_byte
        end_byte = node.end_byte
        return source_code[start_byte:end_byte].strip()
    
    def _parse_python_simple(self, file_path: str) -> Dict:
        """Simple regex-based Python parser as fallback."""
        import re
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            result = {
                'file_path': file_path,
                'module_name': os.path.splitext(os.path.basename(file_path))[0],
                'classes': [],
                'functions': [],
                'imports': [],
                'relationships': []
            }
            
            for i, line in enumerate(lines, 1):
                # Match class definitions
                class_match = re.match(r'^\s*class\s+(\w+)(?:\(([^)]+)\))?', line)
                if class_match:
                    class_name = class_match.group(1)
                    bases_str = class_match.group(2) if class_match.group(2) else ""
                    bases = [b.strip() for b in bases_str.split(',')] if bases_str else []
                    result['classes'].append({
                        'name': class_name,
                        'line_start': i,
                        'line_end': i,  # Will be updated if we track better
                        'bases': bases,
                        'methods': []
                    })
                
                # Match function definitions (not indented = top-level)
                func_match = re.match(r'^\s*def\s+(\w+)', line)
                if func_match and not line.startswith('    ') and not line.startswith('\t'):
                    result['functions'].append({
                        'name': func_match.group(1),
                        'line_start': i,
                        'line_end': i
                    })
                
                # Match imports
                import_match = re.match(r'^\s*(?:from\s+[\w.]+)?\s*import\s+(.+)', line)
                if import_match:
                    result['imports'].append(import_match.group(1))
            
            return result
        except Exception as e:
            return {
                'file_path': file_path,
                'module_name': os.path.splitext(os.path.basename(file_path))[0],
                'classes': [],
                'functions': [],
                'imports': [],
                'relationships': [],
                'error': str(e)
            }
    
    def parse_jac_file(self, file_path: str) -> Dict:
        """
        Parse a Jac file and extract structure.
        Note: This is a basic implementation - may need enhancement.
        
        Args:
            file_path: Path to Jac file
            
        Returns:
            dict with walkers, nodes, and relationships
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            result = {
                'file_path': file_path,
                'module_name': os.path.splitext(os.path.basename(file_path))[0],
                'walkers': [],
                'node_types': [],
                'relationships': []
            }
            
            import re
            
            # Extract walker definitions
            walker_pattern = r'walker\s+(\w+)\s*\{'
            for match in re.finditer(walker_pattern, content):
                result['walkers'].append({
                    'name': match.group(1),
                    'line_start': content[:match.start()].count('\n') + 1
                })
            
            # Extract node type definitions
            node_pattern = r'node\s+type\s+(\w+)\s*\{'
            for match in re.finditer(node_pattern, content):
                result['node_types'].append({
                    'name': match.group(1),
                    'line_start': content[:match.start()].count('\n') + 1
                })
            
            return result
        except Exception as e:
            return {
                'file_path': file_path,
                'module_name': os.path.splitext(os.path.basename(file_path))[0],
                'walkers': [],
                'node_types': [],
                'relationships': [],
                'error': str(e)
            }
    
    def parse_file(self, file_path: str) -> Dict:
        """
        Parse a file based on its extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            Parsed structure dict
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.py':
            return self.parse_python_file(file_path)
        elif ext == '.jac':
            return self.parse_jac_file(file_path)
        else:
            return {
                'file_path': file_path,
                'module_name': os.path.basename(file_path),
                'error': f'Unsupported file type: {ext}'
            }


