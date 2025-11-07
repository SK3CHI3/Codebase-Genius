"""
Code Context Graph (CCG) builder for Codebase Genius.
Builds a graph representation of code relationships.
"""

from typing import Dict, List, Set, Tuple
from collections import defaultdict


class CCGNode:
    """Represents a node in the Code Context Graph."""
    
    def __init__(self, node_id: str, node_type: str, name: str, **kwargs):
        self.id = node_id
        self.type = node_type  # 'module', 'class', 'function', 'file'
        self.name = name
        self.properties = kwargs
        self.edges = []  # List of edge tuples (target_id, edge_type)
    
    def add_edge(self, target_id: str, edge_type: str):
        """Add an edge to another node."""
        if (target_id, edge_type) not in self.edges:
            self.edges.append((target_id, edge_type))
    
    def to_dict(self) -> Dict:
        """Convert node to dictionary."""
        return {
            'id': self.id,
            'type': self.type,
            'name': self.name,
            'properties': self.properties,
            'edges': self.edges
        }


class CCGBuilder:
    """Builds a Code Context Graph from parsed code structures."""
    
    def __init__(self):
        self.nodes: Dict[str, CCGNode] = {}
        self.node_counter = 0
    
    def _generate_id(self, prefix: str = "node") -> str:
        """Generate a unique node ID."""
        self.node_counter += 1
        return f"{prefix}_{self.node_counter}"
    
    def add_module(self, file_path: str, module_name: str, **kwargs) -> str:
        """Add a module node to the graph."""
        node_id = self._generate_id("module")
        node = CCGNode(node_id, 'module', module_name, file_path=file_path, **kwargs)
        self.nodes[node_id] = node
        return node_id
    
    def add_class(self, module_id: str, class_name: str, bases: List[str] = None, **kwargs) -> str:
        """Add a class node to the graph."""
        node_id = self._generate_id("class")
        node = CCGNode(node_id, 'class', class_name, bases=bases or [], **kwargs)
        self.nodes[node_id] = node
        
        # Link class to module
        if module_id in self.nodes:
            self.nodes[module_id].add_edge(node_id, 'contains')
            node.add_edge(module_id, 'belongs_to')
        
        # Link inheritance relationships
        if bases:
            for base in bases:
                # Try to find base class in graph
                base_node = self._find_node_by_name(base, 'class')
                if base_node:
                    node.add_edge(base_node.id, 'inherits_from')
                    base_node.add_edge(node_id, 'inherited_by')
        
        return node_id
    
    def add_function(self, parent_id: str, function_name: str, parent_type: str = 'module', **kwargs) -> str:
        """Add a function node to the graph."""
        node_id = self._generate_id("function")
        node = CCGNode(node_id, 'function', function_name, **kwargs)
        self.nodes[node_id] = node
        
        # Link function to parent (module or class)
        if parent_id in self.nodes:
            self.nodes[parent_id].add_edge(node_id, 'contains')
            node.add_edge(parent_id, 'belongs_to')
        
        return node_id
    
    def add_call_relationship(self, caller_id: str, callee_id: str):
        """Add a function call relationship."""
        if caller_id in self.nodes and callee_id in self.nodes:
            self.nodes[caller_id].add_edge(callee_id, 'calls')
            self.nodes[callee_id].add_edge(caller_id, 'called_by')
    
    def add_import_relationship(self, importer_id: str, imported_id: str):
        """Add an import relationship between modules."""
        if importer_id in self.nodes and imported_id in self.nodes:
            self.nodes[importer_id].add_edge(imported_id, 'imports')
            self.nodes[imported_id].add_edge(importer_id, 'imported_by')
    
    def _find_node_by_name(self, name: str, node_type: str = None) -> CCGNode:
        """Find a node by name and optionally type."""
        for node in self.nodes.values():
            if node.name == name:
                if node_type is None or node.type == node_type:
                    return node
        return None
    
    def find_nodes_by_type(self, node_type: str) -> List[CCGNode]:
        """Find all nodes of a specific type."""
        return [node for node in self.nodes.values() if node.type == node_type]
    
    def get_node(self, node_id: str) -> CCGNode:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def query_relationships(self, node_id: str, relationship_type: str = None) -> List[Tuple[str, str]]:
        """
        Query relationships from a node.
        
        Args:
            node_id: ID of the node to query
            relationship_type: Optional filter for relationship type
            
        Returns:
            List of (target_id, edge_type) tuples
        """
        if node_id not in self.nodes:
            return []
        
        node = self.nodes[node_id]
        if relationship_type:
            return [(target, edge_type) for target, edge_type in node.edges if edge_type == relationship_type]
        return node.edges
    
    def get_callers(self, function_name: str) -> List[str]:
        """Get all functions that call a given function."""
        function_node = self._find_node_by_name(function_name, 'function')
        if not function_node:
            return []
        
        callers = []
        for node in self.nodes.values():
            for target_id, edge_type in node.edges:
                if target_id == function_node.id and edge_type == 'calls':
                    callers.append(node.name)
        return callers
    
    def get_callees(self, function_name: str) -> List[str]:
        """Get all functions called by a given function."""
        function_node = self._find_node_by_name(function_name, 'function')
        if not function_node:
            return []
        
        callees = []
        for target_id, edge_type in function_node.edges:
            if edge_type == 'calls':
                target_node = self.nodes.get(target_id)
                if target_node:
                    callees.append(target_node.name)
        return callees
    
    def to_dict(self) -> Dict:
        """Convert the entire graph to a dictionary."""
        return {
            'nodes': {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            'node_count': len(self.nodes)
        }
    
    def build_from_parsed_files(self, parsed_files: List[Dict]):
        """
        Build CCG from a list of parsed file structures.
        
        Args:
            parsed_files: List of parsed file dictionaries from code_parser
        """
        # First pass: create all modules
        module_map = {}  # file_path -> module_id
        
        for parsed in parsed_files:
            if 'error' in parsed:
                continue
            
            module_id = self.add_module(
                parsed['file_path'],
                parsed['module_name']
            )
            module_map[parsed['file_path']] = module_id
        
        # Second pass: add classes and functions
        class_map = {}  # (module_id, class_name) -> class_id
        function_map = {}  # (parent_id, function_name) -> function_id
        
        for parsed in parsed_files:
            if 'error' in parsed or parsed['file_path'] not in module_map:
                continue
            
            module_id = module_map[parsed['file_path']]
            
            # Add classes
            for class_info in parsed.get('classes', []):
                class_id = self.add_class(
                    module_id,
                    class_info['name'],
                    class_info.get('bases', []),
                    line_start=class_info.get('line_start'),
                    line_end=class_info.get('line_end')
                )
                class_map[(module_id, class_info['name'])] = class_id
                
                # Add methods
                for method in class_info.get('methods', []):
                    method_id = self.add_function(
                        class_id,
                        method['name'],
                        'class',
                        line_start=method.get('line_start'),
                        line_end=method.get('line_end')
                    )
                    function_map[(class_id, method['name'])] = method_id
            
            # Add top-level functions
            for func_info in parsed.get('functions', []):
                func_id = self.add_function(
                    module_id,
                    func_info['name'],
                    'module',
                    line_start=func_info.get('line_start'),
                    line_end=func_info.get('line_end')
                )
                function_map[(module_id, func_info['name'])] = func_id
        
        # Third pass: resolve imports and calls (simplified - would need more analysis)
        # This is a placeholder - full implementation would require deeper code analysis
        return self

