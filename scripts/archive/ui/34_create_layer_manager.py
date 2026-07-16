from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

JS = ROOT / "web" / "js"

code = r'''
import {getMap} from "./map.js";
import {buildCandidatePopup} from "./popup.js";
import {colorFromScore} from "./utils.js";

export let roadLayer;
export let facilityLayer;
export let candidateLayer;

export function createRoadLayer(geojson){

    roadLayer = L.geoJSON(geojson,{
        style:{
            color:"#888",
            weight:1,
            opacity:0.4
        }
    });

    return roadLayer;
}

export function createFacilityLayer(geojson){

    facilityLayer = L.geoJSON(geojson,{

        pointToLayer:function(feature,latlng){

            const t = feature.properties.type;

            let color="#666";

            if(t==="Doctor") color="#9ecae1";

            else if(t==="Clinic") color="#3182bd";

            else if(t==="Hospital") color="#08519c";

            else if(t==="Pharmacy") color="#7b1fa2";

            return L.circleMarker(latlng,{
                radius:4,
                color:color,
                fillColor:color,
                fillOpacity:0.9
            });

        }

    });

    return facilityLayer;

}

export function createCandidateLayer(geojson){

    let maxScore = 0;

    geojson.features.forEach(f=>{

        if(f.properties.final_score>maxScore)
            maxScore=f.properties.final_score;

    });

    candidateLayer = L.geoJSON(geojson,{

        pointToLayer:function(feature,latlng){

            const ratio =
                feature.properties.final_score/maxScore;

            const color=colorFromScore(ratio);

            return L.circleMarker(latlng,{

                radius:7,

                color:color,

                fillColor:color,

                fillOpacity:0.9

            });

        },

        onEachFeature:function(feature,layer){

            layer.bindPopup(
                buildCandidatePopup(feature)
            );

        }

    });

    return candidateLayer;

}

export function addDefaultLayers(){

    const map=getMap();

    roadLayer.addTo(map);

    facilityLayer.addTo(map);

    candidateLayer.addTo(map);

}
'''

(JS/"layerManager.js").write_text(
    code,
    encoding="utf8"
)

print("="*60)
print("LAYER MANAGER CREATED")
print("="*60)
print(JS/"layerManager.js")