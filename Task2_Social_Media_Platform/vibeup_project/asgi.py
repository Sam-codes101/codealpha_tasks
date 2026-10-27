import os
import sys
from pathlib import Path

# Add project root to sys.path so direct execution finds vibeup_project
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vibeup_project.settings')

from django.core.asgi import get_asgi_application

application = get_asgi_application()
