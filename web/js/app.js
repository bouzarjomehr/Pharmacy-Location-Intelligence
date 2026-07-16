async function start() {

    // ----------------------------------------
    // Load all datasets once
    // ----------------------------------------

    await DataStore.load();

    // ----------------------------------------
    // Initialize map
    // ----------------------------------------

    initializeMap();

    // ----------------------------------------
    // Dashboard
    // ----------------------------------------

Router.register("dashboard", () => {

document.getElementById("sidebar-page").innerHTML = `

        <h3>Dashboard</h3>

        <hr>

        <b>Datasets</b>

        <p>Facilities : ${DataStore.facilities.features.length}</p>
        <p>Candidates : ${DataStore.candidates.features.length}</p>
        <p>Best Areas : ${DataStore.bestAreas.features.length}</p>

        <hr>

        <b>Layers</b>

        <label>
            <input type="checkbox" id="chkRoads" checked>
            Roads
        </label><br>

        <label>
            <input type="checkbox" id="chkHospitals" checked>
            Hospitals
        </label><br>

        <label>
            <input type="checkbox" id="chkClinics" checked>
            Clinics
        </label><br>

        <label>
            <input type="checkbox" id="chkDoctors" checked>
            Doctors
        </label><br>

        <label>
            <input type="checkbox" id="chkPharmacies" checked>
            Pharmacies
        </label><br>

        <label>
            <input type="checkbox" id="chkCandidates" checked>
            Top Candidates
        </label>

    `;

    connectLayerEvents();

});

    // ----------------------------------------
    // Map
    // ----------------------------------------

    Router.register("map", () => {

        document.getElementById("sidebar-page").innerHTML = `

            <h3>Map</h3>

            <hr>

            <p>The interactive map is displayed on the right.</p>

            <p>Use layer controls to show or hide data.</p>

        `;

    });

    // ----------------------------------------
    // Buttons
    // ----------------------------------------

    document.getElementById("btnDashboard").onclick =
        () => Router.load("dashboard");

    document.getElementById("btnMap").onclick =
        () => Router.load("map");

    // ----------------------------------------
    // Default page
    // ----------------------------------------

    Router.load("dashboard");

}

function connectLayerEvents() {

    document.getElementById("chkRoads")
        .onchange = e => LayerManager.toggleRoads(e.target.checked);

    document.getElementById("chkHospitals")
        .onchange = e => LayerManager.toggleHospitals(e.target.checked);

    document.getElementById("chkClinics")
        .onchange = e => LayerManager.toggleClinics(e.target.checked);

    document.getElementById("chkDoctors")
        .onchange = e => LayerManager.toggleDoctors(e.target.checked);

    document.getElementById("chkPharmacies")
        .onchange = e => LayerManager.togglePharmacies(e.target.checked);

    document.getElementById("chkCandidates")
        .onchange = e => LayerManager.toggleCandidates(e.target.checked);

}

start();