from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from pymongo import MongoClient
from datetime import datetime
import datetime
from bson.objectid import ObjectId
import pandas as pd
from pytz import timezone
from django.shortcuts import render
import requests
from django.views.decorators.clickjacking import xframe_options_exempt


'''
    Connection with MongoDB
'''
client = MongoClient('mongodb://uberforallApiUser:jHzgur6jW2nxSefv@45.76.152.163/uberforallMongoDb')
db = client.uberforallMongoDb

# URL = "https://heatmap.go-tasker.com/"
URL = "http://127.0.0.1:8000/"


def response_messages(response_status, response_data):
    # Function to create Response Message
    final_response_message = {
        "error": response_status,
        "result": response_data
    }
    return final_response_message


class GetDate(APIView):
    def post(self, request):
        try:
            data = request.data
            print(data)
            time = data['hour']
            days = data['date']
            city = data['cityId']
            status = data['status']
            startdate = data['startdate']
            enddate = data['enddate']
            time_zone = data['timezone']
            zoneId = data['zoneId']
            latlong = getdata(time, days, city, status, time_zone, startdate, enddate, zoneId) # call this function for getting Data between given Datas
            return JsonResponse(latlong, safe=False, status=200)
        except:
            error_message = {
                "error": "Bad request"
            }
            return JsonResponse(error_message, status=500)


def daterange(days, time, time_zone, startdate, enddate):
    if int(days) == 0:
        '''
            for days is 0 and hour is 24(send all hours data)
        '''
        eastern = timezone(time_zone)
        currlocal = eastern.localize(datetime.datetime.now())
        currentdate = (currlocal.replace(hour=0, minute=0, second=0, microsecond=0)).timestamp()
        lastdate = (currlocal.replace(hour=23, minute=59, second=59, microsecond=59)).timestamp()
        return currentdate, lastdate

    if int(days) == 1:
        '''
            for days is 1 and hour is 24(send all hours data)
        '''
        currlocal = datetime.datetime.now() - datetime.timedelta(days=1)
        currentdate = (currlocal.replace(hour=0, minute=0, second=0, microsecond=0)).timestamp()
        lastdate = (currlocal.replace(hour=23, minute=59, second=59, microsecond=59)).timestamp()
        return int(currentdate), int(lastdate)

    if int(days) == 2:
        '''
            for days is 2 (1 Week)
        '''
        currlocal = datetime.datetime.now() - datetime.timedelta(days=7)
        lastdate = (datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).timestamp()
        currentdate = (currlocal.replace(hour=23, minute=59, second=59, microsecond=59)).timestamp()
        return int(currentdate), int(lastdate)

    if int(days) == 3:
        '''
            for days is 3 (1 month)
        '''
        currlocal = datetime.datetime.now() - datetime.timedelta(days=30)
        lastdate = (datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).timestamp()
        currentdate = (currlocal.replace(hour=23, minute=59, second=59, microsecond=59)).timestamp()
        return int(currentdate), int(lastdate)

    if int(days) == 4:
        '''
            for days is 4 (last 1 Year)
        '''
        currlocal = datetime.datetime.now() - datetime.timedelta(days=365)
        lastdate = (datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).timestamp()
        currentdate = (currlocal.replace(hour=23, minute=59, second=59, microsecond=59)).timestamp()
        return int(currentdate), int(lastdate)

    if int(days) == 5:
        '''
            for days is 5 (Custom Dates)
        '''
        print(type(startdate))
        eastern = timezone(time_zone)
        currlocal = eastern.localize(datetime.datetime.strptime(startdate, "%Y-%m-%d %H:%M"))
        currlast = eastern.localize(datetime.datetime.strptime(enddate, "%Y-%m-%d %H:%M"))
        currentdate = currlocal.timestamp()
        lastdate = currlast.timestamp()
        return int(currentdate), int(lastdate)


