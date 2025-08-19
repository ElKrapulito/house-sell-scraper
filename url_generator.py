import constants

default_filters = constants.DEFAULT_FILTERS

def generate_filter(index, combines, filters):
    filter = {}
    filter2 = {}
    if len(combines) - 1 == index:
        return filters
    if index < 0:
        return filters
    if index == 0:
        filter['beds'] = combines[index]
        filter['baths'] = combines[index]
        filters.append(filter)
        return generate_filter(index + 1, combines, filters)
    filter['beds'] = combines[index]
    filter['baths'] = combines[index]
    filters.append(filter)
    filter2['beds'] = filter['beds']
    filter2['baths'] = combines[index - 1]
    filters.append(filter2)
    return generate_filter(index + 1, combines, filters)

def make_url(url: str, filters: list):
    list_urls = []
    for filter in filters:
        beds = filter['beds']
        baths = filter['baths']
        url_filter = f"/filter/{default_filters},min-baths={baths[0]},max-baths={baths[1]},min-beds={beds[0]},max-beds={beds[1]}"
        new_url = f"{url}{url_filter}"
        list_urls.append(new_url)
    return list_urls

def generate_urls(list_urls):
    combines = [[1,2], [3,4], [5,6], [7,8]]
    filters = generate_filter(0, combines, [])
    new_list = []
    for url in list_urls:
        urls = make_url(url, filters)
        new_list = new_list + urls
    return new_list

def get_default_urls():
    list_urls = constants.URL_LIST    
    return generate_urls(list_urls)

if __name__ == "__main__":
    print(get_default_urls())
