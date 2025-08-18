import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
import headers
import csv

header = {
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

csv_headers = headers.CsvHeaders
json_props = headers.JsonProperties

# property_meta = ['taxableLandValue', 'taxableImprovementValue', 'yearBuilt', 'streetAddress', 'listingPrice', 'postalCode']
column_order = [
    csv_headers.PRICE.value, 
    csv_headers.TAX_PRICE.value, 
    csv_headers.TAX_YEAR.value,
    csv_headers.FULL_STREET_ADDRESS.value,
    csv_headers.STREET.value,
    csv_headers.CITY.value,
    csv_headers.STATE.value,
    csv_headers.ZIP_CODE.value,
    csv_headers.BEDS.value,
    csv_headers.BATHS.value,
    csv_headers.SQFT.value,
    csv_headers.COUNTY.value,
]


def scrape_redfin_house(property_values, url):
    """Scrape house"""
    try:
        response = requests.get(url, headers=header)
#        with open('error_response.txt', 'w') as text_file:
#                text_file.write(response.text)

        found_data = {}
        for prop in list(json_props):
            pat = re.compile(f'\\"({prop.value})\\\\\\":((\\w+)|\\\\\\"([\\w\\s]+))')
            res_tax = pat.search(response.text)
            if res_tax:
                found_data[prop.value] = res_tax.group(3) if res_tax.group(3) else res_tax.group(4) if res_tax.group(4) else None 
            else:
                found_data[prop.value] = None
        tax_land = int(found_data[json_props.TAX_LAND.value]) if found_data[json_props.TAX_LAND.value] else 0  
        tax_improve = int(found_data[json_props.TAX_IMPROVEMENT.value]) if found_data[json_props.TAX_IMPROVEMENT.value] else 0
        tax_assessed = tax_land + tax_improve
        property_values[csv_headers.TAX_PRICE.value] = tax_assessed
        property_values[csv_headers.YEAR_BUILT.value] = found_data[json_props.YEAR_BUILT.value] if found_data[json_props.YEAR_BUILT.value] else None
        property_values[csv_headers.PRICE.value] = int(found_data[json_props.PRICE.value]) if found_data[json_props.PRICE.value] else None
        property_values[csv_headers.STREET.value] = found_data[json_props.STREET.value] if found_data[json_props.STREET.value] else None
        property_values[csv_headers.TAX_YEAR.value] = found_data[json_props.TAX_YEAR.value] if found_data[json_props.TAX_YEAR.value] else None
        property_values[csv_headers.CITY.value] = found_data[json_props.CITY.value] if found_data[json_props.CITY.value] else None
        property_values[csv_headers.STATE.value] = found_data[json_props.STATE.value] if found_data[json_props.STATE.value] else None
        property_values[csv_headers.ZIP_CODE.value] = found_data[json_props.ZIP_CODE.value] if found_data[json_props.ZIP_CODE.value] else None
        property_values[csv_headers.COUNTY.value] = found_data[json_props.COUNTY.value] if found_data[json_props.COUNTY.value] else None
#        if found_data['street']:
#            format_street = found_data['street'].replace(' ', '-')
#            with open(f'response-houses/{format_street}.txt', 'w') as text_file:
#                text_file.write(response.text)

    except Exception as e:
        print(f"Error scraping house: {e}")
        return property_values 

def scrape_redfin_search_page(url):
    """Scrape a single page"""
    try:
        response = requests.get(url, headers=header)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        properties = []

        # with open('response.txt', 'w') as text_file:
        #    text_file.write(soup.prettify())
        property_cards = soup.find_all("div", class_="HomeCardContainer")
        for card in property_cards:
            property_data = {}

            if card.find('div', class_='InlineResultStaticPlacement__adContainer'):
                continue

            property_data[csv_headers.FULL_STREET_ADDRESS.value] = card.find('div', class_ ='bp-Homecard__Address').get_text(strip=True) if card.find('div', class_='bp-Homecard__Address') else None
            
            details = card.find('div', class_='bp-Homecard__Stats')
            if details:
                bed_text = details.find('span', class_='bp-Homecard__Stats--beds').get_text(strip=True)
                bath_text = property_data['baths'] = details.find('span', class_='bp-Homecard__Stats--baths').get_text(strip=True)
                property_data[csv_headers.BEDS.value] = re.sub("bed(s)*", "", bed_text) 
                property_data[csv_headers.BATHS.value] = re.sub("bath(s)*", "", bath_text)
                property_data[csv_headers.SQFT.value] = details.find('span', class_='bp-Homecard__LockedStat--value').get_text(strip=True).replace(',', '')
            else:
                property_data[csv_headers.BEDS.value] = None
                property_data[csv_headers.BATHS.value] = None
                property_data[csv_headers.SQFT.value] = None
            p = re.compile('(https:\\/\\/[a-zA-Z0-9\\.\\/\\-]+)')
            script_text = card.find('script').get_text(strip=True)
            if script_text :
                result = p.search(script_text)
                if result :
                    property_data['url'] = result.group(1)
                else :
                    property_data['url'] = None
            else:
                property_data['url'] = None
            properties.append(property_data)

        for property in properties:
            scrape_redfin_house(property, property['url']) if property['url'] else None
            time.sleep(random.uniform(1, 3))

        properties = filter(lambda property : property[csv_headers.TAX_PRICE.value] * 1.05 >= property[csv_headers.PRICE.value] if property[csv_headers.TAX_PRICE.value] and property[csv_headers.PRICE.value] else False , properties) 
        return properties
    except Exception as e:
        print(f"Error scraping page: {e}")
        return []

def scrape_redfin_area(search_url, pages=1):
    all_properties = []
    
    for page in range(1, pages + 1):
        print(f"scraping page {page}")
        paginated_url = f"{search_url}/page-{page}" if page > 1 else search_url
        properties = scrape_redfin_search_page(paginated_url)
        all_properties.extend(properties)

        time.sleep(random.uniform(2, 5))

    return all_properties;

if __name__ == "__main__" :
    start = time.clock_gettime(1)
#     search_url = "https://www.redfin.com/city/17151/CA/San-Francisco"
# https://www.redfin.com/county/2965/VA/Fairfax-County/filter/sort=lo-days,property-type=house+townhouse,school-types=elementary+middle+high/page-3
# https://www.redfin.com/county/2965/VA/Fairfax-County/filter/sort=lo-days,property-type=house+townhouse,school-types=elementary+middle+high
    search_url = "https://www.redfin.com/county/2965/VA/Fairfax-County/filter/sort=lo-days,property-type=house+townhouse,school-types=elementary+middle+high"

    properties = scrape_redfin_area(search_url, pages=9)

    df = pd.DataFrame(properties)
    print(f"Scraped {len(df)} properties")
    df = df[column_order]
    df.to_csv('redfin_properties.csv', index=False, quoting=csv.QUOTE_STRINGS)
#    search_url = "https://www.redfin.com/VA/Herndon/13922-Aviation-Pl-20171/home/191266157"
#    property_data = {}
#    scrape_redfin_house(property_data, search_url)
    end = time.clock_gettime(1)
    print(end - start)
    # scrape_redfin_house({}, "https://www.redfin.com/CA/San-Francisco/174-15th-Ave-94118/home/604751")
 
