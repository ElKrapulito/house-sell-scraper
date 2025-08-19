DEFAULT_FILTERS = "sort=lo-days,property-type=house+townhouse,school-types=elementary+middle+high"
REQUEST_HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Cache-Control': 'max-age=0',
    'Referer': 'https://www.google.com/',
}
# header = { 
#     'User-Agent': 'Mozzila/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#     'Accept-Language': 'en-US,en,q=0.9)',
# }
URL_LIST = [
        "https://www.redfin.com/city/250/VA/Alexandria", 
        "https://www.redfin.com/county/2965/VA/Fairfax-County",
        "https://www.redfin.com/county/2943/VA/Arlington-County",
        "https://www.redfin.com/county/2989/VA/Loudoun-County",
        "https://www.redfin.com/county/3009/VA/Prince-William-County"
]
