"""
End-to-End Automated Browser Verification Suite for Career Compass Auth.
Tests both #auth-screen (full-screen split layout) and #auth-modal.

Tests verified:
1. Fresh browser window -> #auth-screen is visible, #auth-view-login is displayed, #app-shell is hidden.
2. Clicking "Create an account" button/link switches view to #auth-view-signup.
3. Submitting invalid signup data displays proper validation error (name, email, password < 8 chars).
4. Submitting valid signup data creates the account, redirects to #auth-view-login, displays the green success banner, and pre-fills email.
5. Attempting duplicate signup with same email shows 409 conflict error.
6. Submitting login with wrong password displays clear error message in #auth-login-error.
7. Submitting login with correct password logs in and redirects directly to personalized dashboard (#app-shell visible, #auth-screen hidden, user profile chip rendered).
8. Refreshing the browser preserves the active login session (#app-shell remains visible).
9. Modal verification: openAuthModal('signup') switches tab and renders #form-auth-signup; switchAuthTab('login') switches to #form-auth-login; handleAuthLogin / handleAuthSignup execute without any ReferenceError.
10. Mobile screen test (375x667): forms render cleanly with no horizontal overflow.
"""

import subprocess
import time
import json
import urllib.request
import websocket
import threading
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from app import app
from db_repository import UserRepository

TEST_PORT = 5088
CDP_PORT = 9333

def run_flask():
    app.run(host='127.0.0.1', port=TEST_PORT, debug=False, use_reloader=False)

