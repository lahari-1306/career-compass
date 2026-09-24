import subprocess
import time
import json
import urllib.request
import websocket
import threading
import sys
from app import app

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def run_flask():
    app.run(host='127.0.0.1', port=5056, debug=False, use_reloader=False)

def main():
    print("Starting Flask server on port 5056...")
    server_thread = threading.Thread(target=run_flask, daemon=True)
    server_thread.start()
    time.sleep(2)

    edge_profile_dir = r"C:\Users\jagarapu lahari\.gemini\antigravity\scratch\career-compass\edge_profile"
    edge_cmd = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--remote-debugging-port=9223",
        "--remote-allow-origins=*",
        f"--user-data-dir={edge_profile_dir}",
        "http://127.0.0.1:5056"
    ]
    print("Launching Edge headless on debug port 9223...")
    edge_proc = subprocess.Popen(edge_cmd)

    targets = None
    for attempt in range(15):
        time.sleep(1)
        try:
            res = urllib.request.urlopen("http://127.0.0.1:9223/json", timeout=2)
            targets = json.loads(res.read().decode('utf-8'))
            if any('5056' in t.get('url', '') for t in targets):
                break
        except Exception:
            continue

    if not targets:
        print("ERROR: Could not connect to Edge on port 9223")
        edge_proc.terminate()
        sys.exit(1)

    try:
        ws_url = None
        for t in targets:
            if t.get('type') == 'page' and '5056' in t.get('url', ''):
                ws_url = t.get('webSocketDebuggerUrl')
                break

        if not ws_url:
            print("ERROR: Could not find 5056 page target in CDP")
            sys.exit(1)

        print(f"Connected to CDP page: {ws_url}")
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

        time.sleep(2)
        print("Page Title:", eval_js("document.title"))

        # TEST 1: Navigation to Exam Prep Hub
        print("\n--- TEST 1: Navigate to Exam Preparation Hub ---")
        eval_js("navigateToSection('exam-prep')")
        time.sleep(1.5)
        active_sec = eval_js("document.getElementById('section-exam-prep').classList.contains('active')")
        print(f"Exam Prep section is active: {active_sec}")
        assert active_sec is True

        card_count = eval_js("document.querySelectorAll('#exam-prep-grid .exam-prep-card').length")
        print(f"Exam prep cards rendered count: {card_count}")
        assert card_count >= 8, f"Expected at least 8 exam prep blueprints, found {card_count}"
        print("TEST 1 PASSED: Exam Prep Hub navigated and cards rendered!")

        # TEST 2: Filter and Search Exam Blueprints
        print("\n--- TEST 2: Filter & Search Exam Prep Hub ---")
        eval_js("document.getElementById('exam-prep-search-input').value = 'GATE'; filterExamPrepCards();")
        time.sleep(0.5)
        gate_cards = eval_js("document.querySelectorAll('#exam-prep-grid .exam-prep-card').length")
        print(f"Cards matching 'GATE': {gate_cards}")
        assert gate_cards >= 2

        eval_js("filterExamPrepCategory('Medical')")
        time.sleep(0.5)
        med_cards = eval_js("document.querySelectorAll('#exam-prep-grid .exam-prep-card').length")
        print(f"Cards matching 'Medical': {med_cards}")
        assert med_cards >= 1

        eval_js("filterExamPrepCategory('All')")
        time.sleep(0.5)
        print("TEST 2 PASSED: Exam search & category filtering working accurately!")

        # TEST 3: Open 24-Point Blueprint Modal for GATE CSE
        print("\n--- TEST 3: 24-Point Blueprint Modal (GATE CSE) ---")
        eval_js("openExamDetailModal('gate-cse')")
        time.sleep(1)
        modal_open = eval_js("!document.getElementById('exam-detail-modal').classList.contains('hidden')")
        assert modal_open is True
        title_text = eval_js("document.getElementById('exam-detail-header').querySelector('h2').textContent")
        print(f"Exam blueprint modal title: '{title_text}'")
        assert "GATE" in title_text and "Computer Science" in title_text

        # Test tabs
        eval_js("switchExamDetailTab('syllabus')")
        time.sleep(0.5)
        topic_count = eval_js("document.querySelectorAll('.topic-checklist-item').length")
        print(f"Syllabus topics checklist count: {topic_count}")
        assert topic_count >= 10

        eval_js("switchExamDetailTab('books')")
        time.sleep(0.5)
        book_count = eval_js("document.querySelectorAll('.book-card').length")
        print(f"Verified standard textbooks count: {book_count}")
        assert book_count >= 3

        eval_js("switchExamDetailTab('pyqs')")
        time.sleep(0.5)
        pyq_present = eval_js("document.getElementById('exam-detail-body').textContent.includes('Official PDF')")
        assert pyq_present is True
        print("Verified official PYQs and mock simulators present!")

        eval_js("switchExamDetailTab('strategy')")
        time.sleep(0.5)
        strategy_present = eval_js("document.getElementById('exam-detail-body').textContent.includes('6-Month Comprehensive')")
        assert strategy_present is True
        print("Verified multi-phase study plans present!")

        eval_js("closeExamDetailModal()")
        time.sleep(0.5)
        print("TEST 3 PASSED: 24-Point blueprint tabs and content verified!")

        # TEST 4: User Authentication (Sign Up & Session State)
        print("\n--- TEST 4: User Registration & Session Persistence ---")
        eval_js("openAuthModal('signup')")
        time.sleep(0.5)
        unique_email = f"priya.{int(time.time())}@example.com"
        eval_js(f"""
            document.getElementById('signup-name').value = 'Priya Sharma';
            document.getElementById('signup-email').value = '{unique_email}';
            document.getElementById('signup-qual').value = 'B.Tech';
            document.getElementById('signup-branch').value = 'CSE';
            document.getElementById('signup-password').value = 'CompassPass2026!';
            document.getElementById('signup-password-confirm').value = 'CompassPass2026!';
        """)
        eval_js("handleAuthSignup({ preventDefault: () => {} })")
        time.sleep(2)

        # Confirm user profile menu is visible
        user_menu_visible = eval_js("!document.getElementById('user-profile-menu').classList.contains('hidden')")
        print(f"User profile chip visible: {user_menu_visible}")
        assert user_menu_visible is True

        user_name = eval_js("document.getElementById('user-display-name').textContent")
        avatar_initials = eval_js("document.getElementById('user-avatar-initials').textContent")
        print(f"Display Name: '{user_name}', Initials: '{avatar_initials}'")
        assert "Priya" in user_name
        assert avatar_initials == "PS"
        print("TEST 4 PASSED: User successfully registered, session established, header updated!")

        # TEST 5: Interactive Topic Checklist Save (Authenticated)
        print("\n--- TEST 5: Interactive Topic Progress Checklist Save ---")
        eval_js("openExamDetailModal('gate-cse')")
        time.sleep(1)
        eval_js("switchExamDetailTab('syllabus')")
        time.sleep(0.5)

        # Check the first topic
        eval_js("""
            const firstBox = document.querySelector('.topic-checklist-item input[type="checkbox"]');
            firstBox.checked = true;
            firstBox.dispatchEvent(new Event('change'));
        """)
        time.sleep(1)

        # Re-open and verify persistence
        eval_js("closeExamDetailModal()")
        time.sleep(0.5)
        eval_js("openExamDetailModal('gate-cse')")
        time.sleep(1)
        eval_js("switchExamDetailTab('syllabus')")
        time.sleep(0.5)

        first_checked = eval_js("document.querySelector('.topic-checklist-item input[type=\"checkbox\"]').checked")
        print(f"First topic checklist item checked after reload: {first_checked}")
        assert first_checked is True
        eval_js("closeExamDetailModal()")
        print("TEST 5 PASSED: Topic checklist progress persists to DB for authenticated student!")

        # TEST 6: Bookmark / Saved Opportunities
        print("\n--- TEST 6: Saved Opportunities ---")
        eval_js("saveOpportunity('gate-cse', 'GATE CSE 2026', 'IIT Guwahati', 'Entrance Exam', 'See Blueprint', 'https://gate2026.iitg.ac.in')")
        time.sleep(1)
        eval_js("openSavedOpportunitiesModal()")
        time.sleep(1)
        saved_items = eval_js("document.querySelectorAll('#saved-opps-list > div').length")
        print(f"Saved opportunities count: {saved_items}")
        assert saved_items >= 1
        eval_js("closeSavedOpportunitiesModal()")
        print("TEST 6 PASSED: Saved opportunities stored and viewed cleanly!")

        # TEST 7: Logout
        print("\n--- TEST 7: Logout & Guest State Reversion ---")
        eval_js("logoutUser()")
        time.sleep(1)
        login_btn_visible = eval_js("!document.getElementById('auth-login-btn').classList.contains('hidden')")
        user_menu_hidden = eval_js("document.getElementById('user-profile-menu').classList.contains('hidden')")
        print(f"Login button restored: {login_btn_visible}, User menu hidden: {user_menu_hidden}")
        assert login_btn_visible is True
        assert user_menu_hidden is True
        print("TEST 7 PASSED: Logout clears session and restores guest UI cleanly!")

        print("\n=======================================================")
        print("ALL 7 PRODUCTION SYSTEM BROWSER TESTS PASSED SUCCESSFULLY!")
        print("=======================================================")

    finally:
        edge_proc.terminate()

if __name__ == '__main__':
    main()
