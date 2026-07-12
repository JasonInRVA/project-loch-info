from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import hashlib
import json
import re
import requests

ROOT = Path.cwd()
DOCS = ROOT / "docs"
SEEDS = [
    "https://www.nao.usace.army.mil/Media/Public-Notices/Article/4484789/nao-2026-00182-vmrc-project-loch-chesterfield-county-virginia-wauford-prm-site/",
    "https://webapps.mrc.virginia.gov/public/habitat/additionaldocs.php?id=20260171",
]
ALLOWED_HOSTS = {
    "www.nao.usace.army.mil",
    "nao.usace.army.mil",
    "publibrary.sec.usace.army.mil",
    "webapps.mrc.virginia.gov",
    "www.deq.virginia.gov",
    "deq.virginia.gov",
}

for name in ["usace", "vmrc", "deq", "chesterfield", "google", "maps", "media", "source-pages"]:
    (DOCS / name).mkdir(parents=True, exist_ok=True)

def safe_name(value: str) -> str:
    value = re.sub(r'[<>:"/\\|?*]+', "_", value)
    value = re.sub(r"\s+", "_", value.strip())
    return value[:180] or "document"

def folder_for(url: str) -> Path:
    host = urlparse(url).netloc.lower()
    if "usace" in host or "army.mil" in host:
        return DOCS / "usace"
    if "mrc.virginia.gov" in host:
        return DOCS / "vmrc"
    if "deq.virginia.gov" in host:
        return DOCS / "deq"
    return DOCS / "media"

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

manifest = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(accept_downloads=True)

    discovered = set()

    for seed in SEEDS:
        print(f"Opening {seed}")
        page = context.new_page()
        page.goto(seed, wait_until="networkidle", timeout=90000)

        html = page.content()
        title = page.title() or urlparse(seed).netloc
        snapshot = DOCS / "source-pages" / safe_name(title + ".html")
        snapshot.write_text(html, encoding="utf-8")

        soup = BeautifulSoup(html, "lxml")
        for a in soup.find_all("a", href=True):
            href = urljoin(seed, a["href"])
            host = urlparse(href).netloc.lower()
            text = " ".join(a.get_text(" ", strip=True).split())
            lower = f"{href} {text}".lower()

            if host not in ALLOWED_HOSTS:
                continue

            if any(token in lower for token in [
                ".pdf",
                "getadd.php",
                "/api/download",
                "attachment",
                "download",
                "additional information",
                "response package",
                "public notice",
                "non-jurisdiction",
            ]):
                discovered.add((href, text or Path(urlparse(href).path).name, seed))

        page.close()

    browser.close()

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/149 Safari/537.36"
})

for url, title, source_page in sorted(discovered):
    print(f"Downloading {url}")
    try:
        response = session.get(url, timeout=60, allow_redirects=True)
        response.raise_for_status()
    except Exception as exc:
        print(f"  FAILED: {exc}")
        continue

    data = response.content
    content_type = response.headers.get("content-type", "").split(";")[0]
    parsed_response_url = urlparse(response.url)
    name = Path(parsed_response_url.path).name or safe_name(title)

    if parsed_response_url.path.endswith("getADD.php"):
        match = re.search(r"[?&]id=(\d+)", url)
        if match:
            name = f"VMRC_JPA-26-0171_Document_{match.group(1)}"

    if "filename=" in url:
        match = re.search(r"filename=([^&]+)", url)
        if match:
            name = match.group(1)

    if data.startswith(b"%PDF") and not name.lower().endswith(".pdf"):
        name += ".pdf"
    elif "text/html" in content_type and not name.lower().endswith(".html"):
        name += ".html"

    name = safe_name(name)
    path = folder_for(url) / name
    path.write_bytes(data)

    manifest.append({
        "title": title,
        "original_url": url,
        "source_page": source_page,
        "archived_path": str(path.relative_to(ROOT)),
        "content_type": content_type,
        "size_bytes": len(data),
        "sha256": sha256(data),
    })

(DOCS / "manifest.json").write_text(
    json.dumps(manifest, indent=2) + "\n",
    encoding="utf-8",
)

print(f"Saved {len(manifest)} documents")
print("Manifest: docs/manifest.json")
