from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"

html = """<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<title>Pharmacy Location Intelligence</title>

<link rel="stylesheet" href="css/style.css">

</head>

<body>

<div id="container">

    <aside id="sidebar">

        <h2>PLI</h2>

        <button>🏠 Dashboard</button>

        <button>🗺 Map</button>

        <button>🏥 Data</button>

        <button>⚙ Scoring</button>

        <button>▶ Run Pipeline</button>

        <button>📈 Results</button>

        <button>💾 Profiles</button>

        <button>🔧 Settings</button>

    </aside>

    <main id="content">

        <h1>Pharmacy Location Intelligence</h1>

        <p>Version 1.0</p>

        <div id="workspace">

            Workspace

        </div>

    </main>

</div>

<script src="js/app.js"></script>

</body>

</html>
"""

css = """
html,body{

margin:0;

padding:0;

height:100%;

font-family:Segoe UI,Arial;

}

#container{

display:flex;

height:100vh;

}

#sidebar{

width:240px;

background:#203040;

color:white;

padding:20px;

display:flex;

flex-direction:column;

gap:10px;

}

#sidebar h2{

margin-bottom:20px;

}

#sidebar button{

padding:12px;

border:none;

cursor:pointer;

background:#30475a;

color:white;

border-radius:6px;

text-align:left;

font-size:15px;

}

#sidebar button:hover{

background:#46637d;

}

#content{

flex:1;

padding:30px;

background:#f3f5f7;

}

#workspace{

margin-top:20px;

height:700px;

background:white;

border-radius:8px;

border:1px solid #ddd;

display:flex;

justify-content:center;

align-items:center;

font-size:24px;

color:#777;

}
"""

js = """
console.log("Dashboard Loaded");
"""

(WEB/"index.html").write_text(html,encoding="utf8")
(WEB/"css"/"style.css").write_text(css,encoding="utf8")
(WEB/"js"/"app.js").write_text(js,encoding="utf8")

print("="*60)
print("Dashboard Created")
print("="*60)