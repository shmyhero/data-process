from utils.stringhelper import string_fetch


def parse_query_string(query_string):
    content = string_fetch(query_string, '?', '')
    items = content.split('&')
    result = {}
    for item in items:
        if '=' in item:
            (key, value) = item.split('=')
            result[key] = value
    return result


