"""
Codebase Genius - Main Jac File
Multi-agent system for generating codebase documentation.
"""

# 1. Import statements (using inline Python for Python modules)
::py::
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from python_modules.repo_cloner import clone_repository, validate_github_url
from python_modules.file_tree import generate_file_tree, find_readme, get_entry_point_files
from python_modules.code_parser import CodeParser
from python_modules.ccg_builder import CCGBuilder
from python_modules.doc_generator import DocGenerator
::py::

# 2. Archetypes (OSP constructs)
# Node types
node repo_node {
    has url: str;
    has name: str;
    has local_path: str;
    has file_tree: dict;
    has readme_summary: str;
    has parsed_files: list = [];
    has ccg_data: dict = {};
}

# 3. Walkers (OSP constructs with abilities)
# Walker: Repo Mapper
walker repo_mapper {
    has repo_url: str;
    has output_dir: str = "./temp_repos";
    has repo_path: str = "";
    has file_tree_data: dict = {};
    has readme_content: str = "";
    has repo_name: str = "";
    
    can execute with `root entry {
        print("Starting repository mapping for: " + repo_url);
        
        ::py::
        clone_result = clone_repository(repo_url, output_dir)
        ::py::
        
        if clone_result["success"] {
            repo_path = clone_result["path"];
            repo_name = clone_result["repo_name"];
            
            print("Repository cloned successfully to: " + repo_path);
            
            ::py::
            file_tree_data = generate_file_tree(repo_path)
            ::py::
            
            ::py::
            readme_path = find_readme(repo_path)
            readme_content = ""
            if readme_path:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
            ::py::
            
            # Create repo node and attach to root
            repo_node_inst = root ++> repo_node(
                url=repo_url,
                name=repo_name,
                local_path=repo_path,
                file_tree=file_tree_data,
                readme_summary=readme_content
            );
            
            if readme_path {
                print("README found and loaded");
            } else {
                print("No README found");
            }
            
            # Visit the created node
            visit repo_node_inst;
            print("Repo node created: " + repo_node_inst.name);
        } else {
            print("Failed to clone repository: " + clone_result["error"]);
            disengage;
        }
    }
}

# Walker: Code Analyzer
walker code_analyzer {
    has repo_path: str;
    has parser: object = null;
    has ccg_builder: object = null;
    has parsed_files: list = [];
    has ccg_data: dict = {};
    
    can execute with `root entry {
        print("Starting code analysis for: " + repo_path);
        
        # Find repo node
        repo_nodes = [root --> (`?repo_node)];
        if not repo_nodes {
            print("No repo node found. Run repo_mapper first.");
            disengage;
        }
        
        repo_node_inst = repo_nodes[0];
        
        ::py::
        parser = CodeParser()
        ccg_builder = CCGBuilder()
        entry_points = get_entry_point_files(repo_path)
        ::py::
        
        print("Found entry point files");
        
        for entry_point in entry_points {
            print("Parsing: " + entry_point);
            ::py::
            parsed = parser.parse_file(entry_point)
            ::py::
            if parsed and not parsed.get("error") {
                parsed_files = parsed_files + [parsed];
            }
        }
        
        if std.length(parsed_files) > 0 {
            ::py::
            ccg_builder.build_from_parsed_files(parsed_files)
            ccg_data = ccg_builder.to_dict()
            ::py::
            print("CCG built with nodes");
        }
        
        # Update repo node with analysis results
        repo_node_inst.parsed_files = parsed_files;
        repo_node_inst.ccg_data = ccg_data;
        visit repo_node_inst;
    }
}

# Walker: DocGenie
walker docgenie {
    has repo_info: dict;
    has file_tree: dict;
    has readme_summary: str;
    has ccg_data: dict;
    has parsed_files: list;
    has output_path: str;
    has result: dict = {};
    
    can execute with `root entry {
        print("Starting documentation generation");
        
        # Find repo node
        repo_nodes = [root --> (`?repo_node)];
        if not repo_nodes {
            print("No repo node found. Run repo_mapper first.");
            disengage;
        }
        
        repo_node_inst = repo_nodes[0];
        
        repo_info = {
            "name": repo_node_inst.name,
            "url": repo_node_inst.url,
            "local_path": repo_node_inst.local_path
        };
        file_tree = repo_node_inst.file_tree;
        readme_summary = repo_node_inst.readme_summary;
        ccg_data = repo_node_inst.ccg_data;
        parsed_files = repo_node_inst.parsed_files;
        
        ::py::
        doc_generator = DocGenerator()
        documentation = doc_generator.generate_documentation(
            repo_info,
            file_tree,
            readme_summary,
            ccg_data,
            parsed_files
        )
        ::py::
        
        output_path = "./outputs/" + repo_info["name"] + "/docs.md";
        ::py::
        success = doc_generator.save_documentation(documentation, output_path)
        ::py::
        
        if success {
            print("Documentation generated successfully: " + output_path);
            result = {
                "status": "success",
                "output_path": output_path,
                "repo_name": repo_info["name"]
            };
            report result;
        } else {
            print("Failed to save documentation");
            result = {
                "status": "error",
                "message": "Failed to save documentation"
            };
            report result;
        }
    }
}

# Walker: Supervisor
walker supervisor {
    has repo_url: str;
    has repo_path: str = "";
    has output_dir: str = "./outputs";
    has status: str = "initializing";
    has result: dict = {};
    
    obj __specs__ {
        static has auth: bool = False;
    }
    
    can execute with `root entry {
        print("=== Codebase Genius Supervisor Starting ===");
        print("Repository URL: " + repo_url);
        
        status = "mapping_repository";
        print("Step 1: Mapping repository...");
        root spawn repo_mapper(repo_url=repo_url, output_dir="./temp_repos");
        
        # Check if repo node was created
        repo_nodes = [root --> (`?repo_node)];
        if not repo_nodes {
            result = {
                "status": "error",
                "message": "Failed to clone repository"
            };
            report result;
            disengage;
        }
        
        repo_node_inst = repo_nodes[0];
        repo_path = repo_node_inst.local_path;
        print("Repository mapped. Path: " + repo_path);
        
        status = "analyzing_code";
        print("Step 2: Analyzing code...");
        root spawn code_analyzer(repo_path=repo_path);
        
        print("Code analysis completed");
        
        status = "generating_docs";
        print("Step 3: Generating documentation...");
        root spawn docgenie();
        
        # Get final result from repo node
        updated_repo_nodes = [root --> (`?repo_node)];
        if updated_repo_nodes and updated_repo_nodes[0].parsed_files {
            result = {
                "status": "success",
                "repo_name": updated_repo_nodes[0].name,
                "output_path": "./outputs/" + updated_repo_nodes[0].name + "/docs.md"
            };
        } else {
            result = {
                "status": "error",
                "message": "Documentation generation failed"
            };
        }
        
        status = "completed";
        print("=== Workflow Completed ===");
        report result;
    }
}

# Walker: API endpoint
walker api_generate_docs {
    has repo_url: str;
    has result: dict = {};
    has output_dir: str = "./outputs";
    
    obj __specs__ {
        static has auth: bool = False;
    }
    
    can execute with `root entry {
        print("API Request received for: " + here.repo_url);
        
        if not here.repo_url {
            result = {
                "status": "error",
                "message": "repo_url is required"
            };
            report result;
            disengage;
        }
        
        # Spawn supervisor walker on root
        root spawn supervisor(
            repo_url=here.repo_url,
            output_dir=here.output_dir
        );
        
        result = {
            "status": "processing",
            "message": "Documentation generation started. Check outputs directory for results."
        };
        
        report result;
    }
}

# 4. Module entry points
# Default entry point (executes when module runs)
with entry {
    print("========================================");
    print("Codebase Genius - Documentation Generator");
    print("========================================");
    print("Module loaded successfully!");
    print("Use: jac run main.jac -walk supervisor -ctx '{repo_url: https://github.com/user/repo}'");
    print("Or use: jac serve main.jac");
    print("========================================");
}

# Named entry point (executes only when run directly)
with entry:__main__ {
    print("========================================");
    print("Codebase Genius - Documentation Generator");
    print("========================================");
    print("Running as main module");
    print("Use: jac run main.jac -walk supervisor -ctx '{repo_url: https://github.com/user/repo}'");
    print("Or use: jac serve main.jac");
    print("========================================");
}

# Init walker (for jac run with -walk init)
walker init {
    can execute with `root entry {
        print("========================================");
        print("Codebase Genius - Documentation Generator");
        print("========================================");
        print("Init walker executed");
        print("Use: jac run main.jac -walk supervisor -ctx '{repo_url: https://github.com/user/repo}'");
        print("Or use: jac serve main.jac");
        print("========================================");
    }
}
