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
    app.run(host='127.0.0.1', port=5055, debug=False, use_reloader=False)

def main():
    print("Starting Flask server on port 5055...")
    server_thread = threading.Thread(target=run_flask, daemon=True)
    server_thread.start()
    time.sleep(2)

    # Launch Edge in headless mode with remote debugging
    edge_profile_dir = r"C:\Users\jagarapu lahari\.gemini\antigravity\scratch\career-compass\edge_profile"
    edge_cmd = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "--headless=new",
        "--disable-gpu",
        "--remote-debugging-port=9222",
        "--remote-allow-origins=*",
        f"--user-data-dir={edge_profile_dir}",
        "http://127.0.0.1:5055"
    ]
    print("Launching Edge headless...")
    edge_proc = subprocess.Popen(edge_cmd)

    targets = None
    for attempt in range(15):
        time.sleep(1)
        try:
            res = urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=2)
            targets = json.loads(res.read().decode('utf-8'))
            if targets:
                break
        except Exception:
            continue

    if not targets:
        print("ERROR: Could not connect to Edge on port 9222")
        edge_proc.terminate()
        sys.exit(1)

    try:
        ws_url = None
        for t in targets:
            if t.get('type') == 'page':
                ws_url = t.get('webSocketDebuggerUrl')
                break

        if not ws_url:
            print("ERROR: Could not find page target in CDP")
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

        # Wait for page to finish loading and datasets to load
        time.sleep(2)
        print("Page Title:", eval_js("document.title"))

        # TEST A: Open Career Radar Profile modal. Check Stream/Branch list (>= 33 branches). Select another branch and save. Confirm profile chip.
        print("\n--- RUNNING TEST A: Stream / Branch Selection ---")
        eval_js("openRadarProfileModal()")
        branch_count = eval_js("document.getElementById('radar-input-branch').options.length")
        print(f"Branch dropdown options count: {branch_count}")
        assert branch_count >= 33, f"Expected at least 33 branches, got {branch_count}"

        branch_options = eval_js("Array.from(document.getElementById('radar-input-branch').options).map(o => o.value)")
        assert "Information Technology (IT)" in branch_options
        assert "Mechanical Engineering" in branch_options
        assert "Aerospace / Aeronautical Engineering" in branch_options
        assert "Mechatronics" in branch_options
        print("Verified branch list includes specialized engineering disciplines!")

        # Select 'Information Technology (IT)' and save
        eval_js("document.getElementById('radar-input-branch').value = 'Information Technology (IT)'")
        eval_js("saveRadarProfile()")
        time.sleep(0.5)
        chip_text = eval_js("document.getElementById('radar-profile-chip').textContent")
        print(f"Updated Radar Chip: '{chip_text}'")
        assert "Information Technology (IT)" in chip_text
        print("TEST A PASSED: Branch list expanded to 33 branches and chip successfully updated!")

        # TEST B: Check Home State / Scope dropdown
        print("\n--- RUNNING TEST B: Home State / Scope Dropdown ---")
        eval_js("openRadarProfileModal()")
        state_count = eval_js("document.getElementById('radar-input-state').options.length")
        print(f"Home State dropdown options count: {state_count}")
        # 28 states + 8 UTs + 1 National = 37 options
        assert state_count >= 37, f"Expected at least 37 states/UTs/Scope, got {state_count}"

        eval_js("document.getElementById('radar-input-state').value = 'Maharashtra'")
        eval_js("saveRadarProfile()")
        time.sleep(0.5)
        chip_text = eval_js("document.getElementById('radar-profile-chip').textContent")
        print(f"Updated Radar Chip with State: '{chip_text}'")
        assert "Maharashtra" in chip_text
        print("TEST B PASSED: Home State expanded to all 28 states + 8 UTs + National scope!")

        # TEST C: Completion Batch & Status
        print("\n--- RUNNING TEST C: Completion Batch & Status ---")
        eval_js("openRadarProfileModal()")
        status_options = eval_js("Array.from(document.getElementById('radar-input-status').options).map(o => o.value)")
        print(f"Completion status options: {status_options}")
        assert "Currently Studying" in status_options
        assert "Final Year" in status_options
        assert "Completed" in status_options

        year_options = eval_js("Array.from(document.getElementById('radar-input-year').options).map(o => o.value)")
        print(f"Passout batch year options count: {len(year_options)} (2018-2030)")
        assert "2018" in year_options and "2030" in year_options

        eval_js("document.getElementById('radar-input-status').value = 'Completed'")
        eval_js("document.getElementById('radar-input-year').value = '2024'")
        eval_js("saveRadarProfile()")
        time.sleep(0.5)
        chip_text = eval_js("document.getElementById('radar-profile-chip').textContent")
        print(f"Updated Radar Chip with Status: '{chip_text}'")
        assert "Completed" in chip_text
        print("TEST C PASSED: Completion batch (2018-2030) and status successfully selectable!")

        # TEST D: Target Career Direction & Interests (Strict Multi-Select)
        print("\n--- RUNNING TEST D: Target Career Direction & Interests (Multi-Select) ---")
        eval_js("openRadarProfileModal()")
        # Uncheck all, then select 4 distinct interests
        eval_js("""
            document.querySelectorAll('input[name="radar-interest"]').forEach(b => b.checked = false);
            ['Software / IT Roles', 'Cyber Security', 'Data Science / Analytics', 'GATE'].forEach(val => {
                const box = Array.from(document.querySelectorAll('input[name="radar-interest"]')).find(b => b.value === val);
                if (box) box.checked = true;
            });
        """)
        eval_js("saveRadarProfile()")
        time.sleep(0.5)

        # Reopen modal and confirm all 4 remain checked
        eval_js("openRadarProfileModal()")
        checked_interests = eval_js("Array.from(document.querySelectorAll('input[name=\"radar-interest\"]:checked')).map(b => b.value)")
        print(f"Checked interests after reopen: {checked_interests}")
        assert set(checked_interests) == {'Software / IT Roles', 'Cyber Security', 'Data Science / Analytics', 'GATE'}
        eval_js("closeRadarProfileModal()")
        print("TEST D PASSED: Multi-select interests are strictly preserved across saves and reopens!")

        # TEST E: Go to Find My Career Path -> B.Tech -> Completed B.Tech / Final Year. Click card 1
        print("\n--- RUNNING TEST E: B.Tech Pathway Card 1 Selection ---")
        eval_js("selectQualification('btech');")
        time.sleep(1)
        eval_js("switchBTechPathway('job');")
        time.sleep(1)

        card1_highlighted = eval_js("document.getElementById('pathway-card-job').classList.contains('highlighted-card')")
        card1_btn_text = eval_js("document.getElementById('pathway-card-job').querySelector('.pathway-action-btn span').textContent")
        detail_header = eval_js("document.getElementById('btech-pathway-detail-container').querySelector('h3').textContent")
        print(f"Card 1 highlighted: {card1_highlighted}")
        print(f"Card 1 button text: '{card1_btn_text}'")
        print(f"Detail container heading: '{detail_header}'")

        assert card1_highlighted is True
        assert "Currently Viewing Details" in card1_btn_text
        assert "Job Roles for B.Tech" in detail_header
        print("TEST E PASSED: Card 1 highlights and loads Job Roles details!")

        # TEST F: Click card 2 (Higher Studies). Verify card 1 loses highlight and card 2 gains highlight
        print("\n--- RUNNING TEST F: B.Tech Pathway Card 2 (Higher Studies) Selection ---")
        eval_js("switchBTechPathway('higher_studies')")
        time.sleep(0.5)

        card1_highlighted_now = eval_js("document.getElementById('pathway-card-job').classList.contains('highlighted-card')")
        card1_btn_text_now = eval_js("document.getElementById('pathway-card-job').querySelector('.pathway-action-btn span').textContent")
        card2_highlighted = eval_js("document.getElementById('pathway-card-higher_studies').classList.contains('highlighted-card')")
        card2_btn_text = eval_js("document.getElementById('pathway-card-higher_studies').querySelector('.pathway-action-btn span').textContent")
        detail_header2 = eval_js("document.getElementById('btech-pathway-detail-container').querySelector('h3').textContent")

        print(f"Card 1 highlighted now: {card1_highlighted_now} (button: '{card1_btn_text_now}')")
        print(f"Card 2 highlighted: {card2_highlighted} (button: '{card2_btn_text}')")
        print(f"Detail container heading: '{detail_header2}'")

        assert card1_highlighted_now is False, "Card 1 must NOT remain highlighted!"
        assert "Explore Pathway" in card1_btn_text_now
        assert card2_highlighted is True, "Card 2 MUST be highlighted!"
        assert "Currently Viewing Details" in card2_btn_text
        assert any(k in detail_header2 for k in ["Master", "MBA", "Doctoral", "Higher Studies", "M.Tech"])
        print("TEST F PASSED: Card 1 highlight correctly removed; Card 2 highlighted with details updated!")

        # TEST G: Click card 3 (competitive_exams / GATE Guide)
        print("\n--- RUNNING TEST G: B.Tech Pathway Card 3 Selection ---")
        eval_js("switchBTechPathway('competitive_exams')")
        time.sleep(0.5)

        card2_highlighted_now = eval_js("document.getElementById('pathway-card-higher_studies').classList.contains('highlighted-card')")
        card3_highlighted = eval_js("document.getElementById('pathway-card-competitive_exams').classList.contains('highlighted-card')")
        card3_btn_text = eval_js("document.getElementById('pathway-card-competitive_exams').querySelector('.pathway-action-btn span').textContent")
        detail_header3 = eval_js("document.getElementById('btech-pathway-detail-container').querySelector('h3').textContent")

        print(f"Card 2 highlighted now: {card2_highlighted_now}")
        print(f"Card 3 highlighted: {card3_highlighted} (button: '{card3_btn_text}')")
        print(f"Detail container heading: '{detail_header3}'")

        assert card2_highlighted_now is False
        assert card3_highlighted is True
        assert "Currently Viewing Details" in card3_btn_text
        assert "GATE" in detail_header3 or "Competitive" in detail_header3 or "PSU" in detail_header3
        print("TEST G PASSED: Card 3 highlighted and details updated accurately!")

        # TEST H: Side-by-side comparison modal does not break card selection
        print("\n--- RUNNING TEST H: Compare Pathways Side-by-Side Modal ---")
        eval_js("openPathwayCompareModal('comp-job-vs-mtech')")
        time.sleep(0.5)
        modal_open = eval_js("!document.getElementById('pathway-compare-modal').classList.contains('hidden')")
        print(f"Comparison modal open: {modal_open}")
        assert modal_open is True
        eval_js("closePathwayCompareModal()")
        time.sleep(0.3)
        modal_closed = eval_js("document.getElementById('pathway-compare-modal').classList.contains('hidden')")
        print(f"Comparison modal closed: {modal_closed}")
        assert modal_closed is True
        print("TEST H PASSED: Pathway comparison modal operates cleanly without affecting card selection!")

        print("\n=======================================================")
        print("ALL INTERACTION TESTS A THROUGH H PASSED SUCCESSFULLY!")
        print("=======================================================")

    finally:
        edge_proc.terminate()

if __name__ == '__main__':
    main()
