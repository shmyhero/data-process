
def string_fetch(string, first, last):
    try:
        if first == '':
            start = 0
        else:
            start = string.index(first) + len(first)
        if last == '':
            end = len(string)
        else:
            end = string.index(last, start)
        return string[start:end]
    except ValueError:
        return ''


def all_number_p(string):
    for c in string:
        if '0' <= c <= '9':
            pass
        else:
            return False
    return True
