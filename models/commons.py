def clean_dict(mydict):
    for key, value in list(mydict.items()):
        if value is None:
            del mydict[key]
        elif isinstance(value, dict):
            clean_dict(value)
    return mydict
