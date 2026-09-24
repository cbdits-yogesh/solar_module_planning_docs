/**
 * DocType: Site Survey
 * Apply To: Form
 */

frappe.ui.form.on('Site Survey', {
    refresh(frm) {

        frm.add_custom_button('📍 Capture Location', function () {

            if (!navigator.geolocation) {
                frappe.msgprint('❌ Geolocation is not supported by this browser.');
                return;
            }

            frappe.show_alert({ message: '⏳ Fetching GPS location...', indicator: 'blue' });

            navigator.geolocation.getCurrentPosition(
                function (position) {
                    let lat  = parseFloat(position.coords.latitude.toFixed(8));
                    let lng  = parseFloat(position.coords.longitude.toFixed(8));
                    let accuracy = position.coords.accuracy;
                    let captured_time = frappe.datetime.now_datetime();

                    frm.set_value('latitude', lat);
                    frm.set_value('longitude', lng);

                    // frm.set_value('location_map', JSON.stringify({
                    //     "type": "FeatureCollection",
                    //     "features": [{
                    //         "type": "Feature",
                    //         "geometry": {
                    //             "type": "Point",
                    //             "coordinates": [lng, lat]
                    //         },
                    //         "properties": {}
                    //     }]
                    // }));

                    // ✅ FIXED: Full address with all components — zoom=18 for max detail
                    fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json&zoom=18&addressdetails=1`, {
                        headers: {
                            'Accept-Language': 'en',
                            'User-Agent': 'ERPNext-SiteSurvey/1.0'
                        }
                    })
                    .then(r => r.json())
                    .then(data => {
                        let a = data.address;

                        // ✅ All fields listed separately — no OR chaining
                        let parts = [
                            a.house_number,
                            a.house,
                            a.building,
                            a.road,
                            a.neighbourhood,
                            a.hamlet,
                            a.suburb,
                            a.village,
                            a.town,
                            a.city_district,
                            a.county,
                            a.city,
                            a.state_district,
                            a.district,
                            a.state,
                            a.postcode,
                            a.country
                        ].filter(Boolean);

                        // Remove consecutive duplicates e.g. "Thane, Thane"
                        let deduped = parts.filter((val, i, arr) => i === 0 || val !== arr[i - 1]);

                        // Use display_name if structured result is too short
                        let structured = deduped.join(', ');
                        frm.set_value('location_details', structured.length > 10 ? structured : data.display_name);
                        frm.refresh_field('location_details');
                    })
                    .catch(() => {
                        frm.set_value('location_details', `Lat: ${lat}, Long: ${lng}`);
                    });

                    // ✅ Satellite Map with Street Labels
                    let map_html = `
                    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
                    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"><\/script>

                    <div style="font-family:sans-serif; border-radius:8px; overflow:hidden; border:1px solid #ddd;">

                        <div style="background:#1a1a2e; color:white; padding:10px 16px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:4px;">
                            <div style="font-size:13px; font-weight:500;">
                                📍 <b>Lat:</b> ${lat}&deg; &nbsp;
                                <b>Long:</b> ${lng}&deg; &nbsp;
                                <b>Accuracy:</b> ±${accuracy.toFixed(0)}m
                            </div>
                            <div style="font-size:12px; color:#adb5bd;">🕐 ${captured_time}</div>
                        </div>

                        <div id="site-survey-map" style="height:400px; width:100%;"></div>

                        <div style="display:flex; gap:8px; padding:10px; background:#f8f9fa; flex-wrap:wrap;">
                            <a href="https://maps.google.com/?q=${lat},${lng}&t=k" target="_blank"
                               style="font-size:12px; background:#4285F4; color:white; padding:6px 14px; border-radius:4px; text-decoration:none; font-weight:500;">
                               🛰️ Google Satellite
                            </a>
                            <a href="https://maps.google.com/?q=${lat},${lng}&t=h" target="_blank"
                               style="font-size:12px; background:#34A853; color:white; padding:6px 14px; border-radius:4px; text-decoration:none; font-weight:500;">
                               🏠 Google Hybrid
                            </a>
                            <a href="https://www.openstreetmap.org/?mlat=${lat}&mlon=${lng}#map=19/${lat}/${lng}" target="_blank"
                               style="font-size:12px; background:#7EBC6F; color:white; padding:6px 14px; border-radius:4px; text-decoration:none; font-weight:500;">
                               🗺️ OpenStreetMap
                            </a>
                            <a href="https://earth.google.com/web/@${lat},${lng},100a,200d,35y,0h,0t,0r" target="_blank"
                               style="font-size:12px; background:#FF6B35; color:white; padding:6px 14px; border-radius:4px; text-decoration:none; font-weight:500;">
                               🌍 Google Earth
                            </a>
                        </div>
                    </div>

                    <script>
                        setTimeout(function () {
                            if (window._siteSurveyMap) {
                                window._siteSurveyMap.remove();
                                window._siteSurveyMap = null;
                            }

                            var mapEl = document.getElementById('site-survey-map');
                            if (!mapEl || mapEl._leaflet_id) return;

                            var map = L.map('site-survey-map', {
                                center: [${lat}, ${lng}],
                                zoom: 20,
                                zoomControl: true,
                                scrollWheelZoom: true
                            });

                            var satellite = L.tileLayer(
                                'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                                {
                                    attribution: '© Esri, Maxar, Airbus',
                                    maxZoom: 21,
                                    maxNativeZoom: 19
                                }
                            );

                            var labels = L.tileLayer(
                                'https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png',
                                {
                                    attribution: '© CartoDB',
                                    opacity: 1,
                                    maxZoom: 21,
                                    pane: 'overlayPane'
                                }
                            );

                            var street = L.tileLayer(
                                'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                                {
                                    attribution: '© OpenStreetMap contributors',
                                    maxZoom: 19
                                }
                            );

                            satellite.addTo(map);
                            labels.addTo(map);

                            L.control.layers(
                                {
                                    '🛰️ Satellite': satellite,
                                    '🗺️ Street Map': street
                                },
                                {
                                    '🏷️ Labels': labels
                                },
                                { position: 'topright', collapsed: false }
                            ).addTo(map);

                            var redIcon = L.divIcon({
                                className: '',
                                html: '<div style="width:20px;height:20px;background:#e74c3c;border:3px solid white;border-radius:50%;box-shadow:0 0 0 5px rgba(231,76,60,0.35),0 2px 8px rgba(0,0,0,0.4);"></div>',
                                iconSize: [20, 20],
                                iconAnchor: [10, 10],
                                popupAnchor: [0, -12]
                            });

                            L.marker([${lat}, ${lng}], { icon: redIcon })
                             .addTo(map)
                             .bindPopup(
                                '<div style="font-size:13px;line-height:1.8;min-width:180px;">' +
                                '<b style="font-size:14px;">📍 Site Location</b><br>' +
                                '<b>Lat:</b> ${lat}<br>' +
                                '<b>Long:</b> ${lng}<br>' +
                                '<b>Accuracy:</b> ±${accuracy.toFixed(0)}m<br>' +
                                '<b>Time:</b> ${captured_time}' +
                                '</div>',
                                { maxWidth: 250 }
                             )
                             .openPopup();

                            L.circle([${lat}, ${lng}], {
                                radius: ${accuracy},
                                color: '#e74c3c',
                                fillColor: '#e74c3c',
                                fillOpacity: 0.1,
                                weight: 1.5,
                                dashArray: '5,5'
                            }).addTo(map);

                            window._siteSurveyMap = map;

                        }, 500);
                    <\/script>`;

                    frm.set_df_property('map_preview', 'options', map_html);
                    frm.refresh_field('map_preview');

                    frappe.show_alert({ message: '✅ Location captured successfully!', indicator: 'green' });
                },

                function (err) {
                    let errors = {
                        1: 'Permission denied. Please allow location access in your browser settings.',
                        2: 'Position unavailable. Move to open area and retry.',
                        3: 'Request timed out. GPS signal weak — try again outdoors.'
                    };
                    frappe.msgprint({
                        title: 'Location Error',
                        message: '⚠️ ' + (errors[err.code] || err.message),
                        indicator: 'red'
                    });
                },

                {
                    enableHighAccuracy: true,
                    timeout: 20000,
                    maximumAge: 0
                }
            );

        });
    }
});
