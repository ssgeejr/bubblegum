from flask import Flask, send_file, abort
import os, requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

app = Flask(__name__)
CACHE_DIR = "favicons"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def safe_filename(domain):
    return domain.replace("/", "_").replace(":", "_")

def try_download(url, filename):
    try:
        response = requests.get(url, headers=HEADERS, timeout=5, stream=True)
        if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
            with open(filename, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
    except Exception:
        pass
    return False

@app.route("/favicon/<path:domain>")
def get_favicon(domain):
    os.makedirs(CACHE_DIR, exist_ok=True)
    filename = os.path.join(CACHE_DIR, safe_filename(domain) + ".ico")

    if os.path.exists(filename):
        return send_file(filename)

    # 1. Try default /favicon.ico
    base_url = f"https://{domain}"
    default_favicon = urljoin(base_url, "/favicon.ico")
    if try_download(default_favicon, filename):
        return send_file(filename)

    # 2. Parse HTML for <link rel="icon">
    try:
        html = requests.get(base_url, headers=HEADERS, timeout=5).text
        soup = BeautifulSoup(html, "html.parser")
        icon_tags = soup.find_all("link", rel=lambda x: x and 'icon' in x.lower())

        for tag in icon_tags:
            href = tag.get("href")
            if href:
                icon_url = urljoin(base_url, href)
                if try_download(icon_url, filename):
                    return send_file(filename)
    except Exception:
        pass

    # 3. Fallback to DuckDuckGo's shared CDN
    fallback_url = f"https://icons.duckduckgo.com/ip3/{domain}.ico"
    if try_download(fallback_url, filename):
        return send_file(filename)

    abort(404, description="Favicon not found")
