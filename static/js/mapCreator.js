var geojson;
var map;
var info;

$(document).ready(function(){
    initMap(" Casos Absolutos");
});

function initMap(measure, institutionName){

    $.getJSON('/static/gye/data.geojson', function(gyeData) {
        console.log(gyeData);
        var mapboxAccessToken = 'pk.eyJ1IjoibGt1ZmZvIiwiYSI6ImNqdHdmZjFuazBqc3A0M3J6bXV5a3Vyd2wifQ.vj3X2kc1lmQuEyyWbtbCDg';
        map = L.map('map').setView([-2.1708, -79.9121], 12);

        info = L.control();

        info.onAdd = function (map) {
            this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
            this.update();
            return this._div;
        };

        info.update = function (props) {
            this._div.innerHTML = '<h4>MAPA EPIDEMIOLÓGICO</h4>' +  (props ?
                '<b>' + props.name + '</b><br />' + props.density + measure
                : 'Acerca el mouse al sector');
        };

        var legend = L.control({position: 'bottomright'});

        legend.onAdd = function (map) {

            var div = L.DomUtil.create('div', 'info legend'),
                grades = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                labels = [];

            // loop through our density intervals and generate a label with a colored square for each interval
            for (var i = 0; i < grades.length; i++) {
                div.innerHTML +=
                    '<i style="background:' + getColor(grades[i] + 1) + '"></i> ' +
                    grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
            }

            return div;
        };

        L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=' + mapboxAccessToken, {
            id: 'mapbox.light'
        }).addTo(map);

        geojson = L.geoJson(gyeData, {
            style: style,
            onEachFeature: onEachFeature
        }).addTo(map);

        info.addTo(map);

        legend.addTo(map);

    });
}

function getColor(d) {
    return d > 95 ? '#800026' :
           d > 90  ? '#BD0026' :
           d > 80  ? '#E31A1C' :
           d > 60  ? '#FC4E2A' :
           d > 40   ? '#FD8D3C' :
           d > 20   ? '#FEB24C' :
           d > 10   ? '#FED976' :
                      '#FFEDA0';
}

function style(feature) {
    return {
        fillColor: getColor(feature.properties.density),
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7
    };
}

function highlightFeature(e) {
    var layer = e.target;

    layer.setStyle({
        weight: 5,
        color: '#666',
        dashArray: '',
        fillOpacity: 0.7
    });

    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
    }

    info.update(layer.feature.properties);
}

function resetHighlight(e) {
    geojson.resetStyle(e.target);
    info.update();
}

function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
}

function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        click: zoomToFeature
    });
}