from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
import xlwt
from apache_logs.models import ApacheAccessLog
from sites.models import Site


def home(request):
    return render(request, 'index.html', {})


def report(request):
    code_list = [
        '--all--', '100', '101', '102', '200', '201', '202', '203', '204', '205', '206', '207', '208', '226',
        '300', '301', '302', '303', '304', '305', '306', '307', '308', '400', '401', '402', '403',
        '404', '405', '406', '407', '408', '409', '410', '411', '412', '413', '414', '415', '416',
        '417', '418', '421', '422', '423', '424', '426', '428', '429', '431', '451', '500', '501',
        '502', '503', '504', '505', '506', '507', '508', '510', '511'
    ]

    sites = Site.objects.all()
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    site = request.GET.get('site')
    method = request.GET.get('method')
    code = request.GET.get('code')

    # all parameters are not mandatory..site, from_date, to_date ei 3 ta..mark them at required in html
    if from_date <= to_date and site:
        q_objects = [Q(time_received_datetimeobj__range=[from_date, to_date]), Q(site_id=site)]
        if method != 'all':
            q_objects.append(Q(request_method__istartswith=method))
        if code != '--all--':
            q_objects.append(Q(status__istartswith=code))

        query = q_objects.pop()
        for item in q_objects:
            query &= item
        log_list = ApacheAccessLog.objects.filter(query).order_by('-time_millisecond')
    else:
        log_list = ApacheAccessLog.objects.order_by('-time_millisecond')[:25]

    download = request.GET.get('download')

    if download == 'download':
        return dump_as_xls(request, log_list)

    # pagination
    paginator = Paginator(log_list, 20)  # Show 30 logs per page
    page = request.GET.get('page')
    try:
        log_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        log_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        log_list = paginator.page(paginator.num_pages)
    context = {
        "title": "Report",
        "logs": log_list,
        "site_list": sites,
        "site_id": int(site or 0),
        "code_list": code_list
    }
    return render(request, 'report.html', context)


def export_xls(request, log_list, flag):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="apache_log_parser_report.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('ApacheLog')
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Receive Time', 'Method', 'Response', 'Time', 'URL']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    font_style.font.wrap = 1
    font_style.font.height = 240
    font_style.font._weight = 240

    if flag:
        rows = log_list.all().values_list('time_received_tz', 'request_method', 'status', 'time_us', 'request_url_path')
    else:
        rows = ApacheAccessLog.all().values_list('time_received_tz', 'request_method', 'status', 'time_us', 'request_url_path')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    ws.col(0).width = 7000
    ws.col(4).width = 15000

    wb.save(response)
    return response


def dump_as_xls(request, data):
    """Creates report in xls format"""
    import xlwt

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Apache_Access_Log_Report.xls"'

    header_font = xlwt.Font()
    header_font.name = 'Times New Roman'
    header_font.bold = True
    header_font.height = 280

    header_borders = xlwt.Borders()
    header_borders.left = 6
    header_borders.right = 6
    header_borders.top = 6
    header_borders.bottom = 6

    header_alignment = xlwt.Alignment()
    header_alignment.horz = xlwt.Alignment.HORZ_CENTER
    header_alignment.vert = xlwt.Alignment.VERT_CENTER

    header_style = xlwt.XFStyle()
    header_style.font = header_font
    header_style.borders = header_borders
    header_style.alignment = header_alignment

    cell_font = xlwt.Font()
    cell_font.name = 'Times New Roman'
    cell_font.height = 240

    cell_borders = xlwt.Borders()
    cell_borders.left = 1
    cell_borders.right = 1
    cell_borders.top = 1
    cell_borders.bottom = 1

    cell_alignment_L = xlwt.Alignment()
    cell_alignment_L.horz = xlwt.Alignment.HORZ_LEFT
    cell_alignment_L.vert = xlwt.Alignment.VERT_CENTER

    cell_alignment_C = xlwt.Alignment()
    cell_alignment_C.horz = xlwt.Alignment.HORZ_CENTER
    cell_alignment_C.vert = xlwt.Alignment.VERT_CENTER

    cell_alignment_R = xlwt.Alignment()
    cell_alignment_R.horz = xlwt.Alignment.HORZ_RIGHT
    cell_alignment_R.vert = xlwt.Alignment.VERT_CENTER

    cell_style_L = xlwt.XFStyle()
    cell_style_L.font = cell_font
    cell_style_L.borders = cell_borders
    cell_style_L.alignment = cell_alignment_L

    cell_style_C = xlwt.XFStyle()
    cell_style_C.font = cell_font
    cell_style_C.borders = cell_borders
    cell_style_C.alignment = cell_alignment_C

    cell_style_R = xlwt.XFStyle()
    cell_style_R.font = cell_font
    cell_style_R.borders = cell_borders
    cell_style_R.alignment = cell_alignment_R
    cell_style_R.num_format_str = '0.000000'

    wb = xlwt.Workbook()

    keys = ['receive_time', 'request_method', 'status', 'response_time', 'request_url']
    headers = ['Receive Time', 'Method', 'Response', 'Time (sec)', 'URL']

    count = 1
    start = 0
    while True:
        ws1 = wb.add_sheet('log_report_' + str(count))

        ws1.col(0).width = 7680
        ws1.col(1).width = 5120
        ws1.col(2).width = 5120
        ws1.col(3).width = 5120
        ws1.col(4).width = 12500

        ws1.write_merge(0, 0, 0, 4, "Apache Access Log Report", header_style)

        for i, each in enumerate(headers):
            ws1.write(2, i, each, header_style)

        index = 3
        for each in range(start, len(data)):
            ws1.write(index, 0, getattr(data[each], keys[0]), cell_style_C)
            ws1.write(index, 1, getattr(data[each], keys[1]), cell_style_C)
            ws1.write(index, 2, getattr(data[each], keys[2]), cell_style_C)
            ws1.write(index, 3, getattr(data[each], keys[3]), cell_style_R)
            ws1.write(index, 4, getattr(data[each], keys[4]), cell_style_L)
            index += 1
            if index > 65000:
                count += 1
                break
        if index > 65000:
            start = each + 1
            continue
        break

    wb.save(response)
    return response
