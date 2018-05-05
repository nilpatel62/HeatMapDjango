from django.conf.urls import url
from HeatMapp import views
# from DashboardandApis import views/views

app_name = 'HeatMapp'


urlpatterns = [
    # Api
    url(r'^HeatMap/$', views.initialize, name='initialize'),
    url(r'^getlatlong/(?P<cityname>[\w\-]+)$', views.GetCitiesDataAPI.as_view(), name='GetCitiesDataAPI'),
    url(r'^getcitylatlong/(?P<cityname>[\w\-]+)$', views.GetCitiesLatLongAPI.as_view(), name='GetCitiesDataAPI'),
    url(r'^getzonelatlong/(?P<cityname>[\w\-]+)$', views.GetZoneLatLongAPI.as_view(), name='GetZoneLatLongAPI'),
    # url(r'^getlatlong/$', views.GetCitiesDataAPI.as_view(), name='GetCitiesDataAPI'),
    url(r'^getzone/(?P<cityname>[\w\-]+)$', views.GetCitiesZoneAPI.as_view(), name='GetCitiesZoneAPI'),
    url(r'^getzonelat/(?P<id>[\w\-]+)$', views.GetCitiesZoneLatAPI.as_view(), name='GetCitiesZoneAPI'),
    url(r'^getdate/(?P<date>[\w\-]+)$', views.GetDateAPI.as_view(), name='GetDateAPI'),
    # url(r'^getareazone/(?P<zone>[\w\-]+)$', views.GetAreaZoneAPI.as_view(), name='GetAreaZoneAPI'),
]