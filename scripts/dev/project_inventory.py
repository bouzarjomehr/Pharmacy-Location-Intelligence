from pathlib import Path
import ast
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

rows = []

for f in sorted((ROOT / "scripts").glob("*.py")):

    try:
        source = f.read_text(encoding="utf-8")
        tree = ast.parse(source)

        imports = []

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):
                imports.extend(
                    [n.name for n in node.names]
                )

            elif isinstance(node, ast.ImportFrom):

                if node.module:
                    imports.append(node.module)

        rows.append({

            "script": f.name,
            "lines": len(source.splitlines()),
            "imports": ", ".join(sorted(set(imports))),
            "functions": len(
                [
                    n for n in tree.body
                    if isinstance(n, ast.FunctionDef)
                ]
            ),
            "classes": len(
                [
                    n for n in tree.body
                    if isinstance(n, ast.ClassDef)
                ]
            )

        })

    except Exception as e:

        rows.append({

            "script": f.name,
            "lines": "",
            "imports": str(e),
            "functions": "",
            "classes": ""

        })

df = pd.DataFrame(rows)

outfile = ROOT / "docs" / "script_inventory.xlsx"

df.to_excel(outfile, index=False)

print("=" * 60)
print(df)
print("=" * 60)
print(outfile)