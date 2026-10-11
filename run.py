"""
Quiet Corner Finder - Application Runner
Launches the Flask web server with backend and frontend integration.
"""
import sys
import os

# Add backend directory to module search path
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import create_app

if __name__ == '__main__':
    app = create_app()
    print("===============================================================")
    print("  Quiet Corner Finder is running on http://localhost:5000")
    print("  To access from mobile phone: use your laptop's Hotspot IP:5000")
    print("===============================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
