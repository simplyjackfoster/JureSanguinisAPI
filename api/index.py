import os
import sys
from pathlib import Path

from asgiref.wsgi import WsgiToAsgi
from django.core.wsgi import get_wsgi_application

# Ensure project root is on sys.path so Django can be imported when deployed.
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "juresanguinisapi.settings")

# Vercel's Python runtime expects an ASGI-compatible application called `app`.
app = WsgiToAsgi(get_wsgi_application())
