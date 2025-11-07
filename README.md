# Codebase Genius

An AI-powered, multi-agent system that automatically generates high-quality documentation for any software repository using Jac (JacLang) and Gemini AI.

## 🎯 Overview

Codebase Genius is a fully functional agentic application that:
- **Clones** GitHub repositories automatically
- **Analyzes** code structure using Tree-sitter parsing
- **Builds** Code Context Graphs (CCG) showing relationships
- **Generates** AI-enhanced markdown documentation with intelligent explanations
- **Exposes** RESTful API endpoints for easy integration

## ✨ Features

- ✅ **Multi-Agent Architecture**: Supervisor orchestrates Repo Mapper, Code Analyzer, and DocGenie agents
- ✅ **AI-Powered Documentation**: Uses Google Gemini AI for intelligent code explanations
- ✅ **Code Context Graph**: Visualizes relationships between functions, classes, and modules
- ✅ **Python & Jac Support**: Optimized for Python and Jac codebases
- ✅ **RESTful API**: HTTP endpoints for easy integration
- ✅ **Error Handling**: Graceful handling of invalid URLs, parsing errors, and API failures

## 📋 Prerequisites

- **Python 3.8+**
- **Jac (JacLang)** runtime - Install with: `pip install jaclang`
- **Git** (for cloning repositories)
- **Google Gemini API Key** (for AI-powered documentation)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/SK3CHI3/Codebase-Genius.git
cd Codebase-Genius
```

### 2. Set Up Virtual Environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**Get your API key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy it to your `.env` file

### 5. Start the Server

```bash
jac serve main.jac
```

The server will start on `http://localhost:8000` (or check the output for the actual port).

## 📖 Usage

### Option 1: Using the API (Recommended)

#### Generate Documentation

**POST** `/walker/api_generate_docs`

```bash
curl -X POST http://localhost:8000/walker/api_generate_docs \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/username/repository"}'
```

**PowerShell:**
```powershell
$body = @{
    repo_url = "https://github.com/username/repository"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/walker/api_generate_docs" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

#### Use Supervisor Walker Directly

**POST** `/walker/supervisor`

```json
{
  "repo_url": "https://github.com/username/repository"
}
```

### Option 2: Using Python Script

For direct testing without the server:

```bash
python generate_docs.py
```

This will generate documentation for the repository specified in the script.

### Option 3: Command Line (Jac)

```bash
jac run main.jac -walk supervisor -ctx '{"repo_url": "https://github.com/username/repo"}'
```

## 📁 Project Structure

```
Codebase-Genius/
├── main.jac                 # Main Jac file with walkers and API endpoints
├── python_modules/          # Python utility modules
│   ├── repo_cloner.py       # Repository cloning
│   ├── file_tree.py         # File tree generation
│   ├── code_parser.py       # Code parsing with Tree-sitter
│   ├── ccg_builder.py       # Code Context Graph builder
│   └── doc_generator.py     # AI-powered documentation generator
├── agents/                  # Agent definitions (reference)
├── outputs/                 # Generated documentation
├── temp_repos/              # Cloned repositories (temporary)
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create this)
├── generate_docs.py         # Standalone documentation generator
└── README.md               # This file
```

## 🏗️ Architecture

### Agents

1. **Supervisor** (`supervisor` walker)
   - Orchestrates the entire workflow
   - Coordinates other agents
   - Manages state and error handling

2. **Repo Mapper** (`repo_mapper` walker)
   - Clones GitHub repositories
   - Generates file tree structure
   - Extracts and summarizes README files

3. **Code Analyzer** (`code_analyzer` walker)
   - Parses source code using Tree-sitter
   - Builds Code Context Graph (CCG)
   - Identifies relationships (calls, inheritance, imports)

4. **DocGenie** (`docgenie` walker)
   - Generates AI-enhanced markdown documentation
   - Uses Gemini AI for intelligent explanations
   - Creates well-organized, human-readable docs

### Workflow

```
1. User provides GitHub URL
   ↓
2. Repo Mapper clones repository
   ↓
