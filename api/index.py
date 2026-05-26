import os
import sys

# Add the project root and apps/backend to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "apps", "backend"))

from apps.backend.app.main import create_app

app = create_app()