def getdata(time, days, city, status, time_zone, start_date, end_date, zoneId):
    booking = []
    latlong = None
    bookingInfo = []
    '''
        for 0 for today, 1 for yesterday, 2 for 1 week, 3 for month, 4 for week and 5 for custom date
        status 0 for send all data for every Status
        time 24 is for all hours
        bookingstatus:
                        0-bookings
                        1-unassignedBookings
                        2-assignedBookings
    '''
    currentdate, lastdate = daterange(days, time, time_zone, start_date, end_date)
    '''
        find data from database status wise or without status
    '''
    if int(status) == 0 and (zoneId is None or zoneId == 0):
        print('a')
        data = db.bookingsPast.find(
            {
                'bookingDateTimestamp':
                    {
                        '$gte': int(currentdate),
                        '$lt': int(lastdate)
                    },
                'cityId': ObjectId(city)
            }
        )
    elif (zoneId is None or zoneId == 0) and int(status) != 0:
        print('b')
        data = db.bookingsPast.find(
            {
                'bookingDateTimestamp':
                    {
                        '$gte': int(currentdate),
                        '$lt': int(lastdate)
                    },
                'cityId': ObjectId(city),
                'bookingStatus': int(status)
            }
        )
    elif (zoneId is not None or zoneId != 0) and int(status) == 0:
        print('c')
        data = db.bookingsPast.find(
            {
                'bookingDateTimestamp':
                    {
                        '$gte': int(currentdate),
                        '$lt': int(lastdate)
                    },
                'cityId': ObjectId(city),
                'pickupArea.zoneId': str(zoneId),
            }
        )
    elif (zoneId is not None or zoneId != 0) and int(status) != 0:
        print('d')
        data = db.bookingsPast.find(
            {
                'bookingDateTimestamp':
                    {
                        '$gte': int(currentdate),
                        '$lt': int(lastdate)
                    },
                'cityId': ObjectId(city),
                'pickupArea.zoneId': str(zoneId),
                'bookingStatus': int(status)
            }
        )
    for i in data:
        customerName = i['slaveDetails']['name']
        booking.append({
            "customerName": customerName,
            "bookingId": i['bookingId'],
            "latitude": i['pickup']['location']['latitude'],
            "longitude": i['pickup']['location']['longitude'],
            "status": i['bookingStatus'],
            "statusMsg": i['bookingStatusText'],
            "zoneId": i['pickupArea']['zoneId'],
            "zoneName": i['pickupArea']['zoneTitle'],
            "Date": i['bookingDate']
        })
    if len(booking) != 0:
        latlong = []
        df = pd.DataFrame(data=booking)
        df.Date = df.Date + pd.Timedelta('05:30:00')
        dates = datesofweeks(days, start_date, end_date) # call this function for find dates between two date
        if (int(days) == 2 and int(time) != 24) or (int(days) == 3 and int(time) != 24) or (int(days) == 4 and
                                                                                            int(time) != 24) or \
                (int(days) == 5 and int(time) != 24):
            '''
                when the days is 2 or 3 or 4 or 5 and hour is not 24 (particular hour) perform this one
                2 for (1 week) and 2 for (1 Month) and 3 for (last 1 Year) and 5 for (Custom Dates)
            '''
            print('time is not 24 and days is 2 or 3 or 4')
            bookingexpired = 0
            totalride = 0
            bookingdeclined = 0
            bookingcompeted = 0
            providercancel = 0
            customercancel = 0
            d = []
            for i in dates:
                date_time = []
                startdate = i.replace(hour=int(time), minute=0, second=0, microsecond=0)
                enddate = i.replace(hour=int(time), minute=59, second=59, microsecond=0)
                sd = startdate.strftime("%Y-%m-%d %H:%M")
                ed = enddate.strftime("%Y-%m-%d %H:%M")
                mask = (df['Date'] >= sd) & (
                        df['Date'] <= ed)
                total = df.loc[mask]
                if len(total) != 0:
                    dataframe = pd.DataFrame(data=total)
                    df_data = dataframe[['bookingId', 'latitude', 'longitude', 'Date', 'statusMsg', 'customerName', 'zoneName']]
                    final_normalized_jsondata = df_data.to_dict('records')
                    for h in range(0, 24):
                        if h == int(time):
                            date_time.append(len(final_normalized_jsondata))
                        else:
                            date_time.append(0)
                    for i in final_normalized_jsondata:
                        i['Date'] = i['Date'].strftime("%d-%b-%Y %H:%M:%S")
                        bookingInfo.append(i)
                    bookingCompeted = (dataframe['status'] == 12).sum()
                    bookingDeclined = (dataframe['status'] == 3).sum()
                    bookingExpired = (dataframe['status'] == 13).sum()
                    providerCancel = (dataframe['status'] == 5).sum()
                    customerCancel = (dataframe['status'] == 4).sum()
                    totalride = len(final_normalized_jsondata) + totalride
                    bookingdeclined += bookingDeclined
                    bookingexpired += bookingExpired
                    bookingcompeted += bookingCompeted
                    providercancel += providerCancel
                    customercancel += customerCancel
                    d.append(date_time)
            new_df = pd.DataFrame(data=d)
            Total = new_df.sum()
            total = []
            for i in Total:
                total.append(i)
            latlong.append({
                "bookingInfo": bookingInfo,
                "totalRide": int(totalride),
                "bookingExpired": int(bookingexpired),
                "bookingCompeted": int(bookingcompeted),
                "providerCancel": int(providercancel),
                "customerCancel": int(customercancel),
                "bookingDeclined": int(bookingdeclined),
                "Chart": total
            })
            return latlong
        elif (int(days) == 0 and int(time) != 24) or (int(days) == 1 and int(time) != 24):
            '''
                If days is 0 and 1 and hours is not 24 (particular hour)
                0 for Today
                1 for Yesterday 
            '''
            print('time is not 24 and days is 0 and 1')
            date_time = []
            latlongdata = []
            startdate = None
            if int(days) == 0:
                startdate = datetime.datetime.now()
            elif int(days) == 1:
                currentdate = datetime.datetime.now() - datetime.timedelta(days=1)
                startdate = currentdate
            for i in range(0, 24):
                if i == int(time):
                    startdate = startdate.replace(hour=i, minute=0, second=0, microsecond=0)
                    enddate = startdate.replace(hour=i, minute=59, second=59, microsecond=0)
                    sd = startdate.strftime("%Y-%m-%d %H:%M")
                    ed = enddate.strftime("%Y-%m-%d %H:%M")
                    mask = (df['Date'] >= sd) & (
                            df['Date'] <= ed)
                    total = df.loc[mask]
                    if len(total) != 0:
                        dataframe = pd.DataFrame(data=total)
                        df_data = dataframe[
                            ['bookingId', 'latitude', 'longitude', 'Date', 'statusMsg', 'customerName', 'zoneName']]
                        final_normalized_jsondata = df_data.to_dict('records')
                        for i in final_normalized_jsondata:
                            i['Date'] = i['Date'].strftime("%d-%b-%Y %H:%M:%S")
                            bookingInfo.append(i)
                        bookingCompeted = (dataframe['status'] == 12).sum()
                        bookingDeclined = (dataframe['status'] == 3).sum()
                        bookingExpired = (dataframe['status'] == 13).sum()
                        providerCancel = (dataframe['status'] == 5).sum()
                        customerCancel = (dataframe['status'] == 4).sum()
                        latlong.append({
                            "bookingInfo": bookingInfo,
                            "totalRide": len(final_normalized_jsondata),
                            "bookingExpired": int(bookingExpired),
                            "bookingCompeted": int(bookingCompeted),
                            "providerCancel": int(providerCancel),
                            "customerCancel": int(customerCancel),
                            "bookingDeclined": int(bookingDeclined),
                        })
                    if len(total) != 0:
                        date_time.append(len(total))
                    else:
                        date_time.append(0)
                else:
                    date_time.append(0)
            for j in latlong:
                j["Chart"] = date_time
                latlongdata.append(j)
            return latlongdata
        elif int(time) == 24:
            print('time is 24')
            '''
               If hours is 24 (display all data for 0 to 23 four) 
            '''
            date_time = []
            if (int(days) == 0) or (int(days) == 1):
                startdate = datetime.datetime.now()
                if int(days) == 0:
                    startdate = datetime.datetime.now()
                elif int(days) == 1:
                    currentdate = datetime.datetime.now() - datetime.timedelta(days=1)
                    startdate = currentdate
                '''
                    when the days is 0 and 1 perform this one
                    0 for today and 1 for yesterday
                '''
                df_data = df[['bookingId', 'latitude', 'longitude', 'Date', 'statusMsg', 'customerName', 'zoneName']]
                final_normalized_jsondata = df_data.to_dict('records')
                bookingCompeted = (df['status'] == 12).sum()
                bookingDeclined = (df['status'] == 3).sum()
                bookingExpired = (df['status'] == 13).sum()
                providerCancel = (df['status'] == 5).sum()
                customerCancel = (df['status'] == 4).sum()
                for i in final_normalized_jsondata:
                    i['Date'] = i['Date'].strftime("%d-%b-%Y %H:%M:%S")
                    bookingInfo.append(i)
                df = df.set_index('Date')
                for i in range(0, 24):
                    startdate = startdate.replace(hour=i, minute=0, second=0, microsecond=0)
                    enddate = startdate.replace(hour=i, minute=59, second=59, microsecond=0)
                    sd = startdate.strftime("%Y-%m-%d %H:%M")
                    ed = enddate.strftime("%Y-%m-%d %H:%M")
                    total = len(df.loc[sd:ed])
                    if total != 0:
                        date_time.append(total)
                    else:
                        date_time.append(0)
                latlong.append({
                    "bookingInfo": bookingInfo,
                    "totalRide": len(final_normalized_jsondata),
                    "bookingExpired": int(bookingExpired),
                    "bookingCompeted": int(bookingCompeted),
                    "providerCancel": int(providerCancel),
                    "customerCancel": int(customerCancel),
                    "bookingDeclined": int(bookingDeclined),
                    "Chart": date_time
                })
                return latlong
            elif (int(days) == 2) or (int(days) == 3) or (int(days) == 4) or (int(days) == 5):
                '''
                    when the days is 2 or 3 or 4 perform this one
                    2 for (1 week) and 2 for (1 Month) and 3 for (last 1 Year)
                '''
                print('time is 24 and days is 2 or 3 or 4 or 5')
                bookingexpired = 0
                bookingdeclined = 0
                totalride = 0
                bookingcompeted = 0
                providercancel = 0
                customercancel = 0
                d = []
                for z in dates:
                    date_time = []
                    for h in range(0, 24):
                        startdate = z.replace(hour=h, minute=0, second=0, microsecond=0)
                        enddate = z.replace(hour=h, minute=59, second=59, microsecond=0)
                        sd = startdate.strftime("%Y-%m-%d %H:%M")
                        ed = enddate.strftime("%Y-%m-%d %H:%M")
                        mask = (df['Date'] >= sd) & (
                                df['Date'] <= ed)
                        total = df.loc[mask]
                        dataframe = pd.DataFrame(data=total)
                        bookingCompeted = (dataframe['status'] == 12).sum()
                        bookingDeclined = (dataframe['status'] == 3).sum()
                        bookingExpired = (dataframe['status'] == 13).sum()
                        providerCancel = (dataframe['status'] == 5).sum()
                        customerCancel = (dataframe['status'] == 4).sum()
                        df_data = dataframe[['bookingId', 'latitude', 'longitude', 'Date', 'statusMsg', 'customerName', 'zoneName']]
                        final_normalized_jsondata = df_data.to_dict('records')
                        date_time.append(len(final_normalized_jsondata))
                        for i in final_normalized_jsondata:
                            i['Date'] = i['Date'].strftime("%d-%b-%Y %H:%M:%S")
                            bookingInfo.append(i)
                        totalride = len(final_normalized_jsondata) + totalride
                        bookingdeclined += bookingDeclined
                        bookingexpired += bookingExpired
                        bookingcompeted += bookingCompeted
                        providercancel += providerCancel
                        customercancel += customerCancel
                    d.append(date_time)
                df = pd.DataFrame(data=d)
                Total = df.sum()
                total = []
                for i in Total:
                    total.append(i)
                latlong.append({
                    "bookingInfo": bookingInfo,
                    "totalRide": int(totalride),
                    "bookingExpired": int(bookingexpired),
                    "bookingCompeted": int(bookingcompeted),
                    "providerCancel": int(providercancel),
                    "customerCancel": int(customercancel),
                    "bookingDeclined": int(bookingdeclined),
                    "Chart": total
                })
                return latlong
    else:
        return latlong