3. Code Analyzer parses code and builds CCG
   ↓
4. DocGenie generates AI-enhanced documentation
   ↓
5. Documentation saved to ./outputs/<repo_name>/docs.md
```

## 📝 Generated Documentation Structure

The generated documentation includes:

- **Overview**: AI-generated repository description
- **Repository Structure**: File tree visualization
- **Installation**: Setup instructions
- **Architecture**: AI-explained codebase structure
- **Code Context Graph**: Relationship diagrams
- **Module Documentation**: AI-enhanced module descriptions
- **API Reference**: Complete function and class listings

## 🔧 API Endpoints

### `/walker/api_generate_docs`

Main endpoint for generating documentation.

**Request:**
```json
{
  "repo_url": "https://github.com/username/repository",
  "output_dir": "./outputs"
}
```

**Response:**
```json
{
  "status": "processing",
  "message": "Documentation generation started. Check outputs directory for results."
}
```

### `/walker/supervisor`

Direct supervisor walker execution.

**Request:**
```json
{
  "repo_url": "https://github.com/username/repository"
}
```

### `/walker/repo_mapper`

Repository mapping only.

**Request:**
```json
{
  "repo_url": "https://github.com/username/repository",
  "output_dir": "./temp_repos"
}
```

### `/walker/code_analyzer`

Code analysis only (requires repo_node in graph).

**Request:**
```json
{
  "repo_path": "./path/to/repo"
}
```

### `/walker/docgenie`

Documentation generation only (reads from repo_node).

**Request:** (No parameters - reads from graph)

## 🧪 Testing

### Test Python Modules

```bash
python -c "from python_modules.repo_cloner import clone_repository; print('OK')"
```

### Test API

Use the provided test script:

```powershell
.\test_api.ps1
```

### Test Documentation Generation

```bash
python generate_docs.py
```

## 🐛 Troubleshooting

### Server Won't Start

1. **Check Jac installation:**
   ```bash
   jac --version
   ```

2. **Check Python modules:**
   ```bash
   python -c "from python_modules.repo_cloner import clone_repository; print('OK')"
   ```

3. **Check port availability:**
   ```bash
   # Windows
   netstat -an | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

### API Returns 500 Errors

- Check server logs for detailed error messages
- Verify `.env` file exists and contains `GEMINI_API_KEY`
- Ensure all Python dependencies are installed

### AI Not Working

- Verify `GEMINI_API_KEY` is set in `.env`
- Check API key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Ensure `google-generativeai` package is installed: `pip install google-generativeai`

### Repository Cloning Fails

- Verify the repository URL is correct and public
- Check Git is installed: `git --version`
- Ensure you have internet connectivity

## 📚 Documentation

- **Jac Language**: https://www.jac-lang.org/
- **Jac Reference**: https://www.jac-lang.org/learn/jac_ref/
- **byLLM Example**: https://github.com/jaseci-labs/Agentic-AI/task_manager/byllm
- **Gemini API**: https://ai.google.dev/

## 🎓 Learning Resources

Before using this codebase, it's recommended to:

1. **Study Jac Language:**
   - [Beginner's Guide](https://www.jac-lang.org/learn/getting_started/)
   - [Jac Book](https://www.jac-lang.org/jac_book/)

2. **Review byLLM Example:**
   ```bash
   git clone https://github.com/jaseci-labs/Agentic-AI.git
   cd Agentic-AI/task_manager/byllm
   ```

## 🤝 Contributing

This is an assignment project. Contributions and improvements are welcome!

## 📄 License

[Specify your license here]

## 🙏 Acknowledgments

- Built with [Jac (JacLang)](https://www.jac-lang.org/)
- AI powered by [Google Gemini](https://ai.google.dev/)
- Code parsing with [Tree-sitter](https://tree-sitter.github.io/tree-sitter/)
- Inspired by [byLLM Task Manager](https://github.com/jaseci-labs/Agentic-AI)

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the Jac documentation
3. Check server logs for detailed error messages

---

**Made with ❤️ using Jac and AI**
