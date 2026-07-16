from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WEB = ROOT / "web"

# ---------------------------------------------------
# Sidebar HTML
# ---------------------------------------------------

sidebar = """
<div id="sidebar">

<h2>Scoring Engine</h2>

<div class="section">

<label>Hospital Weight</label>
<input id="hospitalWeight"
       type="range"
       min="0"
       max="20"
       step="1"
       value="8">

<label>Clinic Weight</label>
<input id="clinicWeight"
       type="range"
       min="0"
       max="20"
       step="1"
       value="4">

<label>Doctor Weight</label>
<input id="doctorWeight"
       type="range"
       min="0"
       max="20"
       step="1"
       value="2">

<label>Pharmacy Penalty</label>
<input id="pharmacyWeight"
       type="range"
       min="-20"
       max="0"
       step="1"
       value="-6">

</div>

<hr>

<div class="section">

<label>Search Radius (m)</label>
<input id="radius"
       type="range"
       min="100"
       max="1500"
       step="50"
       value="800">

<label>Sigma</label>
<input id="sigma"
       type="range"
       min="50"
       max="800"
       step="25"
       value="250">

</div>

<hr>

<div class="section">

<button id="applyButton">

Apply Changes

</button>

</div>

</div>
"""

(WEB / "components" / "scoringPanel.html").write_text(
    sidebar,
    encoding="utf8"
)

# ---------------------------------------------------
# CSS
# ---------------------------------------------------

css = """

#sidebar{

position:absolute;

top:15px;

left:15px;

width:290px;

background:white;

padding:15px;

border-radius:12px;

box-shadow:0 0 12px rgba(0,0,0,.25);

z-index:9999;

font-family:Arial;

}

#sidebar h2{

margin-top:0;

}

#sidebar label{

display:block;

margin-top:12px;

font-size:13px;

}

#sidebar input{

width:100%;

}

#sidebar button{

margin-top:15px;

width:100%;

height:42px;

font-weight:bold;

cursor:pointer;

}
"""

with open(WEB / "css" / "style.css", "a", encoding="utf8") as f:
    f.write(css)

# ---------------------------------------------------
# JS placeholder
# ---------------------------------------------------

js = """
export function initializeScoringPanel(){

    console.log("Scoring panel ready.");

}
"""

(WEB / "js" / "scoringPanel.js").write_text(
    js,
    encoding="utf8"
)

print("=" * 60)
print("SCORING PANEL CREATED")
print("=" * 60)

print(WEB / "components" / "scoringPanel.html")
print(WEB / "js" / "scoringPanel.js")