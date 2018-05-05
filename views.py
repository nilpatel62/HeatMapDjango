from django.shortcuts import render
from django.utils import timezone
import datetime
import time
import datetime
from datetime import timedelta
import pytz
from pytz import timezone
from rest_framework.views import APIView
from pandas import ExcelWriter
from django.http import JsonResponse
import pandas as pd
import numpy as np
import os
from pymongo import MongoClient
import json
from tzlocal import get_localzone
from bson import ObjectId

# Create your views here.

# Connection with MongoDB
client = MongoClient('mongodb://uberforallApiUser:jHzgur6jW2nxSefv@45.76.152.163/uberforallMongoDb')
db = client.uberforallMongoDb


def response_messages(response_status, response_data):
    # Function to create Response Message
    final_response_message = {
        "error": response_status,
        "result": response_data
    }
    return final_response_message


# get particular city Latitude and Longitude
class GetCitiesDataAPI(APIView):
    def post(self, request, cityname):
        try:
            # fetch particular city data from DataBase
            get_city = db.cities.find({'_id': ObjectId(cityname)})
            latlong = []
            for i in get_city:
                longtitude = []
                latitude = []
                for j in i['polygons']['coordinates']:
                    for k in j:
                        longtitude.append(k[0])
                        latitude.append(k[1])
                latlong.append(
                    {
                        'lat': sum(latitude) / len(latitude),
                        'lng': sum(longtitude) / len(longtitude)
                    }
                )
            return JsonResponse(latlong[0], safe=False, status=200)
        except:
            message = [
                {
                    "message": "Internal Server Error"
                }
            ]
            error_message = response_messages(2, message)
            return JsonResponse(error_message, safe=False, status=500)


class GetCitiesLatLongAPI(APIView):
    def post(self, request, cityname):
        try:
            # fetch particular city data from DataBase
            get_city = db.cities.find({'_id': ObjectId(cityname)})
            latlong = []
            for i in get_city:
                for j in i['polygons']['coordinates']:
                    for k in j:
                        latlong.append(
                            {
                                'lat': k[1], 'lng': k[0]
                            }
                        )
            return JsonResponse(latlong, safe=False, status=200)
        except:
            message = [
                {
                    "message": "Internal Server Error"
                }
            ]
            error_message = response_messages(2, message)
            return JsonResponse(error_message, safe=False, status=500)


class GetZoneLatLongAPI(APIView):
    def post(self, request, cityname):
        try:

        # fetch particular zone data from DataBase
            get_city = db.areaZones.find({'cityId': ObjectId(cityname)})
            title_zone_main = []

            for i in get_city:
                title_zone = []
                for j in i['polygons']['coordinates']:
                    for k in j:
                        title_zone.append(
                            {
                                'lat': k[1],
                                'lng': k[0]
                            }
                        )
                title_zone_main.append(title_zone)
            return JsonResponse(title_zone_main, safe=False, status=200)
        except:
            message = [
                {
                    "message": "Internal Server Error"
                }
            ]
            error_message = response_messages(2, message)
            return JsonResponse(error_message, safe=False, status=500)


class GetCitiesZoneAPI(APIView):
    def post(self, request, cityname):
        try:
            # fetch particular city data from DataBase
            get_city = db.areaZones.find({'cityId': ObjectId(cityname)})
            latlong = []
            for i in get_city:
                latlong.append(
                    {
                        'id': str(i['_id']),
                        'title': i['title']
                    }
                )
            return JsonResponse(latlong, safe=False, status=200)
        except:
            message = [
                {
                    "message": "Internal Server Error"
                }
            ]
            error_message = response_messages(2, message)
            return JsonResponse(error_message, safe=False, status=500)


class GetCitiesZoneLatAPI(APIView):
    def post(self, request, id):
        try:
            # fetch particular city data from DataBase
            get_city = db.areaZones.find({'_id': ObjectId(id)})
            latlong = []
            for i in get_city:
                longtitude = []
                latitude = []
                for j in i['polygons']['coordinates']:
                    for k in j:
                        longtitude.append(k[0])
                        latitude.append(k[1])
                    latlong.append(
                    {
                        'lat': sum(latitude) / len(latitude),
                        'lng': sum(longtitude) / len(longtitude)
                    }
                )
            return JsonResponse(latlong[0], safe=False, status=200)
        except:
            message = [
                {
                    "message": "Internal Server Error"
                }
            ]
            error_message = response_messages(2, message)
            return JsonResponse(error_message, safe=False, status=500)


