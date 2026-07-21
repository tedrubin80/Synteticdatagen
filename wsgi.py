"""WSGI entrypoint for Railway, Vercel, and other hosts.

Exposes a module-level ``app`` so platforms that expect ``wsgi:app``
(or auto-detect ``wsgi.py``) can run the Flask application without
knowing about the factory in ``web/app.py``.
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ROOT, "web")

# Repo root (core/, formatters/) and web/ (config, blueprints, templates)
for path in (ROOT, WEB):
    if path not in sys.path:
        sys.path.insert(0, path)

from app import create_app  # noqa: E402  — web/app.py after path setup

app = create_app()
