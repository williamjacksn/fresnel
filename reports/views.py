import csv
import datetime
import decimal
import json

from django.conf import settings
from django.db import connection
from django.http import Http404, HttpResponse
from django.shortcuts import render

from itscss.reports.reports.report_defs import reports, report_exists, get_report


class FresnelEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return str(obj)
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return super(FresnelEncoder, self).default(obj)


def get_db_for_ctx():
    db = dict(settings.DATABASES['default'])
    sql = ('select date_format(convert_tz(max(last_sync), \'+00:00\', '
           '\'system\'), \'%Y-%m-%d %H:%i:%s\') as sync_time from '
           'lanrev_last_export_date')
    cur = connection.cursor()
    cur.execute(sql)
    row = cur.fetchone()
    db['SYNC_TIME'] = row[0]
    return db


def encode_row(row):
    out = list()
    for item in row:
        if item is None:
            out.append('')
        elif isinstance(item, basestring):
            out.append(item.encode('utf_8'))
        else:
            out.append(str(item).encode('utf_8'))
    return out


def index(request):
    ctx = dict(db=get_db_for_ctx(), reports=reports)
    response = render(request, 'reports/index.html', ctx)
    response['Content-Type'] = 'text/html; charset=windows-1252'
    return response


def detail(request, report_id):
    report_id = int(report_id)
    if not report_exists(report_id):
        raise Http404

    report = get_report(report_id)
    cur = connection.cursor()
    prompts = list()
    if report.prompts is None:
        cur.execute(report.sql)
    else:
        for prompt in report.prompts:
            if prompt in request.GET:
                prompts.append(request.GET.get(prompt))
            else:
                ctx = dict(db=get_db_for_ctx, report=report,
                           missing_prompt=prompt)
                response = render(request, 'reports/err_prompt.html', ctx)
                response['Content-Type'] = 'text/html; charset=windows-1252'
                return response
        cur.execute(report.sql, prompts)
    data = cur.fetchall()
    ctx = dict(db=get_db_for_ctx, report=report, data=data, prompts=prompts)
    response = render(request, 'reports/detail.html', ctx)
    response['Content-Type'] = 'text/html; charset=windows-1252'
    return response


def detail_csv(request, report_id):
    report_id = int(report_id)
    if not report_exists(report_id):
        raise Http404

    report = get_report(report_id)
    cur = connection.cursor()
    if report.prompts is None:
        cur.execute(report.sql)
    else:
        prompts = list()
        for prompt in report.prompts:
            if prompt in request.GET:
                prompts.append(request.GET.get(prompt))
            else:
                ctx = dict(prompt=prompt)
                response = render(request, 'reports/err_prompt.json', ctx)
                response['Content-Type'] = 'application/json; charset=utf-8'
                return response
        cur.execute(report.sql, prompts)

    response = HttpResponse(content_type='text/csv')
    content_disposition = 'attachment; filename="{}.csv"'.format(report.name)
    response['Content-Disposition'] = content_disposition
    writer = csv.writer(response)
    writer.writerow(report.columns)
    for row in cur.fetchall():
        writer.writerow(encode_row(row))
    return response


def detail_json(request, report_id):
    ct = 'application/json; charset=utf-8'
    report_id = int(report_id)
    if not report_exists(report_id):
        raise Http404

    data = list()
    report = get_report(report_id)
    cur = connection.cursor()
    if report.prompts is None:
        cur.execute(report.sql)
    else:
        prompts = list()
        for prompt in report.prompts:
            if prompt in request.GET:
                prompts.append(request.GET.get(prompt))
            else:
                ctx = dict(prompt=prompt)
                response = render(request, 'reports/err_prompt.json', ctx)
                response['Content-Type'] = ct
                return response
        cur.execute(report.sql, prompts)

    for row in cur.fetchall():
        record = dict()
        for idx, column in enumerate(report.columns):
            record[column] = row[idx] or ''
        data.append(record)

    response = HttpResponse(json.dumps(data, cls=FresnelEncoder))
    response['Content-Type'] = ct
    return response
