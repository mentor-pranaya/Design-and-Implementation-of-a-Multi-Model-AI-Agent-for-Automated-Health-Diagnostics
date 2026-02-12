# 🚨 Site Can't Be Reached - Quick Fix

If you're seeing **"This site can't be reached"** when trying to access http://localhost:10000, follow these steps:

---

## ⚡ Quick Fix (30 seconds)

### Step 1: Run Diagnostic
```bash
diagnose.bat
```
This will tell you exactly what's wrong.

### Step 2: Fix Issues Found
Based on diagnostic results, follow the recommended actions.

### Step 3: Start Server
```bash
setup_and_start.bat
```

### Step 4: Test
Open browser: http://localhost:10000

---

## 🔧 Common Issues & Solutions

### ❌ Issue 1: "Python is not recognized"
**Problem:** Python is not installed or not in PATH

**Solution:**
1. Download Python: https://www.python.org/downloads/
2. **IMPORTANT:** Check these boxes during installation:
   - ✅ "Add Python to PATH"
   - ✅ "Install pip"
3. Restart your computer
4. Try again

**Verify:** Open new terminal and run:
```bash
python --version
pip --version
```

---

### ❌ Issue 2: "Module not found" errors
**Problem:** Dependencies not installed

**Solution:**
```bash
setup_and_start.bat
```
This will automatically install all required packages.

---

### ❌ Issue 3: "Address already in use" 
**Problem:** Port 10000 is already occupied

**Solution:**
Option A: Kill existing process
```bash
netstat -ano | findstr :10000
taskkill /PID <PID> /F
```

Option B: Use different port (edit setup_and_start.bat)
```batch
set PORT=10001
```

---

### ❌ Issue 4: "Connection refused"
**Problem:** Server isn't actually running

**Solution:**
1. Check if server is running:
   ```bash
   curl http://localhost:10000/health
   ```
   
2. If not, start it:
   ```bash
   setup_and_start.bat
   ```
   
3. Wait for message: "Uvicorn running on http://0.0.0.0:10000"

---

### ❌ Issue 5: "Connection timeout"
**Problem:** Server is running but not responding

**Solution:**
1. Check Windows Firewall:
   - Allow Python through firewall
   - Or temporarily disable firewall for testing
   
2. Use localhost instead of 0.0.0.0:
   ```
   http://localhost:10000  ✅
   http://0.0.0.0:10000    ❌ (won't work locally)
   ```

3. Restart server

---

## 📋 Full Setup From Scratch

### Step 1: Install Python
- Download: https://www.python.org/downloads/
- **MUST check:** "Add Python to PATH"
- Install for all users
- Restart computer

### Step 2: Verify Installation
```bash
python --version
pip --version
```

Should show version numbers, not "not found" errors.

### Step 3: Navigate to Project
```bash
cd "c:\Users\gurus\OneDrive\文档\Desktop\blood_report_ai"
```

### Step 4: Create Virtual Environment
```bash
python -m venv venv
```

### Step 5: Activate Virtual Environment
```bash
venv\Scripts\activate
```

### Step 6: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 7: Start Server
```bash
python run_instant.py
```

Or use:
```bash
setup_and_start.bat
```

### Step 8: Test
Open browser: http://localhost:10000

---

## ✅ Server Running Successfully? 

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:10000 (Press CTRL+C to quit)
```

Then open browser to: http://localhost:10000

---

## 🧪 Quick Tests

### Test 1: Health Check
```bash
curl http://localhost:10000/health
```

### Test 2: API Status
```bash
curl http://localhost:10000/api/status
```

### Test 3: Web Interface
```
http://localhost:10000
```

---

## 📋 Checklist

- [ ] Python installed and in PATH
- [ ] Virtual environment created (`venv` folder exists)
- [ ] Dependencies installed (no errors in setup)
- [ ] Server started (you see "Uvicorn running")
- [ ] Can reach http://localhost:10000
- [ ] Health check returns status "healthy"

---

## 🆘 Still Not Working?

### Collect Diagnostic Info
```bash
diagnose.bat
```

### Check Port
```bash
netstat -ano | findstr :10000
```

### View Recent Errors
```bash
type inbloodo.log
```

### Restart Everything
```bash
REM Close terminal
REM Restart computer
REM Run setup_and_start.bat again
```

---

## 🎯 Most Common Solution

**99% of the time, the issue is:**

❌ Python not in PATH

**Fix:**
1. Install Python again: https://www.python.org/downloads/
2. **CHECK "Add Python to PATH"** ← This is crucial!
3. Restart computer
4. Run `setup_and_start.bat`

---

## 📞 Key Commands

| Command | Purpose |
|---------|---------|
| `diagnose.bat` | Find what's wrong |
| `setup_and_start.bat` | Full setup + start |
| `python --version` | Check Python |
| `curl http://localhost:10000` | Test server |
| `tasklist \| findstr python` | Find Python process |

---

## 🎉 Once It Works

You'll have:
- ✅ Running server at http://localhost:10000
- ✅ Instant blood report analysis
- ✅ 10-100x performance boost
- ✅ Real-time metrics dashboard

Enjoy! 🚀