def datesofweeks(days, start_date, end_date):
    # date range for finding dates
    if int(days) == 2:
        range = 7
        enddate = (datetime.datetime.now() - datetime.timedelta(days=range - 1)).strftime("%Y-%m-%d")
        mydates = pd.date_range(enddate, periods=range,
                                freq='D').tolist()  # we gate dates between two dates using pandas
        return mydates
    elif int(days) == 3:
        range = 30
        enddate = (datetime.datetime.now() - datetime.timedelta(days=range - 1)).strftime("%Y-%m-%d")
        mydates = pd.date_range(enddate, periods=range,
                                freq='D').tolist()  # we gate dates between two dates using pandas
        return mydates
    elif int(days) == 4:
        range = 365
        enddate = (datetime.datetime.now() - datetime.timedelta(days=range - 1)).strftime("%Y-%m-%d")
        mydates = pd.date_range(enddate, periods=range,
                                freq='D').tolist()  # we gate dates between two dates using pandas
        return mydates
    elif int(days) == 0:
        range = 0
        enddate = (datetime.datetime.now() - datetime.timedelta(days=range - 1)).strftime("%Y-%m-%d")
        mydates = pd.date_range(enddate, periods=range,
                                freq='D').tolist()  # we gate dates between two dates using pandas
        return mydates
    elif int(days) == 1:
        range = 1
        enddate = (datetime.datetime.now() - datetime.timedelta(days=range - 1)).strftime("%Y-%m-%d")
        mydates = pd.date_range(enddate, periods=range,
                                freq='D').tolist()  # we gate dates between two dates using pandas
        return mydates
    if int(days) == 5:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M')
        startdate=start_date.strftime("%Y-%m-%d")
        enddate=end_date.strftime("%Y-%m-%d")
        mydates = pd.date_range(start=startdate, end=enddate,
                                freq='D').tolist() # we gate dates between two dates using pandas

        return mydates


