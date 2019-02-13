import pandas as pd
from bokeh.io import output_file
from bokeh.models import ColumnDataSource, HoverTool, LogColorMapper, GMapOptions
from bokeh.plotting import gmap
from bokeh.core import json_encoder
from shapely.geometry import Polygon, Point
from shapely.prepared import prep
import json


def normalizeCie10(shapeNumbers, shapeNames):
    casosTotales = {}
    f = open("casos_totales.csv")
    for line in f:
        casos, v = line.strip().split(",")
        casosTotales[casos] = float(v)
    f.close()
    for i in range(len(shapeNumbers)):
        if (casosTotales[shapeNames[i]] == 0):
            continue
        shapeNumbers[i] = float(shapeNumbers[i]) / casosTotales[shapeNames[i]] * 100

def calculateOcurrences(polygons, shapeNumbers, shapeNames, cie10=None):
    all_points = pd.read_csv("./neughboursMapping.csv")
    all_points.dropna(inplace=True)
    if cie10:
        all_points = all_points[all_points["cie10"] == cie10]
    locations = all_points["shapeName"].values.tolist()
    strCoordLocations =  list(filter(lambda x: "|" in x, locations))
    coordLocations = []
    for latlon in strCoordLocations:
        lon, lat = latlon.split("|")
        point = Point(float(lat), float(lon))
        coordLocations.append(point)
    mappedLocations = list(filter(lambda x: "|" not in x, locations))

    print set(mappedLocations).difference(set(shapeNames))
    print len(set(mappedLocations).difference(set(shapeNames)))

    for i, polygon in enumerate(polygons):
        shapeName = shapeNames[i].upper()
        poly = prep(polygon)
        shapeNumbers[i] += int(len(list(filter(poly.contains, coordLocations))))
        shapeNumbers[i] += int(len(list(filter(lambda x: x == shapeName, mappedLocations))))


def generateMap(cie10, gyeGeojson="/static/gye/GYEv1.geojson",
                institution="hlb", output="/static/maps/",
                custom_colors=('#ffffff', '#b5d6df', '#6caebf', '#0b7895', '#086077'),
                title="Mapa"):
    output = output + institution + "/" + cie10 +".html"
    with open(gyeGeojson) as f:
        shapes = json.load(f)

    shapesFeatures = shapes['features']
    shapesFeatures = list(filter(lambda x: x['properties']['name'].upper() != "TARQUI", shapesFeatures))

    shapeNames = [feat['properties']['name'].upper() for feat in shapesFeatures]
    district_x = [[x[0] for x in feat["geometry"]["coordinates"][0]] for feat in shapesFeatures]
    district_y = [[y[1] for y in feat["geometry"]["coordinates"][0]] for feat in shapesFeatures]
    district_xy = [[xy for xy in feat["geometry"]["coordinates"][0]] for feat in shapesFeatures]
    polygons = [Polygon(xy) for xy in district_xy]
    shapeNumbers = [0] * len(shapeNames)

    calculateOcurrences(polygons, shapeNumbers, shapeNames, cie10=cie10)
    normalizeCie10(shapeNumbers, shapeNames)

    sectores = {}

    for i in range (0, len(shapeNumbers)):
        sectores[shapeNames[i]] = shapeNumbers[i]
        print shapeNames[i], ",",shapeNumbers[i]

    # sorted_x = sorted(sectores.items(), key=operator.itemgetter(1))
    # for k in sorted_x:
    #     print k

    #
    # GRAFICACION
    #

    color_mapper = LogColorMapper(palette=custom_colors, low=5, high=max(shapeNumbers))
    source = ColumnDataSource(data=dict(
        x=district_x, y=district_y,
        name=shapeNames, rate=shapeNumbers,
    ))

    TOOLS = "pan,wheel_zoom,reset,hover,save"

    map_options = GMapOptions(lat=-2.1708, lng=-79.9121, map_type="roadmap", zoom=12, styles=json_encoder.serialize_json([
      {
        "elementType": "geometry",
        "stylers": [
          {
            "color": "#f5f5f5"
          }
        ]
      },
      {
        "elementType": "labels.icon",
        "stylers": [
          {
            "visibility": "off"
          }
        ]
      },
      {
        "elementType": "labels.text.fill",
        "stylers": [
          {
            "color": "#616161"
          }
        ]
      },
      {
        "elementType": "labels.text.stroke",
        "stylers": [
          {
            "color": "#f5f5f5"
          }
        ]
      },
      {
        "featureType": "administrative.land_parcel",
        "elementType": "labels.text.fill",
        "stylers": [
          {
            "color": "#bdbdbd"
          }
        ]
      },
      {
        "featureType": "poi",
        "elementType": "geometry",
        "stylers": [
          {
            "color": "#eeeeee"
          }
        ]
      },
      {
        "featureType": "poi",
        "elementType": "labels.text.fill",
        "stylers": [
          {
            "color": "#757575"
          }
        ]
      },
      {
        "featureType": "poi.park",
        "elementType": "geometry",
        "stylers": [
          {
            "color": "#e5e5e5"
          }
        ]
      },
      {
        "featureType": "poi.park",
        "elementType": "labels.text.fill",
        "stylers": [
          {
            "color": "#9e9e9e"
          }
        ]
      },
      {
        "featureType": "road",
        "elementType": "geometry",
        "stylers": [
          {
            "color": "#ffffff"
          }
        ]
      },
      {
        "featureType": "road.arterial",
        "elementType": "labels.text.fill",
        "stylers": [
          {
            "color": "#757575"
          }
        ]
      },
      {
        "featureType": "road.highway",
        "elementType": "geometry",
        "stylers": [
          {
            "color": "#dadada"
          }
        ]
      },
      {
        "featureType": "road.highway",
        "elementType": "labels.text.fill",
        "stylers": [
          {
            "color": "#616161"
          }
        ]
      },
      {
        "featureType": "road.local",
        "elementType": "labels.text.fill",
        "stylers": [
          {
            "color": "#9e9e9e"
          }
        ]
      },
      {
        "featureType": "transit.line",
        "elementType": "geometry",
        "stylers": [
          {
            "color": "#e5e5e5"
          }
        ]
      },
      {
        "featureType": "transit.station",
        "elementType": "geometry",
        "stylers": [
          {
            "color": "#eeeeee"
          }
        ]
      },
      {
        "featureType": "water",
        "elementType": "geometry",
        "stylers": [
          {
            "color": "#c9c9c9"
          }
        ]
      },
      {
        "featureType": "water",
        "elementType": "labels.text.fill",
        "stylers": [
          {
            "color": "#9e9e9e"
          }
        ]
      }
    ]))

    p = gmap("AIzaSyDf_e_UPiCdz7LDjHVKY2bb8ljh8u-ZkF4", map_options,
        title=title, tools=TOOLS,
        x_axis_location=None, y_axis_location=None, sizing_mode='stretch_both')

    p.grid.grid_line_color = None
    p.patches('x', 'y', source=source,
              fill_color={'field': 'rate', 'transform': color_mapper},
              fill_alpha=0.8, line_color="black", line_width=0.5)

    hover = p.select_one(HoverTool)
    hover.point_policy = "follow_mouse"
    hover.tooltips = [("Sector/Parroquia", "@name"),("Numero de Casos de Emergencia", "@rate")]

    output_file(output)
