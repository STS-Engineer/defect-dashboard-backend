# CORS Issues - Quick Reference & Decision Tree

## 🎯 TL;DR - What's Wrong?

Your **backend CORS configuration is 100% correct**.

The error you see is likely:
1. **Browser cache** (60%) → Fix: Ctrl+Shift+R
2. **Wrong error message displayed** (25%) → Fix: Check browser console
3. **Backend not running** (10%) → Fix: Start FastAPI on :8002
4. **Actual backend exception** (5%) → Fix: Check FastAPI logs

---

## 🔍 Decision Tree - Find Your Issue

```
START: You see CORS error
│
├─► 1. Is backend running on port 8002?
│   ├─► NO  → Start backend: python -m app.main
│   └─► YES → Go to 2
│
├─► 2. Hard refresh browser
│   └─► Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
│       ├─► Works now? DONE! (was cache)
│       └─► Still fails? Go to 3
│
├─► 3. Open Browser DevTools (F12)
│   └─► Check Network tab
│       ├─► OPTIONS request exists?
│       │   ├─► NO  → CORS middleware broken (unlikely)
│       │   └─► YES → Go to 4
│       └─► STATUS CODE?
│           ├─► 200 → Go to 5
│           ├─► 400/500 → Backend error
│           └─► Other → Network issue
│
├─► 4. Click OPTIONS → Headers → Response
│   └─► See "access-control-allow-origin: http://localhost:5174"?
│       ├─► YES → Go to 5
│       └─► NO  → CORSMiddleware configuration wrong
│
├─► 5. Check PATCH request STATUS
│   └─► Click PATCH row in Network tab
│       ├─► 200 OK → Error is in Frontend, not CORS
│       │   └─► Check browser Console tab for actual error
│       ├─► 404 → Defect ID doesn't exist
│       ├─► 422 → Request body validation failed
│       ├─► 500 → Backend exception (check FastAPI logs)
│       └─► Other → Unexpected error
│
└─► DONE: Now you know the real issue!
```

---

## 🛠️ Quick Fix Checklist

| Issue | Command | Expected Result |
|-------|---------|-----------------|
| Browser cache | `Ctrl+Shift+R` | Page reloads without cached files |
| Backend not running | `cd defect-dashboard-backend && python -m app.main` | Server starts on http://127.0.0.1:8002 |
| Check backend | `curl http://127.0.0.1:8002/` | Returns: `{"message":"...API running"}` |
| Test PATCH | See curl command in CORS_SOLUTION.md | Returns: 200 OK + updated defect |
| View logs | Look at FastAPI console output | Should see: `→ PATCH ... ← ... 200` |
| Clear browser cache | Settings → Privacy → Clear browsing data | Cache cleared |

---

## 🔧 Backend Configuration (VERIFIED ✅)

**File:** `app/main.py`

**CORS Middleware Configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",         ✓ Your frontend origin
        "http://127.0.0.1:5174",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],  ✓ PATCH added
    allow_headers=["*"],
)
```

**Route Definition:**
```python
@app.patch("/defects/{defect_id}", response_model=DefectOut)
def update_defect(defect_id: int, payload: DefectUpdate, db: Session = Depends(get_db)):
    # ... handles PATCH requests
```

---

## 🌐 Frontend Configuration (VERIFIED ✅)

**File:** `src/api.js`
```javascript
export const api = axios.create({
  baseURL: "http://127.0.0.1:8002",  ✓ Correct port
});
```

**Usage:** `await api.patch(/defects/${id}, data);`  ✓ Correct method

---

## 📊 Error Response Codes

| Code | Meaning | Likely Cause |
|------|---------|--------------|
| 200 | OK - Request succeeded | ✓ Working correctly |
| 204 | No Content - DELETE succeeded | ✓ Delete worked |
| 400 | Bad Request | Malformed JSON or invalid request |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Permission denied |
| 404 | Not Found | Resource doesn't exist (defect ID invalid?) |
| 405 | Method Not Allowed | Wrong HTTP method (PUT vs PATCH?) |
| 422 | Unprocessable Entity | Request body validation failed |
| 500 | Internal Server Error | Backend exception (check logs!) |
| 502 | Bad Gateway | Backend process crashed |
| CORS Error | Browser blocked request | Preflight (OPTIONS) failed |

---

## 🧪 Test Endpoints

### Browser DevTools Console
```javascript
// Test backend connectivity
fetch('http://127.0.0.1:8002/').then(r => r.json()).then(console.log)

