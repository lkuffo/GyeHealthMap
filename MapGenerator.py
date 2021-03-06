import pandas as pd
from shapely.geometry import Polygon, Point
from shapely.prepared import prep
from flask import current_app
from datetime import datetime
import json
import os
import re

class MapGenerator():

    def __init__(
        self,
        app,
        institution="hlb",
        capitulo=None,
        agrupacion=None,
        cie10="all",
        startDate=None,
        endDate=None,
        edad=None,
        file_location="static/gye/GYEv1.geojson",
        file_output="static/gye/data.geojson"
    ):
        self.app = app
        self.institution = institution
        self.capitulo = capitulo
        self.agrupacion = agrupacion
        self.cie10 = cie10
        self.start = startDate
        self.end = endDate
        self.edad = edad
        self.file = file_location
        self.output = file_output

    def normalizeCie10(self, shapeNumbers, shapeNames, shapeNormalized):
        for i in range(len(shapeNormalized)):
            shapeNormalized[i] = 0
        casosTotales = {}
        f = current_app.open_resource("casos_totales.csv")
        #f = open("casos_totales.csv")
        for line in f:
            casos, v = line.strip().split(",")
            casosTotales[casos] = float(v)
        f.close()
        for i in range(len(shapeNumbers)):
            if (casosTotales[shapeNames[i]] == 0):
                continue
            value = float(shapeNumbers[i]) / casosTotales[shapeNames[i]] * 100
            value = float("{0:.2f}".format(value))
            shapeNormalized[i] = value

    def findCapitulo(self, cie10, letraStart, letraEnd, start, end):
        cie10Letra, cie10Numero = cie10[0], int(cie10[1:3]) #truncate CIE10
        if (cie10Letra.upper() >= letraStart.upper() and cie10Letra.upper() <= letraEnd.upper()) \
            and (cie10Numero >= start and cie10Numero <= end):
            return True
        return False

    def findAgrupacion(self, cie10, letra, start, end):
        cie10Letra, cie10Numero = cie10[0], int(cie10[1:3]) #truncate CIE10
        if letra.upper() == cie10Letra.upper() and (cie10Numero >= start and cie10Numero <= end):
            return True
        return False

    def calculateOcurrences(self, polygons, shapeNumbers, shapeNames, cie10=None, capitulo=None, agrupacion=None, edad=None):
        all_points = pd.read_csv(current_app.open_resource("neighboursMapping.csv"))
        #all_points = pd.read_csv("neighboursMapping.csv")
        all_points.dropna(inplace=True)
        all_points["edad"] = pd.to_numeric(all_points["edad"])
        if cie10:
            all_points = all_points[all_points["cie10"] == cie10]

        if agrupacion:
            start, end = agrupacion.upper().split("-")
            letra, numStart = start[0], int(start[1:])
            numEnd = int(end[1:])
            all_points = all_points[all_points.apply(lambda x: self.findAgrupacion(x["cie10"], letra, numStart, numEnd), axis=1)]

        if capitulo:
            start, end = capitulo.upper().split("-")
            letraStart, numStart = start[0], int(start[1:])
            letraEnd, numEnd = end[0], int(end[1:])
            all_points = all_points[all_points.apply(lambda x: self.findCapitulo(x["cie10"], letraStart, letraEnd, numStart, numEnd), axis=1)]

        if edad and edad != "":
            print edad
            edadStart, edadEnd = edad.split("-")
            edadStart = re.sub('[^0-9]','', edadStart)
            edadEnd = re.sub('[^0-9]','', edadEnd)
            all_points = all_points[(all_points["edad"] >= int(edadStart)) & (all_points["edad"] <= int(edadEnd))]

        all_points['fecha'] = all_points['fecha'].apply(lambda x: datetime.strptime(x[0:8], '%m/%d/%y'))
        print self.start
        print self.end
        if self.start and self.start != "":
            all_points = all_points[all_points['fecha'] >= self.start]
        if self.end and self.end != "":
            all_points = all_points[all_points['fecha'] <= self.end]
        locations = all_points["shapeName"].values.tolist()

        # anonimized_values = {}
        # all_cie10 = all_points["cie10"].values.tolist()
        # for z, location in enumerate(locations):
        #     key = "NOT_FOUND"
        #     if "|" in location:
        #         lon, lat = location.split("|")
        #         point = Point(float(lat), float(lon))
        #         for i, polygon in enumerate(polygons):
        #             poly = prep(polygon)
        #             shapeName = shapeNames[i].upper()
        #             if poly.contains(point):
        #                 key = shapeName + "|" + all_cie10[z]
        #                 break
        #     else:
        #         key = location.upper() + "|" + all_cie10[z]
        #     if key not in anonimized_values:
        #         anonimized_values[key] = 0
        #     anonimized_values[key] += 1
        # for k, v in anonimized_values.items():
        #     print k, "|", v
        # exit()

        strCoordLocations =  list(filter(lambda x: "|" in x, locations))
        coordLocations = []
        for latlon in strCoordLocations:
            lon, lat = latlon.split("|")
            point = Point(float(lat), float(lon))
            coordLocations.append(point)
        mappedLocations = list(filter(lambda x: "|" not in x, locations))
        # print set(mappedLocations).difference(set(shapeNames))
        # print len(set(mappedLocations).difference(set(shapeNames)))
        print "Starting dict"
        tmpDict = {}
        for elem in mappedLocations:
            if elem not in tmpDict:
                tmpDict[elem] = 0
            tmpDict[elem] += 1
        print "Finishing dict"
        print "Starting Polygons"
        for elem in coordLocations:
            for i, polygon in enumerate(polygons):
                poly = prep(polygon)
                shapeName = shapeNames[i].upper()
                if poly.contains(elem):
                    if shapeName not in tmpDict:
                        tmpDict[shapeName] = 0
                    tmpDict[shapeName] += 1
                    break
        print "Finishing Polygons"
        for i, polygon in enumerate(polygons):
            shapeName = shapeNames[i].upper()
            try:
                shapeNumbers[i] += tmpDict[shapeName]
            except:
                None
        print sum(tmpDict.values())

    def generateMap(self):
        #with open(self.file) as f:
        with current_app.open_resource(self.file) as f:
            shapes = json.load(f)
        usedFilter = None
        shapesFeatures = shapes['features']

        shapeNames = [feat['properties']['name'].upper() for feat in shapesFeatures]
        district_x = [[x[0] for x in feat["geometry"]["coordinates"][0]] for feat in shapesFeatures]
        district_y = [[y[1] for y in feat["geometry"]["coordinates"][0]] for feat in shapesFeatures]
        district_xy = [[xy for xy in feat["geometry"]["coordinates"][0]] for feat in shapesFeatures]
        polygons = [Polygon(xy) for xy in district_xy]
        shapeNumbers = [0] * len(shapeNames)
        shapeNormalized = [100] * len(shapeNames)
        if self.capitulo != None:
            self.calculateOcurrences(polygons, shapeNumbers, shapeNames, capitulo=self.capitulo, edad=self.edad)
            self.normalizeCie10(shapeNumbers, shapeNames,shapeNormalized)
            usedFilter = "capitulo"
        elif self.agrupacion != None:
            self.calculateOcurrences(polygons, shapeNumbers, shapeNames, agrupacion=self.agrupacion, edad=self.edad)
            self.normalizeCie10(shapeNumbers, shapeNames,shapeNormalized)
            usedFilter = "agrupacion"
        else:
            if self.cie10 == "all" or self.cie10 == None:
                self.calculateOcurrences(polygons, shapeNumbers, shapeNames, edad=self.edad)
                usedFilter = "Pacientes Totales"
            else:
                self.calculateOcurrences(polygons, shapeNumbers, shapeNames, cie10=self.cie10, edad=self.edad)
                self.normalizeCie10(shapeNumbers, shapeNames,shapeNormalized)
                usedFilter = "cie10"

        sectores = {}

        for i in range (0, len(shapeNumbers)):
            sectores[shapeNames[i]] = shapeNumbers[i]
            # print shapeNames[i], ",",shapeNumbers[i]

        for feature in shapes["features"]:
            index = shapeNames.index(feature["properties"]["name"].upper())
            feature["properties"]["density"] = shapeNumbers[index]
            feature["properties"]["normalized"] = shapeNormalized[index]

        # with current_app.open_resource(self.output, 'w') as outfile:
        # with open(os.path.join(self.app.root_path, self.output), 'w') as outfile:
        #     json.dump(shapes, outfile)
        print "FINISHED!"
        return shapes, usedFilter
        # sorted_x = sorted(sectores.items(), key=operator.itemgetter(1))
        # for k in sorted_x:
        #     print k

        #
        # ACTUALIZACION
        #

# testMapGenerator = MapGenerator("app")
# testMapGenerator.generateMap()