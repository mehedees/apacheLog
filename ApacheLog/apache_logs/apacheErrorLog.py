import re
from .models import ApacheErrorLog
import json
from django.db import IntegrityError
from django.shortcuts import render
from .models import ApacheAccessLog, ApacheErrorLog
from sites.models import Site
from log_formats.models import LogFormats
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import apache_log_parser
import apacheErrorLog


def parse_error_log(log_file, site_id, log_format_id, request):
    parts = [
        r"\[(?P<time>[A-Za-z]{3} [A-Za-z]{3} \d\d \d\d:\d\d:\d\d[\.\d]*\s[\d]{4})\]",
        r"\[(?P<logModule>.*)?:(?P<logLevel>[a-z]+)\]",
        r"\[pid\s(?P<pid>[\d]+):tid\s(?P<tid>[\d]+)\]",
        r"(?P<srcFileName>.*)?",
        r"(?P<errorStatus>.*)?",
        r"\[client\s(?P<remoteHost>[\d\.:]+)\]",
        r"(?P<errorMsg>.+),",
        r"(referer:\s*)?(?P<referer>.*)"
    ]
    status = "Valid"
    #errors = []
    parsed_log_list = []
    log_lines = []
    expr = re.compile('\s*'.join(parts))

    for line in log_file.file:
        try:
            line = line.strip()
            if bool(line) and line not in log_lines:
                # import pdb
                # pdb.set_trace()
                rx = expr.search(line)
                # try:
                #
                # except Exception as e:
                #     return render(request, 'upload_log.html', {'msg': line})



                time = rx.group('time') if rx.group('time') else ''
                logModule = rx.group('logModule') if rx.group('logModule') else ''
                logLevel = rx.group('logLevel') if rx.group('logLevel') else ''
                pid = rx.group('pid') if rx.group('pid') else ''
                tid = rx.group('tid') if rx.group('tid') else ''
                srcFileName = rx.group('srcFileName') if rx.group('srcFileName') else ''
                status = rx.group('errorStatus') if rx.group('errorStatus') else ''
                remoteHost = rx.group('remoteHost') if rx.group('remoteHost') else ''
                errorMsg = rx.group('errorMsg') if rx.group('errorMsg') else ''
                referer = rx.group('referer') if rx.group('referer') else ''
                errors = {
                    'full_line': line,
                    'time': time,
                    'log_module': logModule,
                    'log_level': logLevel,
                    'pid': pid,
                    'tid': tid,
                    'src_fileName': srcFileName,
                    'status': status,
                    'remote_host': remoteHost,
                    'error_msg': errorMsg,
                    'referer': referer,
                    'log_format_id': log_format_id,
                    'site_id': site_id
                }
                # import pdb
                # pdb.set_trace()
                try:
                    apl = ApacheErrorLog(**errors)
                    #apl.id = ''
                    parsed_log_list.append(apl)
                    log_lines.append(line)
                except Exception as e:
                    return render(request, 'upload_log.html',
                                  {'msg': e.message})
        except Exception as e:
            status = "Invalid"
            return parsed_log_list, log_lines, status

    # for line in log_file.readlines():
    #     rx = expr.search(line)
    #     time = rx.group('time') if rx.group('time') else ''
    #     logModule = rx.group('logModule') if rx.group('logModule') else ''
    #     logLevel = rx.group('logLevel') if rx.group('logLevel') else ''
    #     pid = rx.group('pid') if rx.group('pid') else ''
    #     tid = rx.group('tid') if rx.group('tid') else ''
    #     srcFileName = rx.group('srcFileName') if rx.group('srcFileName') else ''
    #     status = rx.group('errorStatus') if rx.group('errorStatus') else ''
    #     remoteHost = rx.group('remoteHost') if rx.group('remoteHost') else ''
    #     errorMsg = rx.group('errorMsg') if rx.group('errorMsg') else ''
    #     referer = rx.group('referer') if rx.group('referer') else ''
    #     errors.append({'Request Time': time, 'Log Module': logModule, 'Log Level': logLevel, 'PID': pid, 'TID': tid,
    #                    'SRC File Name': srcFileName, 'Status': status, 'Remote Host': remoteHost,
    #                    'Error Message': errorMsg, 'Referer': referer})
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(errors)
    #print(errors)
    return parsed_log_list, log_lines, status