class FetchCity(APIView):
    def get(self, request):
        try:
            city = []
            get_city = db.cities.find({})
            for i in get_city:
                city.append({
                    'name': i['city'],
                    'id': str(i['_id'])
                })
            return JsonResponse(city, safe=False, status=200)
        except:
            error_message = {
                "error": "Bad request"
            }
            return JsonResponse(error_message, status=500)


class CityLatLong(APIView):
    def post(self, request):
        # try:
            data = request.data
            id = data['cityId']
            get_city = db.cities.find({'_id': ObjectId(id)})
            for i in get_city:
                latlong = i['pointsProps']
            latlong['fillOpacity'] = 0
            latlong["strokeColor"] = "#FFFF00"
            return JsonResponse(latlong, safe=False, status=200)
        # except:
        #     error_message = {
        #         "error": "Bad request"
        #     }
        #     return JsonResponse(error_message, status=500)


class GetCitiesZoneAPI(APIView):
    def post(self, request):
        try:
            # fetch particular city data from DataBase
            data = request.data
            id = data['cityId']
            get_city = db.areaZones.find({'cityId': ObjectId(id)})
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


class CityZone(APIView):
    def post(self, request):
        # try:
            # fetch particular city data from DataBase
            data = request.data
            id = data['cityId']
            get_city = db.areaZones.find({'cityId': ObjectId(id)})
            title_zone_main = []
            for i in get_city:
                title_zone_main.append(i['pointsProps'])
            for j in title_zone_main:
                j['fillOpacity'] = 0
                j["strokeColor"] = "#FFFFFF"
            return JsonResponse(title_zone_main, safe=False, status=200)
        # except:
        #     message = [
        #         {
        #             "message": "Internal Server Error"
        #         }
        #     ]
        #     error_message = response_messages(2, message)
        #     return JsonResponse(error_message, safe=False, status=500)