# get data from database between dates
class GetDateAPI(APIView):
    '''
    0 for today
    1 for yesterday
    2 for past 7 days
    3 for past 30 days
    4 for past 1 year
    '''
    def post(self, request, date):
        try:
            print('date', date)
            if date == '0':
                # for Today

                current_date = datetime.datetime.now()
                print(current_date)
                current_mid_date = datetime.datetime.now()
                current_midnight_date = current_mid_date.replace(hour=0, minute=0, second=0, microsecond=0)
                print(current_midnight_date)
                current_local_timestamp = current_date.timestamp()
                current_midnight_timestamp = current_midnight_date.timestamp()
                print('current', current_local_timestamp)
                print('yesterday', current_midnight_timestamp)

                # call getdateinfo() function for get data from DataBase
                latlong = getdateinfo(current_local_timestamp, current_midnight_timestamp)
                return JsonResponse(latlong, safe=False, status=200)

            elif date == '1':

                yesterday_date = datetime.datetime.now() - datetime.timedelta(days=1)
                yesterday_midnight_date = yesterday_date.replace(hour=0, minute=0, second=0, microsecond=0)
                print(yesterday_midnight_date)
                yesterday_midnight_pm_date = yesterday_date.replace(hour=23, minute=59, second=59, microsecond=0)
                print(yesterday_midnight_pm_date)
                yesterday_midnight_timestamp = yesterday_midnight_date.timestamp()
                yesterday_local_timestamp = yesterday_midnight_pm_date.timestamp()
                print(yesterday_local_timestamp)
                print(yesterday_midnight_timestamp)
                latlong = getdateinfo(yesterday_midnight_timestamp, yesterday_local_timestamp)
                return JsonResponse(latlong, safe=False, status=200)

            elif date == '2':
                latlong = gettimestamp(7)
                return JsonResponse(latlong, safe=False, status=200)

            elif date == '3':
                latlong = gettimestamp(30)
                return JsonResponse(latlong, safe=False, status=200)

            elif date == '4':
                latlong = gettimestamp(365)
                return JsonResponse(latlong, safe=False, status=200)
            elif date == '5':
                start_date = request.POST.get('startdate')
                startdate = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M")
                end_date = request.POST.get('enddate')
                enddate = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M")
                current_date = startdate
                print(current_date)
                yesterday_date = enddate
                print(yesterday_date)
                yesterday_local_timestamp = yesterday_date.timestamp()
                current_local_timestamp = current_date.timestamp()
                print(yesterday_local_timestamp)
                print(current_local_timestamp)
                # call getdateinfo() function for get data from DataBase
                latlong = getdateinfo(current_local_timestamp, yesterday_local_timestamp)
                return JsonResponse(latlong, safe=False, status=200)
        except:
            message = [
                {
                    "message": "Internal Server Error"
                }
            ]
            error_message = response_messages(2, message)
            return error_message


def gettimestamp(days):
    try:
        current_date = datetime.datetime.now()
        print(current_date)
        yesterday_date = datetime.datetime.now() - datetime.timedelta(days=days)
        print(yesterday_date)
        current_local_timestamp = current_date.timestamp()
        yesterday_local_timestamp = yesterday_date.timestamp()

        # call getdateinfo() function for get data from DataBase
        latlong = getdateinfo(yesterday_local_timestamp, current_local_timestamp)
        return latlong
    except:
        message = [
            {
                "message": "Internal Server Error"
            }
        ]
        error_message = response_messages(2, message)
        return error_message


# find data from database between given date
def getdateinfo(current_local_timestamp, yesterday_local_timestamp):
    try:
        getbooking = db.bookingsPast.find(
            {
                'timeStamp.created':
                    {
                        '$gte': int(current_local_timestamp),
                        '$lt': int(yesterday_local_timestamp)
                    }
            }
        )
        pickup = []

        for i in getbooking:
            pickup.append(i)
        pick_up_len = len(pickup)
        # Store data into dataframe(pandas)
        if pick_up_len != 0:
            dataframe = pd.DataFrame(data=pickup)
            # get count of total Completed ride
            b_complete = dataframe['bookingStatusText'].str.contains('Completed').value_counts()[True]
            booking_complete = b_complete.tolist()
            # get count of total Requested Cancelled ride
            r_cancel = dataframe['bookingStatusText'].str.contains('Request Cancelled').value_counts()[True]
            request_cancle = r_cancel.tolist()

            # get count of total Booking Expired
            b_expired = dataframe['bookingStatusText'].str.contains('Booking Expired').value_counts()[True]
            booking_expired = b_expired.tolist()

            # get count of total Driver Cancelled Ride
            d_cancel = dataframe['bookingStatusText'].str.contains('Driver Cancelled').value_counts()[True]
            driver_cancel = d_cancel.tolist()

            # get count of total Customer Cancelled Ride
            c_cancel = dataframe['bookingStatusText'].str.contains('Customer Cancelled').value_counts()[True]
            customer_cancel = c_cancel.tolist()

            df_data = dataframe[['bookingStatusText', 'bookingId', 'bookingDate', 'pickup']]
            final_normalized_jsondata = df_data.to_dict('records')
            total_ride = len(final_normalized_jsondata)

            latlong = []
            for item in final_normalized_jsondata:
                latlong.append({
                    'bookingId': item['bookingId'],
                    'bookingStatusText': item['bookingStatusText'],
                    'bookingDate': item['bookingDate'],
                    'latitude': item['pickup']['location']['latitude'],
                    'longitude': item['pickup']['location']['longitude'],
                    'total_ride': total_ride,
                    'request_cancle': request_cancle,
                    'booking_expired': booking_expired,
                    'booking_complete': booking_complete,
                    'driver_cancel': driver_cancel,
                    'customer_cancel': customer_cancel
                }
                )
            # print(latlong)
            return latlong
    except:
        message = [
            {
                "message": "Internal Server Error"
            }
        ]
        error_message = response_messages(2, message)
        return error_message


# fetching today's data from database
def initialize(request):
    try:
        # get All Cities from database
        city_data = db.cities.find()
        cities = []
        id = []
        for city in city_data:
            cities.append(city['city'])
            id.append(str(city['_id']))
        city_name = []
        city_id = []
        for i in cities:
            city_name.append(i)
        for i in id:
            city_id.append(i)
        zzip = zip(city_name, city_id)
        return render(request, 'Heat/HeatMapUber.html', context={ 'city_name': zzip})
    except:
        message = [
            {
                "message": "Internal Server Error"
            }
        ]
        error_message = response_messages(2, message)
        return JsonResponse(error_message, safe=False, status=500)


