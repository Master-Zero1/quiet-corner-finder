"""
Main application factory and entry point for Quiet Corner Finder.
Mobile-first campus space finder using decay-weighted crowd/noise reports,
confidence freshness tiers, hour-of-day baselines, and self-measured accuracy.
"""
import os
import sys

# Ensure backend directory is in sys.path when executed directly or imported
BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from flask import Flask, render_template, jsonify
import config
from models import init_db
from routes import spaces_bp, reports_bp, stats_bp, demo_bp

PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, '..'))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')
TEMPLATE_DIR = os.path.join(FRONTEND_DIR, 'templates')
STATIC_DIR = os.path.join(FRONTEND_DIR, 'static')

def create_app():
    app = Flask(
        __name__,
        template_folder=TEMPLATE_DIR,
        static_folder=STATIC_DIR
    )
    app.config.from_object(config)

    # Initialize DB tables if they don't exist
    init_db()

    # Register API blueprints
    app.register_blueprint(spaces_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(demo_bp)

    @app.route('/')
    def index():
        return render_template('index.html', demo_mode=config.DEMO_MODE)

    @app.route('/api/health')
    def health():
        return jsonify({
            "ok": True,
            "service": "Quiet Corner Finder API",
            "demo_mode": config.DEMO_MODE
        })

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    print("===============================================================")
    print("  Quiet Corner Finder is running on http://localhost:5000")
    print("  To access from mobile phone: use your laptop's Hotspot IP:5000")
    print("===============================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
