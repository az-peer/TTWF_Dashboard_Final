// Delay the execution of the map setup to ensure the DOM and Leaflet are fully loaded
setTimeout(function () {
    // Get the HTML container element with ID 'pakistan-map'
    const container = document.getElementById("pakistan-map");

    // Proceed only if the container exists and Leaflet (L) is defined
    if (container && typeof L !== "undefined") {
        // Define the initial center coordinates of the map (latitude, longitude)
        const initialCenter = [30.3753, 69.3451];

        // Set the initial zoom level of the map
        const initialZoom = 5.5;

        // Initialize the Leaflet map inside the 'pakistan-map' container
        const map = L.map("pakistan-map").setView(initialCenter, initialZoom);

        // Add a tile layer using OpenStreetMap tiles with attribution
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "© OpenStreetMap contributors", // Attribution for legal use
            maxZoom: 18 // Maximum zoom level
        }).addTo(map); // Add this tile layer to the map

        // Define a custom Leaflet control to serve as a "Home" button
        const homeControl = L.Control.extend({
            options: { position: "topright" }, // Position of the control on the map

            // Called when the control is added to the map
            onAdd: function () {
                // Create a div container for the button with custom styling
                const container = L.DomUtil.create("div", "leaflet-bar leaflet-control leaflet-control-custom");
                
                // Set the button content to a home emoji
                container.innerHTML = "🏠";

                // Style the home button visually
                container.style.backgroundColor = "white";
                container.style.width = "34px";
                container.style.height = "34px";
                container.style.display = "flex";
                container.style.justifyContent = "center";
                container.style.alignItems = "center";
                container.style.cursor = "pointer";
                container.style.fontSize = "20px";

                // Define what happens when the home button is clicked
                container.onclick = function () {
                    // Reset the map view to the initial center and zoom
                    map.setView(initialCenter, initialZoom);
                };

                // Return the DOM element so Leaflet can add it to the map
                return container;
            }
        });

        // Add the custom home button control to the map
        map.addControl(new homeControl());

        // Fetch the district coordinates JSON file from the specified path
        fetch("/assets/district_coords.json")
            .then(response => response.json()) // Parse the response as JSON
            .then(districts => {
                // Iterate through each district entry
                districts.forEach(d => {
                    // Parse latitude and longitude from the district object
                    const lat = parseFloat(d.lat);
                    const lng = parseFloat(d.long);
                    const name = d.name; // Get the name of the district

                    // Create a circular marker at the district location
                    L.circleMarker([lat, lng], {
                        radius: 10, // Radius of the circle marker
                        color: "blue", // Stroke color
                        fillColor: "blue", // Fill color
                        fillOpacity: 0.6, // Fill transparency
                        weight: 1 // Border thickness
                    })
                        .addTo(map) // Add the circle marker to the map
                        .bindPopup(`<strong>${name}</strong>`); // Bind a popup showing the district name
                });
            })
            .catch(error => {
                // Log an error if the JSON file fails to load
                console.error("Failed to load district coordinates:", error);
            });

    } else {
        // Log an error if Leaflet or the container are not available
        console.error("Leaflet or container not ready");
    }
}, 1000); // Delay in milliseconds to ensure page and libraries are fully loaded