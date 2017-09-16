

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


if __name__ == '__main__':
    print list_to_hash([['a',1],['b',2]])
