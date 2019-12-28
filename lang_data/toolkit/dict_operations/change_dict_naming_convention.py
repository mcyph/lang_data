
def camel_case(s):
    if s[0].isupper():
        return s

    output = ''.join(x for x in s.title() if x.isalnum())
    return output[0].lower() + output[1:]


def change_dict_naming_convention(o, convert_function):
    """
    See also solution by jllopezpino:
    https://stackoverflow.com/questions/11700705/python-recursively-replace-character-in-keys-of-nested-dictionary

    Convert a nested dictionary from one convention to another.
    Args:
        d (dict): dictionary (nested or not) to be converted.
        convert_function (func): function that takes the string in one convention and returns it in the other one.
    Returns:
        Dictionary with the new keys.
    """

    if isinstance(o, dict):
        new_v = {}

        for k, v in o.items():
            new_v[convert_function(k)] = change_dict_naming_convention(v, convert_function)

    elif isinstance(o, list):
        new_v = list()

        for x in o:
            new_v.append(
                change_dict_naming_convention(x, convert_function)
            )
    elif isinstance(o, tuple):
        new_v = list()

        for x in o:
            new_v.append(
                change_dict_naming_convention(x, convert_function)
            )
        new_v = tuple(new_v)
    else:
        new_v = o

    return new_v


def keys_camel_cased(D):
    return change_dict_naming_convention(D, camel_case)

