var geojson;
var map;
var info;
var grades;
var graphType;

// $(document).ready(function(){
//     // initMap(" pacientes Absolutos");
// });

function initMap(measure, institutionName, gyeData, type){
    graphType = type;
    console.log(gyeData);
    var mapboxAccessToken = 'pk.eyJ1IjoibGt1ZmZvIiwiYSI6ImNqdHdmZjFuazBqc3A0M3J6bXV5a3Vyd2wifQ.vj3X2kc1lmQuEyyWbtbCDg';
    map = L.map('map', { zoomControl: false }).setView([-2.1708, -79.9121], 12);

    var measures = [];
    for (var i = 0; i < gyeData.features.length; i++){
        if (type === "absolute"){
            loop_measure = gyeData.features[i].properties.density;
        } else {
            loop_measure = gyeData.features[i].properties.normalized;
        }
        measures.push(loop_measure)
    }

    measures.sort(function(a,b){
        return a-b
    });

    grades = distributedCopy(measures, 10);

    console.log(grades);

    info = L.control();

    info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
        this.update();
        return this._div;
    };

    info.update = function (props) {
        this._div.innerHTML = '<h4>' + institutionName + '</h4>' +  (props ?
            '<b>' + props.name + '</b><br />' + props.density + " pacientes" + '<br/>' +
            props.normalized + "% de pacientes (relativo a todos los pacientes del sector)"
            : 'Acerca el mouse al sector para ver más información');
    };

    var legend = L.control({position: 'bottomright'});

    legend.onAdd = function (map) {

        var div = L.DomUtil.create('div', 'info legend'),
            labels = [];

        // loop through our density intervals and generate a label with a colored square for each interval
        for (var i = 1; i < grades.length-1; i++) {
            div.innerHTML +=
                '<i style="background:' + getColor(grades[i] + 1) + '"></i> ' +
                grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '<br>');
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

    new L.Control.Zoom({ position: 'bottomleft' }).addTo(map);

}

function getColor(d) {
    colors = [
        '#a8a8a8',
        '#fff6ce',
        '#FFEDA0',
        '#FED976',
        '#FEB24C',
        '#FD8D3C',
        '#fd6e25',
        '#FC4E2A',
        '#E31A1C',
        '#800026'
    ];
    for (i = 0; i < grades.length; i++) {
      if (d <= grades[i]){
        return colors[i]
      }
    }
}

function style(feature) {
    return {
        fillColor: graphType === "absolute" ? getColor(feature.properties.density): getColor(feature.properties.normalized),
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

/**
 * Retrieve a fixed number of elements from an array, evenly distributed but
 * always including the first and last elements.
 *
 * @param   {Array} items - The array to operate on
 * @param   {Number} n - The number of elements to extract
 * @returns {Array}
 */
function distributedCopy(items, n) {
    var elements = [items[0]];
    var totalItems = items.length - 2;
    var interval = Math.floor(totalItems/(n - 2));
    for (var i = 1; i < n - 1; i++) {
        elements.push(items[i * interval]);
    }
    elements.push(items[items.length - 1]);
    return elements;
}