def dashboard(request):
    try:
        city = []
        get_city = requests.get(URL + "city/")
        for city_data in get_city.json():
            city.append(city_data)
        return render(request, 'HeatMap/kerrymap.html', context={'city': city})
    except:
        message = [
            {
                "message": "Internal Server Error"
            }
        ]
        error_message = response_messages(2, message)
        return JsonResponse(error_message, safe=False, status=500)


class GetCitiesZoneLatAPI(APIView):
    def post(self, request):
        try:
            latlong = None
            data = request.data
            id = data['zoneId']
            get_city = db.areaZones.find({'_id': ObjectId(id)})
            for i in get_city:
                latlong = i['pointsProps']
            latlong['fillOpacity'] = 0
            latlong["strokeColor"] = "#FFFF00"
            return JsonResponse(latlong, safe=False, status=200)
        except:
            message = [
                {
                    "message": "Internal Server Error"
                }
            ]
            error_message = response_messages(2, message)
            return JsonResponse(error_message, safe=False, status=500)


class ChorPlethMap(APIView):
    def get(self, request, date):
        try:
            get_city = db.areaZones.find({'cityId': ObjectId(date)})
            lat = []
            for i in get_city:
                lat.append(i)
            length = len(lat)
            latlong = []
            if length != 0:
                d = pd.DataFrame(data=lat)
                df_data = d[['title', 'polygons', '_id']]
                final_normalized_jsondata = df_data.to_dict('records')
                title = []
                count = 0
                for i in final_normalized_jsondata:
                    latlong.append(
                        {
                            "type": "Feature",
                            "geometry": i['polygons'],
                            "properties": {
                                "STATE": count + 1,
                                "NAME": i["title"]
                            }
                        }
                    )
                    count = count+1
                dd = {"type": "FeatureCollection", "features": latlong}
                return JsonResponse(dd, safe=False, status=200)
            else:
                dd = {"type": "FeatureCollection", "features": latlong}
                return JsonResponse(dd, safe=False, status=200)
        except:
            message = [
                {
                    "message": "Internal Server Error"
                }
            ]
            error_message = response_messages(2, message)
            return JsonResponse(error_message, safe=False, status=500)


