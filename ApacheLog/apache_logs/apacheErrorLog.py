import re

def parse_error_log(log_file):
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
    errors = []
    expr = re.compile('\s*'.join(parts))

    for line in log_file.readlines():
        rx = expr.search(line)
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
        errors.append({'Request Time': time, 'Log Module': logModule, 'Log Level': logLevel, 'PID': pid, 'TID': tid,
                       'SRC File Name': srcFileName, 'Status': status, 'Remote Host': remoteHost,
                       'Error Message': errorMsg, 'Referer': referer})
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(errors)
    #print(errors)
    return errors
