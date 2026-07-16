from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WEB = ROOT / "web"
JS = WEB / "js"

FILES = {

    "map.js": """
let map;

export function initializeMap(){

    map = L.map("map").setView([31.8974,54.3569],13);

    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            attribution:"© OpenStreetMap"
        }
    ).addTo(map);

    return map;
}

export function getMap(){
    return map;
}
""",

    "layers.js": """
export let roadLayer;
export let facilityLayer;
export let candidateLayer;
""",

    "dataLoader.js": """
export async function loadGeoJSON(path){

    const response = await fetch(path);

    return await response.json();

}
""",

    "popup.js": """
export function buildCandidatePopup(feature){

    const p = feature.properties;

    return `
    <b>${p.candidate_id}</b><br>
    Score : ${p.final_score.toFixed(2)}<br>
    Road : ${p.road_type}
    `;

}
""",

    "utils.js": """
export function colorFromScore(r){

    if(r>=0.80) return "#006400";

    if(r>=0.60) return "#228B22";

    if(r>=0.40) return "#32CD32";

    if(r>=0.20) return "#7CFC00";

    return "#C8E6C9";

}
"""
}

for name, text in FILES.items():

    path = JS / name

    if not path.exists():

        path.write_text(text.strip(), encoding="utf8")

print("="*60)
print("WEB API CREATED")
print("="*60)

for f in FILES:
    print(f)