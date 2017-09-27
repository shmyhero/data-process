

def flatten(x):
    """
    flatten the list
    :param x:
    :return:
    """
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result


def list_to_hash(lst):
    """
    convert list to hash
    :param lst:
    :return:
    """
    result = {}
    for record in lst:
        result[record[0]] = record[1]
    return result


def hash_to_list(dic, order_by_key = False):
    """
    convert hash to list
    :param dic:
    :return:
    """
    result = []
    for key, value in dic.iteritems():
        result.append([key, value])
    if order_by_key:
        result.sort(key=lambda x: x[0])
    return result


if __name__ == '__main__':
    d =  list_to_hash([['a',1],['b',2]])
    print d
    print hash_to_list(d)
