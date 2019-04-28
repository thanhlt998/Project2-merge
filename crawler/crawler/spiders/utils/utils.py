import re


def parse_attribute(d):
    attr = []
    for k, v in d.items():
        if type(v) is not dict:
            attr.append(k)
        else:
            attr += [f'{k}_{at}' for at in parse_attribute(v)]
    return attr


def flatten_dict(d):
    result = {}
    for k, v in d.items():
        if k.startswith('@') or k == 'identifier':
            continue
        if type(v) is dict:
            result = {**result, **{f'{k}_{k_}': v_ for k_, v_ in flatten_dict(v).items()}}
        elif type(v) is list:
            if len(v) == 1 and type(v[0]) is dict:
                result = {**result, **{f'{k}_{k_}': v_ for k_, v_ in flatten_dict(v[0]).items()}}
            else:
                result[k] = v
        else:
            if is_url(v):
                continue
            result[k] = v

    return result


def is_url(url):
    pattern = r"^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$"
    return re.match(pattern, str(url)) is not None


def format(json_object, dictionary):
    result = {}
    for k, v in json_object.items():
        if k == '@id' or k == '@type':
            continue
        key = k.split("/")[-1]

        # iter over all values in v
        value = []
        for vi in v:
            tmp = None
            if type(vi) is dict:
                if vi.get('@id') is not None:
                    if dictionary.get(vi['@id']) is not None:
                        tmp = format(dictionary[vi['@id']], dictionary)
                else:
                    tmp = re.sub("\\n\\s+", "\n ", vi['@value'].strip())
            else:
                tmp = re.sub("\\n\\s+", "\n ", vi.strip())

            if tmp not in value and tmp is not None:
                value.append(tmp)

        if len(value) == 0:
            continue
        elif len(value) == 1:
            if value[0] == '':
                continue
            result[key] = value[0]
        else:
            is_all_string = True
            for vi in value:
                if type(vi) is dict:
                    result[key] = vi
                    is_all_string = False
                    break
            if is_all_string:
                result[key] = value

    return result


def parse_json(json_list):
    dictionary = {o['@id']: o for o in json_list}

    # Find json object with JobPostingSchema
    jobs = [o for o in json_list if "http://schema.org/JobPosting" in o.get("@type")]

    return [format(job, dictionary) for job in jobs]


def date_normalize(date):
    year_month_date = re.split(r'\/-', date[:10])
    if len(year_month_date[0]) == 2:
        return '-'.join(year_month_date[::-1])
    else:
        return '-'.join(year_month_date)
