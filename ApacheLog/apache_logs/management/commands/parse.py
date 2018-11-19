#! python
# -*- coding: utf-8 -*-

"""
Module: parse.py
Author: HZ
Created: October 27, 2018

Description: ''
"""

# global imports below: built-in, 3rd party, own
from django.core.management import BaseCommand
from apache_logs.models import ApacheAccessLog, ApacheErrorLog
from log_formats.models import LogFormats
from sites.models import Site
from ApacheLog import settings
import apache_log_parser
import re
from django.db import IntegrityError


# Ownership information

__author__ = 'HZ'
__copyright__ = "Copyright 2018, HZ, Divine IT Ltd."
__credits__ = ["HZ"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "HZ"
__email__ = "hz.ce06@gmail.com"
__status__ = "Development"


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('server_url', type=str, help='The server address for which we are parsing logs.')

        # Named (optional) arguments
        parser.add_argument('-lt', '--log_type', type=str, choices=['access_log', 'error_log'], help='The log type: access_log/error_log')
        #     '--delete',
        #     action='store_true',
        #     dest='delete',
        #     default=False,
        #     help='Delete poll instead of closing it',
        # )

    def handle(self, *args, **options):
        server_url = options['server_url']
        log_type = options['log_type']
        site = Site.objects.get(site_url=server_url)

        if log_type is not None:
            log_formats = LogFormats.objects.filter(site_id=site.id, log_type=log_type)
        else:
            log_formats = LogFormats.objects.filter(site_id=site.id)

        if len(log_formats) == 0:
            self.stdout.write(self.style.WARNING('No log format exists for this server %s.' % server_url))
        else:
            lines_parsed = 0
            parsed_log_list = []
            log_lines = []

            if log_type is None:
                for log_format in log_formats:
                    found = False
                    '''try to parse with error_log'''
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
                    expr = re.compile('\s*'.join(parts))
                    log_file = open(settings.apache_log, 'r')
                    for line in log_file:
                        try:
                            line = line.strip()
                            if bool(line):
                                # import pdb
                                # pdb.set_trace()
                                rx = expr.search(line)
                                if rx is not None:
                                    lines_parsed += 1
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
                                        'log_format_id': log_format.id,
                                        'site_id': site.id
                                    }
                                    try:
                                        apl = ApacheErrorLog(**errors)
                                        parsed_log_list.append(apl)
                                        log_lines.append(line)
                                    except Exception as e:
                                        self.stdout.write(self.style.WARNING('Error in creating ApacheErrorLog object'))
                        except Exception as e:
                            break
                    try:
                        from itertools import islice
                        start = 0
                        '''Batch size is : 2 for now as the sample size is small'''
                        batch_size = 2
                        stop = batch_size
                        # while stop <= len(parsed_log_list):
                        while stop <= len(parsed_log_list):
                            batch = list(islice(parsed_log_list, start, stop))
                            if not batch:
                                break
                            ApacheErrorLog.objects.bulk_create(batch, batch_size)
                            start = stop
                            stop += batch_size
                            if stop > len(parsed_log_list):
                                stop = len(parsed_log_list)
                    except IntegrityError as ie:
                        # should not happen as duplicates should be removed before..
                        self.stdout.write(self.style.WARNING("Uniqueness failed! Most probably file uploaded before! Site Id: %s, Site: %s" % (site.id, site.site_url)))
                    except Exception, e:
                        self.stdout.write(self.style.WARNING(str(e)))
                    log_file.close()
                    if lines_parsed > 0:
                        self.stdout.write(self.style.SUCCESS('%d log lines parsed by error log1' % (lines_parsed)))
                        found = True
                        break
                    '''try to parse with access_log'''
                    line_parser = apache_log_parser.make_parser(str(log_format.log_format))
                    log_file = open(settings.apache_log, 'r')
                    for line in log_file:
                        try:
                            line = line.strip()
                            if bool(line):
                                data = line_parser(line)
                                apl = ApacheAccessLog(**data)
                                apl.full_line = line
                                apl.site_id = site.id
                                apl.log_format_id = log_format.id
                                parsed_log_list.append(apl)
                                log_lines.append(line)
                                lines_parsed += 1
                        except Exception as e:
                            break
                    try:
                        from itertools import islice
                        start = 0
                        batch_size = 10
                        stop = batch_size
                        while stop <= len(parsed_log_list):
                            batch = list(islice(parsed_log_list, start, stop))
                            if not batch:
                                break
                            ApacheAccessLog.objects.bulk_create(batch, batch_size)
                            start = stop
                            stop += batch_size
                            if stop > len(parsed_log_list):
                                stop = len(parsed_log_list)
                    except IntegrityError as ie:
                        # should not happen as duplicates should be removed before..
                        self.stdout.write(self.style.WARNING("Uniqueness failed! Most probably file uploaded before! Site Id: %s, Site: %s" % (site.id, site.site_url)))
                        #print "Duplicates found!"
                    except Exception, e:
                        self.stdout.write(self.style.WARNING(str(e)))
                    log_file.close()
                    if lines_parsed > 0:
                        self.stdout.write(self.style.SUCCESS('%d log lines parsed by access log' % (lines_parsed)))
                        found = True
                        break
                if not found:
                    self.stdout.write(self.style.WARNING('Invalid logfile/format'))

            elif log_type == 'error_log':
                # import pdb
                # pdb.set_trace()
                '''currently there is only one error log format, so we don't need to check for all'''
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
                expr = re.compile('\s*'.join(parts))
                log_file = open(settings.apache_log, 'r')
                for line in log_file:
                    try:
                        line = line.strip()
                        if bool(line):
                            # import pdb
                            # pdb.set_trace()
                            rx = expr.search(line)
                            if rx is not None:
                                lines_parsed += 1
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
                                    'log_format_id': log_formats[0].id,
                                    'site_id': site.id
                                }
                                try:
                                    apl = ApacheErrorLog(**errors)
                                    parsed_log_list.append(apl)
                                    log_lines.append(line)
                                except Exception as e:
                                    self.stdout.write(self.style.WARNING('Error in creating ApacheErrorLog object'))
                    except Exception as e:
                        break
                try:
                    from itertools import islice
                    start = 0
                    '''Batch size is : 2 for now as the sample size is small'''
                    batch_size = 2
                    stop = batch_size
                    # while stop <= len(parsed_log_list):
                    while stop <= len(parsed_log_list):
                        batch = list(islice(parsed_log_list, start, stop))
                        if not batch:
                            break
                        ApacheErrorLog.objects.bulk_create(batch, batch_size)
                        start = stop
                        stop += batch_size
                        if stop > len(parsed_log_list):
                            stop = len(parsed_log_list)
                except IntegrityError as ie:
                    # should not happen as duplicates should be removed before..
                    self.stdout.write(self.style.WARNING(
                        "Uniqueness failed! Most probably file uploaded before! Site Id: %s, Site: %s" % (
                        site.id, site.site_url)))
                except Exception, e:
                    self.stdout.write(self.style.WARNING(str(e)))
                log_file.close()
                if lines_parsed > 0:
                    self.stdout.write(self.style.SUCCESS('%d log lines parsed by error log2' % (lines_parsed)))
                else:
                    self.stdout.write(self.style.WARNING('Invalid logfile/format'))
            elif log_type == 'access_log':
                for log_format in log_formats:
                    found = False
                    line_parser = apache_log_parser.make_parser(str(log_format.log_format))
                    log_file = open(settings.apache_log, 'r')
                    for line in log_file:
                        try:
                            line = line.strip()
                            if bool(line):
                                data = line_parser(line)
                                apl = ApacheAccessLog(**data)
                                apl.full_line = line
                                apl.site_id = site.id
                                apl.log_format_id = log_format.id
                                parsed_log_list.append(apl)
                                log_lines.append(line)
                                lines_parsed += 1
                        except Exception as e:
                            break
                    try:
                        from itertools import islice
                        start = 0
                        batch_size = 10
                        stop = batch_size
                        while stop <= len(parsed_log_list):
                            batch = list(islice(parsed_log_list, start, stop))
                            if not batch:
                                break
                            ApacheAccessLog.objects.bulk_create(batch, batch_size)
                            start = stop
                            stop += batch_size
                            if stop > len(parsed_log_list):
                                stop = len(parsed_log_list)
                    except IntegrityError as ie:
                        # should not happen as duplicates should be removed before..
                        self.stdout.write(self.style.WARNING("Uniqueness failed! Most probably file uploaded before! Site Id: %s, Site: %s" % (site.id, site.site_url)))
                        #print "Duplicates found!"
                    except Exception, e:
                        self.stdout.write(self.style.WARNING(str(e)))
                    log_file.close()
                    if lines_parsed > 0:
                        self.stdout.write(self.style.SUCCESS('%d log lines parsed by access log' % (lines_parsed)))
                        found = True
                        break
                if not found:
                    self.stdout.write(self.style.WARNING('Invalid logfile/format'))
            else:
                self.stdout.write(self.style.WARNING('Invalid log format or file'))
