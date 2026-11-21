# run_app.py
# ==============================================================================
# NIRVYTH Command Center Launcher
# Hackathon: 13th Protocol: An AI Hackathon 2026 | Team Voyager (KCC ITM)
# Team NIRVYTH: Ravishankar Kushwaha, Piyush Jiloka, Sammi Dubey
# ==============================================================================

import webbrowser
import threading
import time
from nirvyth_app import main

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:8080")

if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    main()
