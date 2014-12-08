from django.conf.urls import *

urlpatterns = patterns('itscss.reports.reports.views',
    url(r'^$', 'index'),
    url(r'^(?P<report_id>\d+)$', 'detail'),
    url(r'^(?P<report_id>\d+)/json$', 'detail_json'),
    url(r'^(?P<report_id>\d+)/csv$', 'detail_csv')
)
