import pandas as pd
from shapely.geometry import Polygon, Point
from shapely.prepared import prep
import json

class MapGenerator():

    def __init__(
        self,
        institution="hlb",
        capitulo=None,
        agrupacion=None,
        cie10="all",
        startDate=None,
        endDate=None,
        file_location="/static/gye/GYEv1.geojson",
        file_output="/static/gye/data.geojson"
    ):
        self.institution = institution
        self.capitulo = capitulo
        self.agrupacion = agrupacion
        self.cie10 = cie10
        self.start = startDate
        self.end = endDate
        self.file = file_location
        self.output = file_output

    def normalizeCie10(self, shapeNumbers, shapeNames):
        casosTotales = {}
        f = open("casos_totales.csv")
        for line in f:
            casos, v = line.strip().split(",")
            casosTotales[casos] = float(v)
        f.close()
        for i in range(len(shapeNumbers)):
            if (casosTotales[shapeNames[i]] == 0):
                continue
            value = float(shapeNumbers[i]) / casosTotales[shapeNames[i]] * 100
            value = float("{0:.2f}".format(value))
            shapeNumbers[i] = value

    def calculateOcurrences(self, polygons, shapeNumbers, shapeNames, cie10=None):
        all_points = pd.read_csv("./neighboursMapping.csv")
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


    def generateMap(self):
        with open(self.file) as f:
            shapes = json.load(f)

        shapesFeatures = shapes['features']

        shapeNames = [feat['properties']['name'].upper() for feat in shapesFeatures]
        district_x = [[x[0] for x in feat["geometry"]["coordinates"][0]] for feat in shapesFeatures]
        district_y = [[y[1] for y in feat["geometry"]["coordinates"][0]] for feat in shapesFeatures]
        district_xy = [[xy for xy in feat["geometry"]["coordinates"][0]] for feat in shapesFeatures]
        polygons = [Polygon(xy) for xy in district_xy]
        shapeNumbers = [0] * len(shapeNames)

        self.calculateOcurrences(polygons, shapeNumbers, shapeNames, cie10=self.cie10)
        self.normalizeCie10(shapeNumbers, shapeNames)

        sectores = {}



        for i in range (0, len(shapeNumbers)):
            sectores[shapeNames[i]] = shapeNumbers[i]
            print shapeNames[i], ",",shapeNumbers[i]

        for feature in shapes.features:
            index = shapeNames.index(feature["properties"]["name"])
            feature["properties"]["density"] = shapeNumbers[index]

        with open(self.output, 'w') as outfile:
            json.dump(shapes, outfile)

        return 200
        # sorted_x = sorted(sectores.items(), key=operator.itemgetter(1))
        # for k in sorted_x:
        #     print k

        #
        # ACTUALIZACION
        #