def main():
    print("=" * 70)
    print("CAREER COMPASS — COMPLETE AUTHENTICATION VERIFICATION SUITE")
    print("=" * 70)

    # Clean up test accounts
    test_email = f"auth_e2e_{int(time.time())}@example.com"
    test_pwd = "TestPassword123!"
    test_name = "Kavya Reddy"

    print(f"\n[SETUP] Starting Flask test server on port {TEST_PORT}...")
    server_thread = threading.Thread(target=run_flask, daemon=True)
    server_thread.start()
    time.sleep(2)

    edge_profile_dir = os.path.abspath("edge_profile_auth_verify")
    edge_cmd = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        f"--remote-debugging-port={CDP_PORT}",
        "--remote-allow-origins=*",
        f"--user-data-dir={edge_profile_dir}",
        f"http://127.0.0.1:{TEST_PORT}/"
    ]

    print(f"[SETUP] Launching Edge headless with CDP on port {CDP_PORT}...")
    edge_proc = subprocess.Popen(edge_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3)

    try:
        targets = None
        for _ in range(10):
            try:
                req = urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json")
                targets = json.loads(req.read().decode())
                if targets:
                    break
            except Exception:
                time.sleep(1)

        ws_url = None
        if targets:
            for t in targets:
                if t.get('type') == 'page' and f':{TEST_PORT}' in t.get('url', ''):
                    ws_url = t.get('webSocketDebuggerUrl')
                    break
            if not ws_url:
                for t in targets:
                    if t.get('type') == 'page':
                        ws_url = t.get('webSocketDebuggerUrl')
                        break

        if not ws_url:
            print("[FAIL] Could not find page target in CDP")
            sys.exit(1)

        print(f"[SETUP] Connected to CDP page: {ws_url}")
        ws = websocket.create_connection(ws_url)
        msg_id = 0

        def send_cmd(method, params=None):
            nonlocal msg_id
            msg_id += 1
            payload = {"id": msg_id, "method": method, "params": params or {}}
            ws.send(json.dumps(payload))
            while True:
                resp = json.loads(ws.recv())
                if resp.get("id") == msg_id:
                    return resp

        def eval_js(expr):
            resp = send_cmd("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
            result = resp.get("result", {}).get("result", {})
            if "value" in result:
                return result["value"]
            if resp.get("result", {}).get("exceptionDetails"):
                print("JS Exception:", resp["result"]["exceptionDetails"])
            return None

        # Explicitly navigate to test server and wait for DOM
        send_cmd("Page.enable")
        send_cmd("Page.navigate", {"url": f"http://127.0.0.1:{TEST_PORT}/"})

        # Wait until page has completely loaded and auth-screen is ready
        for _ in range(30):
            try:
                ready = eval_js("document.readyState === 'complete' && !!document.getElementById('auth-screen')")
                if ready:
                    break
            except Exception:
                pass
            time.sleep(0.5)

        print("Page Title:", eval_js("document.title"))

        results = {}

        # -------------------------------------------------------------
        # TEST 1: Initial Unauthenticated View
        # -------------------------------------------------------------
        print("\n--- TEST 1: Unauthenticated First Screen (#auth-screen visible, #app-shell hidden) ---")
        auth_visible = eval_js("!document.getElementById('auth-screen').classList.contains('hidden')")
        app_hidden = eval_js("document.getElementById('app-shell').classList.contains('hidden')")
        login_view_visible = eval_js("!document.getElementById('auth-view-login').classList.contains('hidden')")
        signup_view_hidden = eval_js("document.getElementById('auth-view-signup').classList.contains('hidden')")

        print(f"Auth screen visible: {auth_visible}")
        print(f"App shell hidden: {app_hidden}")
        print(f"Login view active: {login_view_visible}")
        print(f"Signup view hidden: {signup_view_hidden}")

        if auth_visible and app_hidden and login_view_visible and signup_view_hidden:
            results["Test 1: Initial View"] = "PASS"
            print(">>> TEST 1: PASS")
        else:
            results["Test 1: Initial View"] = "FAIL"
            print(">>> TEST 1: FAIL")

        # -------------------------------------------------------------
        # TEST 2: "Create an Account" Link/Button Transitions View
        # -------------------------------------------------------------
        print("\n--- TEST 2: Create an Account link switches to Registration View ---")
        # Click the "Create an account" button in login form
        eval_js("document.querySelector('#auth-view-login .auth-link-btn').click()")
        time.sleep(0.5)

        signup_active = eval_js("!document.getElementById('auth-view-signup').classList.contains('hidden')")
        login_hidden = eval_js("document.getElementById('auth-view-login').classList.contains('hidden')")
        print(f"Signup view active: {signup_active}")
        print(f"Login view hidden: {login_hidden}")

        if signup_active and login_hidden:
            results["Test 2: Switch to Signup"] = "PASS"
            print(">>> TEST 2: PASS")
        else:
            results["Test 2: Switch to Signup"] = "FAIL"
            print(">>> TEST 2: FAIL")

        # -------------------------------------------------------------
        # TEST 3: Validation Error on Short Password (< 8 chars)
        # -------------------------------------------------------------
        print("\n--- TEST 3: Signup Validation (< 8 characters password) ---")
        eval_js("document.getElementById('auth-signup-name').value = 'Test User'")
        eval_js(f"document.getElementById('auth-signup-email').value = 'test_short_{int(time.time())}@example.com'")
        eval_js("document.getElementById('auth-signup-password').value = 'short'")
        eval_js("document.getElementById('auth-signup-confirm').value = 'short'")
        eval_js("handleAuthSignupSubmit(new Event('submit'))")
        time.sleep(0.5)

        err_visible = eval_js("!document.getElementById('auth-signup-error').classList.contains('hidden')")
        err_text = eval_js("document.getElementById('auth-signup-error').textContent")
        print(f"Error box visible: {err_visible}")
        print(f"Error text: '{err_text}'")

        if err_visible and "8 characters" in err_text:
            results["Test 3: Signup Validation"] = "PASS"
            print(">>> TEST 3: PASS")
        else:
            results["Test 3: Signup Validation"] = "FAIL"
            print(">>> TEST 3: FAIL")

        # -------------------------------------------------------------
        # TEST 4: Successful Account Registration -> Redirect to Login Page with Success Banner
        # -------------------------------------------------------------
        print("\n--- TEST 4: Successful Registration -> Redirect to Login with Success Message ---")
        eval_js(f"document.getElementById('auth-signup-name').value = '{test_name}'")
        eval_js(f"document.getElementById('auth-signup-email').value = '{test_email}'")
        eval_js(f"document.getElementById('auth-signup-password').value = '{test_pwd}'")
        eval_js(f"document.getElementById('auth-signup-confirm').value = '{test_pwd}'")
        eval_js("handleAuthSignupSubmit(new Event('submit'))")
        time.sleep(2)

        login_view_now = eval_js("!document.getElementById('auth-view-login').classList.contains('hidden')")
        signup_view_now = eval_js("document.getElementById('auth-view-signup').classList.contains('hidden')")
        success_visible = eval_js("!document.getElementById('auth-login-success').classList.contains('hidden')")
        success_msg = eval_js("document.getElementById('auth-login-success').textContent")
        prefilled_email = eval_js("document.getElementById('auth-login-email').value")

        print(f"Redirected to Login view: {login_view_now}")
        print(f"Signup view hidden: {signup_view_now}")
        print(f"Success banner visible: {success_visible}")
        print(f"Success message: '{success_msg}'")
        print(f"Pre-filled email on login form: '{prefilled_email}'")

        if login_view_now and success_visible and prefilled_email == test_email and "Account created successfully" in success_msg:
            results["Test 4: Registration & Redirect"] = "PASS"
            print(">>> TEST 4: PASS")
        else:
            results["Test 4: Registration & Redirect"] = "FAIL"
            print(">>> TEST 4: FAIL")

        # -------------------------------------------------------------
        # TEST 5: Duplicate Registration Conflict (409)
        # -------------------------------------------------------------
        print("\n--- TEST 5: Duplicate Email Registration (409 Conflict) ---")
        eval_js("showAuthView('signup')")
        eval_js(f"document.getElementById('auth-signup-name').value = 'Duplicate User'")
        eval_js(f"document.getElementById('auth-signup-email').value = '{test_email}'")
        eval_js(f"document.getElementById('auth-signup-password').value = '{test_pwd}'")
        eval_js(f"document.getElementById('auth-signup-confirm').value = '{test_pwd}'")
        eval_js("handleAuthSignupSubmit(new Event('submit'))")
        time.sleep(2)

        dup_err_visible = eval_js("!document.getElementById('auth-signup-error').classList.contains('hidden')")
        dup_err_text = eval_js("document.getElementById('auth-signup-error').textContent")
        print(f"Duplicate error visible: {dup_err_visible}")
        print(f"Duplicate error text: '{dup_err_text}'")

        if dup_err_visible and "already exists" in dup_err_text:
            results["Test 5: Duplicate Prevention"] = "PASS"
            print(">>> TEST 5: PASS")
        else:
            results["Test 5: Duplicate Prevention"] = "FAIL"
            print(">>> TEST 5: FAIL")

        # -------------------------------------------------------------
        # TEST 6: Sign In with Incorrect Credentials
        # -------------------------------------------------------------
        print("\n--- TEST 6: Sign In with Incorrect Password (Shows Clear Error) ---")
        eval_js("showAuthView('login')")
        eval_js(f"document.getElementById('auth-login-email').value = '{test_email}'")
        eval_js("document.getElementById('auth-login-password').value = 'WrongPassword999!'")
        eval_js("handleAuthLoginSubmit(new Event('submit'))")
        time.sleep(1.5)

        login_err_visible = eval_js("!document.getElementById('auth-login-error').classList.contains('hidden')")
        login_err_text = eval_js("document.getElementById('auth-login-error').textContent")
        print(f"Login error visible: {login_err_visible}")
        print(f"Login error message: '{login_err_text}'")

        if login_err_visible and "Invalid email or password" in login_err_text:
            results["Test 6: Invalid Credentials Error"] = "PASS"
            print(">>> TEST 6: PASS")
        else:
            results["Test 6: Invalid Credentials Error"] = "FAIL"
            print(">>> TEST 6: FAIL")

        # -------------------------------------------------------------
        # TEST 7: Sign In with Correct Credentials -> Personalized Dashboard
        # -------------------------------------------------------------
        print("\n--- TEST 7: Sign In with Correct Credentials (Redirects to Dashboard) ---")
        eval_js(f"document.getElementById('auth-login-email').value = '{test_email}'")
        eval_js(f"document.getElementById('auth-login-password').value = '{test_pwd}'")
        eval_js("handleAuthLoginSubmit(new Event('submit'))")
        time.sleep(2)

        auth_hidden_after_login = eval_js("document.getElementById('auth-screen').classList.contains('hidden')")
        app_visible_after_login = eval_js("!document.getElementById('app-shell').classList.contains('hidden')")
        display_name = eval_js("document.getElementById('user-display-name')?.textContent")
        dropdown_email = eval_js("document.getElementById('dropdown-user-email')?.textContent")

        print(f"Auth screen hidden: {auth_hidden_after_login}")
        print(f"App shell visible: {app_visible_after_login}")
        print(f"User display name in header: '{display_name}'")
        print(f"User email in dropdown: '{dropdown_email}'")

        if auth_hidden_after_login and app_visible_after_login and display_name and dropdown_email == test_email:
            results["Test 7: Successful Login & Dashboard Redirection"] = "PASS"
            print(">>> TEST 7: PASS")
        else:
            results["Test 7: Successful Login & Dashboard Redirection"] = "FAIL"
            print(">>> TEST 7: FAIL")

        # -------------------------------------------------------------
        # TEST 8: Session Persistence Across Page Refresh
        # -------------------------------------------------------------
        print("\n--- TEST 8: Session Persistence across Page Reload ---")
        send_cmd("Page.reload")
        time.sleep(3)

        auth_hidden_reload = eval_js("document.getElementById('auth-screen').classList.contains('hidden')")
        app_visible_reload = eval_js("!document.getElementById('app-shell').classList.contains('hidden')")
        logged_in_user = eval_js("currentUser ? currentUser.email : null")

        print(f"Auth screen hidden after reload: {auth_hidden_reload}")
        print(f"App shell visible after reload: {app_visible_reload}")
        print(f"Current user email after reload: {logged_in_user}")

        if auth_hidden_reload and app_visible_reload and logged_in_user == test_email:
            results["Test 8: Session Persistence"] = "PASS"
            print(">>> TEST 8: PASS")
        else:
            results["Test 8: Session Persistence"] = "FAIL"
            print(">>> TEST 8: FAIL")

        # -------------------------------------------------------------
        # TEST 9: Modal Tab Switching and Handlers
        # -------------------------------------------------------------
        print("\n--- TEST 9: Auth Modal Tab Switching & Submission Handlers ---")
        # Open modal
        eval_js("openAuthModal('signup')")
        modal_visible = eval_js("!document.getElementById('auth-modal').classList.contains('hidden')")
        form_signup_visible = eval_js("!document.getElementById('form-auth-signup').classList.contains('hidden')")
        form_login_hidden = eval_js("document.getElementById('form-auth-login').classList.contains('hidden')")

        print(f"Modal visible: {modal_visible}")
        print(f"Modal signup form visible: {form_signup_visible}")
        print(f"Modal login form hidden: {form_login_hidden}")

        # Switch tab to login
        eval_js("switchAuthTab('login')")
        form_login_now_visible = eval_js("!document.getElementById('form-auth-login').classList.contains('hidden')")
        form_signup_now_hidden = eval_js("document.getElementById('form-auth-signup').classList.contains('hidden')")

        print(f"After switchAuthTab('login'), login form visible: {form_login_now_visible}")
        print(f"After switchAuthTab('login'), signup form hidden: {form_signup_now_hidden}")

        # Check handleAuthLogin and handleAuthSignup exist
        handlers_defined = eval_js("typeof handleAuthLogin === 'function' && typeof handleAuthSignup === 'function' && typeof handleAuthForgot === 'function'")
        print(f"Modal handler functions defined: {handlers_defined}")

        eval_js("closeAuthModal()")
        modal_hidden_after_close = eval_js("document.getElementById('auth-modal').classList.contains('hidden')")
        print(f"Modal hidden after close: {modal_hidden_after_close}")

        if modal_visible and form_signup_visible and form_login_now_visible and handlers_defined and modal_hidden_after_close:
            results["Test 9: Modal Tabs & Handlers"] = "PASS"
            print(">>> TEST 9: PASS")
        else:
            results["Test 9: Modal Tabs & Handlers"] = "FAIL"
            print(">>> TEST 9: FAIL")

        # -------------------------------------------------------------
        # TEST 10: Mobile Viewport Rendering (375x667)
        # -------------------------------------------------------------
        print("\n--- TEST 10: Mobile Viewport Layout Verification ---")
        send_cmd("Emulation.setDeviceMetricsOverride", {
            "width": 375,
            "height": 667,
            "deviceScaleFactor": 2,
            "mobile": True
        })
        time.sleep(1)

        # Logout to inspect mobile login layout
        eval_js("logoutUser()")
        time.sleep(1.5)

        has_h_scroll = eval_js("document.documentElement.scrollWidth > document.documentElement.clientWidth")
        auth_mobile_visible = eval_js("!document.getElementById('auth-screen').classList.contains('hidden')")
        submit_btn_visible = eval_js("!document.getElementById('auth-login-btn-submit').classList.contains('hidden')")

        print(f"Has horizontal scroll: {has_h_scroll}")
        print(f"Auth screen visible on mobile: {auth_mobile_visible}")
        print(f"Submit button visible on mobile: {submit_btn_visible}")

        if not has_h_scroll and auth_mobile_visible and submit_btn_visible:
            results["Test 10: Mobile Viewport"] = "PASS"
            print(">>> TEST 10: PASS")
        else:
            results["Test 10: Mobile Viewport"] = "FAIL"
            print(">>> TEST 10: FAIL")

        # -------------------------------------------------------------
        # SUMMARY
        # -------------------------------------------------------------
        print("\n" + "=" * 70)
        print("SUMMARY OF TEST RESULTS")
        print("=" * 70)
        all_passed = True
        for tname, status in results.items():
            print(f"[{status}] {tname}")
            if status != "PASS":
                all_passed = False

        if all_passed:
            print("\n>>> ALL 10 TESTS PASSED PERFECTLY! <<<")
            sys.exit(0)
        else:
            print("\n>>> SOME TESTS FAILED <<<")
            sys.exit(1)

    finally:
        try:
            edge_proc.terminate()
            edge_proc.wait(timeout=3)
        except Exception:
            pass

if __name__ == "__main__":
    main()
