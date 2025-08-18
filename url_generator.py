# https://www.redfin.com/county/2965/VA/Fairfax-County/filter/sort=lo-days,property-type=house+townhouse,school-types=elementary+middle+high
# https://www.redfin.com/county/2965/VA/Fairfax-County/filter/sort=lo-days,property-type=house+townhouse,min-beds=1,max-beds=2,school-types=elementary+middle+high
# https://www.redfin.com/county/2965/VA/Fairfax-County/filter/sort=lo-days,property-type=house+townhouse,min-beds=1,max-beds=2,min-baths=2,school-types=elementary+middle+high
# https://www.redfin.com/county/2965/VA/Fairfax-County/filter/sort=lo-days,property-type=house+townhouse,min-beds=1,max-beds=2,min-baths=1,max-baths=2,school-types=elementary+middle+high

# fairfax county
# arlington county
# city of alexandria
# loundon county
# prince william county

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

def generate_url(url: str, filters: list):
    list_urls = []
    for filter in filters:
        beds = filter['beds']
        baths = filter['baths']
        url_filter = f"min-baths={baths[0]},max-baths={baths[1]},min-beds={beds[0]},max-beds={beds[0]}"
        new_url = f"{url},{url_filter}"
        list_urls.append(new_url)
    return list_urls

def get_urls():
    url = "https://www.redfin.com/county/2965/VA/Fairfax-County/filter/sort=lo-days,property-type=house+townhouse,school-types=elementary+middle+high"
    filters = []
    combines = [[1,2], [3,4], [5,6], [7,8]]
    filters = generate_filter(0, combines, filters)
    urls = generate_url(url, filters)
    print(urls)
    print(len(urls))

if __name__ == "__main__":
    list_urls = [
        "https://www.redfin.com/city/250/VA/Alexandria", 
        "https://www.redfin.com/county/2965/VA/Fairfax-County/filter/sort=lo-days,property-type=house+townhouse,school-types=elementary+middle+high",
        "https://www.redfin.com/city/250/VA/Alexandria"
    ]
    get_urls()
