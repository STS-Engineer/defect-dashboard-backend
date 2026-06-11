#!/usr/bin/env python3
"""
CORS Debugging Script - Run this to identify the exact issue
Usage: python debug_cors.py
"""

import subprocess
import sys
import json

def run_curl(description, method, url, headers=None, data=None):
    """Run a curl command and display the result."""
    print(f"\n{'='*70}")
    print(f"📡 {description}")
    print(f"{'='*70}")
    
    cmd = ["curl", "-i", "-X", method, url]
    
    if headers:
        for header, value in headers.items():
            cmd.extend(["-H", f"{header}: {value}"])
    
    if data:
        cmd.extend(["-H", "Content-Type: application/json"])
        cmd.extend(["-d", json.dumps(data)])
    
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except subprocess.TimeoutExpired:
        print("❌ Request timeout - backend may not be running")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    backend_url = "http://127.0.0.1:8002"
    frontend_origin = "http://localhost:5174"
    defect_id = 1084
    
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                     CORS DEBUGGING SCRIPT                         ║
║                                                                   ║
║ This script tests all aspects of your CORS configuration.        ║
║ Watch the FastAPI console for log messages!                      ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    print(f"🎯 Target: {backend_url}")
    print(f"🌐 Frontend: {frontend_origin}")
    print(f"📝 Test Defect ID: {defect_id}")
    
    # Test 1: Root endpoint (no CORS needed)
    run_curl(
        "1️⃣ TEST: GET / (baseline - no CORS needed)",
        "GET",
        f"{backend_url}/"
    )
    
    # Test 2: OPTIONS preflight request
    run_curl(
        "2️⃣ TEST: OPTIONS preflight for PATCH request",
        "OPTIONS",
        f"{backend_url}/defects/{defect_id}",
        headers={
            "Origin": frontend_origin,
            "Access-Control-Request-Method": "PATCH",
            "Access-Control-Request-Headers": "content-type",
        }
    )
    
    # Test 3: PATCH without CORS headers (backend only)
    run_curl(
        "3️⃣ TEST: PATCH /defects/{id} (backend test, no CORS headers)",
        "PATCH",
        f"{backend_url}/defects/{defect_id}",
        data={
            "securisation": "OK",
            "poste_occurrence": "POSTE1",
            "poste_detection": "POSTE2",
            "root_cause_occurrence": "RC1",
            "root_cause_non_detection": "RC2",
            "plan_action_occurrence": "PA1",
            "plan_action_non_detection": "PA2"
        }
    )
    
    # Test 4: PATCH with CORS headers (simulating browser)
    run_curl(
        "4️⃣ TEST: PATCH /defects/{id} WITH CORS headers (browser simulation)",
        "PATCH",
        f"{backend_url}/defects/{defect_id}",
        headers={
            "Origin": frontend_origin,
            "Content-Type": "application/json",
        },
        data={
            "securisation": "OK",
            "poste_occurrence": "POSTE1",
            "poste_detection": "POSTE2",
            "root_cause_occurrence": "RC1",
            "root_cause_non_detection": "RC2",
            "plan_action_occurrence": "PA1",
            "plan_action_non_detection": "PA2"
        }
    )
    
    # Test 5: Swagger endpoint
    run_curl(
        "5️⃣ TEST: GET /docs (Swagger UI)",
        "GET",
        f"{backend_url}/docs"
    )
    
    print(f"\n{'='*70}")
    print("📊 INTERPRETATION GUIDE")
    print(f"{'='*70}")
    print("""
Test 1 ✓ but Test 2 ✗:
  → CORSMiddleware not working, check middleware registration order

Test 2 ✓ but Test 4 ✗:
  → OPTIONS works but actual request fails = backend exception in PATCH handler

Test 3 ✗ (without CORS headers):
  → PATCH endpoint broken or defect_id doesn't exist (404) or schema validation failed (422)

Test 4 ✗ with 500:
  → Internal server error in PATCH handler (check FastAPI logs)

Test 4 ✗ with 422:
  → Request body validation failed (check DefectUpdate schema in schemas.py)

Test 4 ✗ with 404:
  → Defect with ID {defect_id} doesn't exist in database

Test 4 ✗ with 403/401:
  → Authentication/authorization issue

All tests ✗:
  → Backend not running on port 8002
    """)

if __name__ == "__main__":
    main()