class StateData(APIView):
    def post(self, request, city, date, status, time, startdate, enddate, zone_id):
        try:
            time_zone = "Asia/Kolkata"
            count = 0
            if int(date) != 5:
                currentdate, lastdate = daterange(date, time, time_zone, startdate, enddate)
            else:
                currentdate = startdate
                lastdate = enddate
            get_zone = db.areaZones.find({'cityId': ObjectId(city)})
            id = []
            for i in get_zone:
                id.append(i)
            df = pd.DataFrame(data=id)
            df_zone = df[['_id']].astype('str')
            final_normalized_jsondata = df_zone.to_dict('records')
            '''
                find data from database status wise or without status
            '''
            zone_total = [[
                "DP02_0066PE",
                "state"
            ]]
            if zone_id is None or zone_id == '' or zone_id == '0':
                for i in final_normalized_jsondata:
                    if int(status) == 0:
                        get_city = db.bookingsPast.find(
                            {
                                'bookingDateTimestamp':
                                    {
                                        '$gte': int(currentdate),
                                        '$lt': int(lastdate)
                                    },
                                'pickupArea.zoneId': i['_id']
                            }
                        )
                    else:
                        get_city = db.bookingsPast.find(
                            {
                                'bookingDateTimestamp':
                                    {
                                        '$gte': int(currentdate),
                                        '$lt': int(lastdate)
                                    },
                                'pickupArea.zoneId': i['_id']
                                , 'bookingStatus': int(status)
                            }
                        )
                    lat = []
                    for j in get_city:
                        lat.append(j)
                    if int(time) != 24:
                        if len(lat) != 0:
                            df_t = pd.DataFrame(data=lat)
                            df_t.bookingDate = df_t.bookingDate + pd.Timedelta('05:30:00')
                            df_t = df_t.set_index('bookingDate')
                            d = df_t.between_time(str(time)+':00', str(int(time)+1)+':00')
                        else:
                            d = pd.DataFrame(data=lat)
                    else:
                        d = pd.DataFrame(data=lat)
                    zone_total.append([len(d), str(count + 1)])
                    count = count + 1
                return JsonResponse(zone_total, safe=False, status=200)
            elif zone_id != '' and zone_id != '0':
                for i in final_normalized_jsondata:
                    lat = []
                    if i['_id'] == zone_id:
                        if int(status) == 0:
                            get_city = db.bookingsPast.find(
                                {
                                    'bookingDateTimestamp':
                                        {
                                            '$gte': int(currentdate),
                                            '$lt': int(lastdate)
                                        },
                                    'pickupArea.zoneId': i['_id']
                                }
                            )
                        else:
                            get_city = db.bookingsPast.find(
                                {
                                    'bookingDateTimestamp':
                                        {
                                            '$gte': int(currentdate),
                                            '$lt': int(lastdate)
                                        },
                                    'pickupArea.zoneId': str(i['_id'])
                                    , 'bookingStatus': int(status)
                                }
                            )
                        for j in get_city:
                            lat.append(j)
                    else:
                        lat = []
                    if int(time) != 24:
                        if len(lat) != 0:
                            df_t = pd.DataFrame(data=lat)
                            df_t.bookingDate = df_t.bookingDate + pd.Timedelta('05:30:00')
                            df_t = df_t.set_index('bookingDate')
                            d = df_t.between_time(str(time)+':00', str(int(time)+1)+':00')
                        else:
                            d = pd.DataFrame(data=lat)
                    else:
                        d = pd.DataFrame(data=lat)
                    zone_total.append([len(d), str(count + 1)])
                    count = count + 1
                return JsonResponse(zone_total, safe=False, status=200)
        except:
            message = [
                {
                    "message": "Internal Server Error"
                }
            ]
            error_message = response_messages(2, message)
            return JsonResponse(error_message, safe=False, status=500)