from builtins import print
from django.shortcuts import render
import dash
from rest_framework.views import APIView
from django.http import JsonResponse
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly import graph_objs as go
from plotly.graph_objs import *
from flask import Flask
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
from pymongo import MongoClient
import json
# Create your views here.
client = MongoClient('mongodb://uberforallApiUser:jHzgur6jW2nxSefv@45.76.152.163/uberforallMongoDb')
db = client.uberforallMongoDb

app = dash.Dash('UberApp')
server = app.server

mapbox_access_token = 'pk.eyJ1IjoiYWxpc2hvYmVpcmkiLCJhIjoiY2ozYnM3YTUxMDAxeDMzcGNjbmZyMmplZiJ9.ZjmQ0C2MNs1AzEBC_Syadg'


class GetCitiesDataAPI(APIView):
    def post(self, request, cityname):
        print(cityname)
        getcity1 = db.cities.find({'city': cityname})
        citylat = []
        for cordinate in getcity1:
            citylat.append(cordinate['polygons'])
        coordinates = []
        for coordinate in citylat:
            coordinates.append(coordinate['coordinates'])
        latitude = []
        longtotude = []
        for i in coordinates:
            for j in i:
                for k in j:
                    longtotude.append(
                        {
                            "lng": k[0],
                            "lat": k[1]
                        }
                    )
        print(longtotude[0])
        return JsonResponse(longtotude[0], safe=False, status=200)


class GetCitiesZoneAPI(APIView):
    def post(self, request, cityname):
        getzone = db.areaZones.find({'city': cityname})
        print(cityname)
        title_zone = []

        for i in getzone:
            longtitude = []
            latitude = []
            for j in i['polygons']['coordinates']:
                for k in j:
                    longtitude.append(k[0])
                    latitude.append(k[1])
            title_zone.append({
                    'title': i['title'],
                    'lat': sum(latitude) / len(latitude),
                    'lng': sum(longtitude) / len(longtitude)
                })
        print(title_zone)
        return JsonResponse(title_zone, safe=False, status=200)

        # zone = []
        # for i in title_zone:
        #     zone.append(
        #         dict(
        #             args=[{
        #                 'mapbox.zoom': 13,
        #                 'mapbox.center.lon': i['long'],
        #                 'mapbox.center.lat': i['lat'],
        #                 'mapbox.bearing': 0,
        #                 'mapbox.style': 'dark'
        #             }],
        #             label=i['title'],
        #             method='relayout'
        #         )
        #     )
        # return zone


def initialize(request):
    value = request.POST.get('city')
    getcity = db.cities.find()
    cities = []
    for city in getcity:
        cities.append(city['city'])
    city_data = []
    for i in cities:
        city_data.append(i)

    uberalldata = db.bookingsPast.find()
    uberdata = []
    date = []
    for data in uberalldata:
        uberdata.append(data)
    pickup = []

    for i in uberdata:
        pickup.append(i['pickup'])
        date.append(i['dateAndTime'])

    created_date = []
    for n in date:
        created_date.append(str(n['created']))

    location = []
    for j in pickup:
        location.append(j['location'])

    longitude = []
    for k in location:
        longitude.append(k['longitude'])

    latitude = []
    for l in location:
        latitude.append(l['latitude'])

    getzone = db.areaZones.find({'city': 'Bengaluru'})
    title_zone = []

    for i in getzone:
        longtitude = []
        latitude = []
        for j in i['polygons']['coordinates']:
            for k in j:
                longtitude.append(k[0])
                latitude.append(k[1])
        title_zone.append(i['title'])

    return render(request, 'Heat/HeatMapUber.html', context={'latitude': latitude, 'longitude': longitude
        ,'city': city_data, 'title_zone': title_zone})
