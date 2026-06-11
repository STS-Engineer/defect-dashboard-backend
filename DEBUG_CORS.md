# CORS Debugging Guide

## Step 1: Verify the Route Exists
```python
# In FastAPI shell or inspect with curl:
curl -X PATCH http://127.0.0.1:8002/defects/1084 \
  -H "Content-Type: application/json" \
  -d '{"securisation": "test"}'
```

Expected: Either 200/204 or 422 (validation error), NOT 404/405.

---

## Step 2: Check CORS Middleware Registration Order
In main.py, verify:
- CORSMiddleware is added BEFORE app.include_router()
- Currently at line 120-133 ✓ (correct position)

---

## Step 3: Test OPTIONS Request (Preflight)
```bash
# This is what the browser sends before PATCH
curl -X OPTIONS http://127.0.0.1:8002/defects/1084 \
  -H "Origin: http://localhost:5174" \
  -H "Access-Control-Request-Method: PATCH" \
  -H "Access-Control-Request-Headers: content-type" \
  -v
```

Expected response headers:
- HTTP/1.1 200 OK
- Access-Control-Allow-Origin: http://localhost:5174
- Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
- Access-Control-Allow-Headers: *

---

## Step 4: Enable Debug Logging
Add this to main.py before creating FastAPI app:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Then run backend and watch for errors.

---

## Step 5: Check Browser Network Tab
1. Open DevTools (F12) → Network tab
2. Reproduce the update action
3. Look for:
   - OPTIONS request → Check Status Code
   - PATCH request → Check Status Code & Response

---

## Step 6: Test with Swagger UI
1. Go to http://127.0.0.1:8002/docs
2. Find the PATCH /defects/{defect_id} endpoint
3. Click "Try it out"
4. Enter defect_id: 1084
5. Enter body with valid data
6. Click "Execute"
7. Check response

If Swagger works but frontend fails → Frontend configuration issue
If Swagger fails → Backend issue

---

## Step 7: Direct Backend Testing
```bash
# Test PATCH endpoint directly
curl -X PATCH http://127.0.0.1:8002/defects/1084 \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:5174" \
  -d '{
    "securisation": "OK",
    "poste_occurrence": "POSTE1",
    "poste_detection": "POSTE2",
    "root_cause_occurrence": "RC1",
    "root_cause_non_detection": "RC2",
    "plan_action_occurrence": "PA1",
    "plan_action_non_detection": "PA2"
  }' \
  -v
```

---

## Error Diagnosis

| Error | Cause | Fix |
|-------|-------|-----|
| 404 Not Found | Route doesn't exist | Verify @app.patch() decorator exists |
| 405 Method Not Allowed | Wrong HTTP method | Frontend using PUT instead of PATCH |
| 422 Unprocessable Entity | Invalid request body | Check DefectUpdate schema |
| 500 Internal Server Error | Backend exception | Check server logs |
| CORS error on OPTIONS | CORSMiddleware issue | Check middleware order & config |
| CORS error on PATCH | OPTIONS failed first | Fix OPTIONS response first |
