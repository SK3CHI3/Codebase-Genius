# Complete Setup Guide - Codebase Genius

This guide will help you set up and run Codebase Genius from scratch.

## 📋 Step-by-Step Setup

### Step 1: Prerequisites Check

Verify you have the required software:

```bash
# Check Python (3.8+)
python --version

# Check Git
git --version

# Check if Jac is installed (if not, we'll install it)
jac --version
```

### Step 2: Clone Repository

```bash
git clone https://github.com/SK3CHI3/Codebase-Genius.git
cd Codebase-Genius
```

### Step 3: Create Virtual Environment

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

You should see `(venv)` in your terminal prompt.

### Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `jaclang` - Jac runtime
- `google-generativeai` - Gemini AI SDK
- `tree-sitter` - Code parsing
- `gitpython` - Repository cloning
- `python-dotenv` - Environment variables
- And other dependencies

### Step 5: Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

### Step 6: Create .env File

Create a file named `.env` in the root directory:

**Windows (PowerShell):**
```powershell
"GEMINI_API_KEY=your_api_key_here" | Out-File -FilePath .env -Encoding ASCII
```

**Linux/Mac:**
```bash
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

**Or manually:**
Create `.env` file with:
```
GEMINI_API_KEY=AIzaSyAxHPVZfU8SaHEtN8fpBi7h8uoRNc8ukrg
```

### Step 7: Verify Setup

Test that everything works:

```bash
# Test Python modules
python -c "from python_modules.repo_cloner import clone_repository; print('✓ Python modules OK')"

# Test AI integration
python -c "from python_modules.doc_generator import DocGenerator; dg = DocGenerator(); print('✓ AI Available:', dg.use_ai)"

# Test Jac compilation
jac build main.jac
```

### Step 8: Start the Server

```bash
jac serve main.jac
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## 🧪 Test the Application

### Test 1: Generate Documentation via API

**PowerShell:**
```powershell
$body = @{
    repo_url = "https://github.com/octocat/Hello-World"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/walker/api_generate_docs" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

**cURL:**
```bash
curl -X POST http://localhost:8000/walker/api_generate_docs \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/octocat/Hello-World"}'
```

### Test 2: Check Generated Documentation

After running the API, check:

```bash
# Windows
dir outputs

# Linux/Mac
ls outputs
```

The documentation will be in `outputs/<repo_name>/docs.md`

### Test 3: Direct Python Script

```bash
python generate_docs.py
```

This will generate documentation for the repository specified in the script.

## 🔍 Verify Everything Works

Run this comprehensive test:

```bash
# 1. Check Python modules
python -c "from python_modules.repo_cloner import clone_repository; from python_modules.doc_generator import DocGenerator; print('All modules OK')"

# 2. Check Jac compilation
jac build main.jac

# 3. Check server starts (in another terminal)
jac serve main.jac
```

## 🎯 First Documentation Generation

Try generating docs for a small repository:

```bash
python generate_docs.py
```

Or use the API:

```powershell
$body = @{repo_url='https://github.com/octocat/Hello-World'} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:8000/walker/api_generate_docs' -Method POST -Body $body -ContentType 'application/json'
```

## 📝 Common Issues & Solutions

### Issue: "jac: command not found"

**Solution:**
```bash
pip install jaclang
# Or reinstall
pip install --upgrade jaclang
```

### Issue: "GEMINI_API_KEY not found"

**Solution:**
1. Verify `.env` file exists in project root
2. Check file contains: `GEMINI_API_KEY=your_key`
3. Ensure no extra spaces or quotes
4. Restart the server after creating `.env`

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Windows - Find process
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill
```

### Issue: "Module not found" errors

**Solution:**
```bash
# Ensure venv is activated
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: AI not working

**Solution:**
1. Verify API key is correct
2. Check API key has not expired
3. Test API key directly:
   ```python
   import google.generativeai as genai
   genai.configure(api_key="your_key")
   model = genai.GenerativeModel('gemini-1.5-flash')
   response = model.generate_content("Hello")
   print(response.text)
   ```

## ✅ Setup Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Git installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with `GEMINI_API_KEY`
- [ ] Jac compiles without errors (`jac build main.jac`)
- [ ] Server starts successfully (`jac serve main.jac`)
- [ ] Can generate documentation via API or Python script

## 🚀 Next Steps

Once setup is complete:

1. **Explore the API**: Use the test scripts or Postman to test endpoints
2. **Generate Documentation**: Try different repositories
3. **Review Output**: Check `outputs/` directory for generated docs
4. **Customize**: Modify prompts in `doc_generator.py` for different documentation styles

## 📚 Additional Resources

- [Jac Language Documentation](https://www.jac-lang.org/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [byLLM Example](https://github.com/jaseci-labs/Agentic-AI/task_manager/byllm)

---

**Need Help?** Check the main README.md or review server logs for detailed error messages.