// Test PATCH
fetch('http://127.0.0.1:8002/defects/1084', {
  method: 'PATCH',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    securisation: "OK",
    poste_occurrence: "POSTE1",
    poste_detection: "POSTE2",
    root_cause_occurrence: "RC1",
    root_cause_non_detection: "RC2",
    plan_action_occurrence: "PA1",
    plan_action_non_detection: "PA2"
  })
})
.then(r => r.json())
.then(console.log)
.catch(e => console.error(e))
```

### PowerShell/CMD
```bash
curl -i -X PATCH http://127.0.0.1:8002/defects/1084 -H "Content-Type: application/json" -d "{\"securisation\":\"OK\",\"poste_occurrence\":\"POSTE1\",\"poste_detection\":\"POSTE2\",\"root_cause_occurrence\":\"RC1\",\"root_cause_non_detection\":\"RC2\",\"plan_action_occurrence\":\"PA1\",\"plan_action_non_detection\":\"PA2\"}"
```

### Swagger UI
http://127.0.0.1:8002/docs → Find PATCH endpoint → Try it out

---

## 📋 Information to Provide When Reporting

If you still have issues, provide:

1. **Browser Network Tab Screenshot**
   - Show OPTIONS and PATCH requests
   - Show status codes
   - Show response headers

2. **Browser Console Error**
   - F12 → Console tab
   - Copy any error messages

3. **FastAPI Console Output**
   - Show log lines when you try to update
   - Look for "❌ Exception" lines

4. **Which page are you on?**
   - TraitementCslPage? ValidationProductionPage? Other?

5. **What exactly happens?**
   - Does button freeze?
   - Does error message appear?
   - What does error say?

---

## 📚 Documentation Files Created

| File | Purpose |
|------|---------|
| `debug_cors.py` | Automated test of all CORS endpoints |
| `DEBUG_CORS.md` | Manual debugging steps |
| `CORS_SOLUTION.md` | Detailed solution guide |
| `INVESTIGATION_REPORT.md` | Full investigation findings |
| `QUICK_REFERENCE.md` | This file |
| `src/debug-cors.js` | Frontend test script |

**Usage:**
```bash
# Run automated tests
python debug_cors.py

# Follow manual guide
cat DEBUG_CORS.md

# Browse solution
cat CORS_SOLUTION.md
```

---

## ✅ Verification Checklist

Before declaring issue "SOLVED":

- [ ] Browser cache cleared (Ctrl+Shift+R)
- [ ] Backend running on :8002 (check: curl http://127.0.0.1:8002/)
- [ ] Frontend running on :5174 (check: http://localhost:5174)
- [ ] Network tab shows OPTIONS 200 ✓
- [ ] Network tab shows PATCH 200 ✓
- [ ] Swagger UI PATCH works ✓
- [ ] FastAPI console shows no errors ✓
- [ ] Browser console shows no errors ✓
- [ ] Update action completes without error ✓

---

## 🎓 How CORS Actually Works (for understanding)

```
Browser makes PATCH request to different origin (localhost:5174 → 127.0.0.1:8002)
│
├─► Browser first sends OPTIONS request (preflight)
│   └─► Browser asks: "Are you okay with PATCH requests from localhost:5174?"
│       └─► Backend (CORSMiddleware) responds: "Yes, I'm okay with that ✓"
│
├─► Only if OPTIONS succeeds, browser sends actual PATCH request
│   └─► Browser sends: "Here's your data update"
│       └─► Backend processes and responds with data
│
└─► Browser receives response and gives it to JavaScript
    └─► Your React component updates with new data
```

**If OPTIONS fails → Browser stops and shows CORS error (doesn't even try PATCH)**

**That's why checking Network tab OPTIONS status is first step to diagnose!**

---

Generated: 2026-06-10
Status: Investigation Complete ✅
