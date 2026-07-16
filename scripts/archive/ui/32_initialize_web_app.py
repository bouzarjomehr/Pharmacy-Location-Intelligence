from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

web = ROOT / "web"

folders = [
    "css",
    "js",
    "pages",
    "data",
    "assets",
    "assets/icons",
    "assets/images",
    "components",
]

for folder in folders:
    (web / folder).mkdir(parents=True, exist_ok=True)

files = {
    "index.html": "",
    "css/style.css": "",
    "js/app.js": "",
    "js/map.js": "",
    "js/api.js": "",
}

for file in files:
    path = web / file

    if not path.exists():
        path.write_text("", encoding="utf8")

print("=" * 60)
print("WEB APP INITIALIZED")
print("=" * 60)

print()

for p in sorted(web.rglob("*")):
    print(p.relative_to(web))