from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

folders = [
    "data",
    "data/raw",
    "data/processed",
    "data/cache",
    "data/manual",
    "outputs",
    "logs",
    "docs",
    "scripts",
]

files = [
    "README.md",
    "CHANGELOG.md",
    "requirements.txt",
    "config.py",
    "docs/DEVLOG.md",
    "docs/DECISION_LOG.md",
    "docs/PROJECT_SCOPE.md",
]

for folder in folders:
    path = ROOT / folder
    path.mkdir(parents=True, exist_ok=True)
    print(f"📁 {folder}")

for file in files:
    path = ROOT / file
    path.touch(exist_ok=True)
    print(f"📄 {file}")

print("\n✅ Project initialized successfully.")