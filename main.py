import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re

header = { 
    'User-Agent': 'Mozzila/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en,q=0.9)',
}

def scrape_redfin_search_page(url):
    """Scrape a single page"""
    try:
        response = requests.get(url, headers=header)
        response.raise_for_status()

        # print(f"response {url}: {response.text}")
        soup = BeautifulSoup(response.text, 'html.parser')
        properties = []

        # print(f"response {url}: {soup.prettify()}")
        with open('response.txt', 'w') as text_file:
            text_file.write(soup.prettify())
        property_cards = soup.find_all("div", class_="bp-mobileListHomeCard")
        for card in property_cards:
            property_data = {}

            if card.find('div', class_='InlineResultStaticPlacement__adContainer'):
                continue

            property_data['address'] = card.find('div', class_ ='bp-Homecard__Address').get_text(strip=True) if card.find('div', class_='bp-Homecard__Address') else None
            property_data['price'] = card.find('span', class_='bp-Homecard__Price--value').get_text(strip=True) if card.find('span', class_='bp-Homecard__Price--value') else None

            details = card.find('div', class_='bp-Homecard__Stats')
            if details:
                bed_text = details.find('span', class_='bp-Homecard__Stats--beds').get_text(strip=True)
                bath_text = property_data['baths'] = details.find('span', class_='bp-Homecard__Stats--baths').get_text(strip=True)
                property_data['baths'] = re.sub("bed(s)*", "", bed_text)
                property_data['beds'] = re.sub("bath(s)*", "", bath_text)
                property_data['sqft'] = details.find('span', class_='bp-Homecard__LockedStat--value').get_text(strip=True).replace(',', '')
            else:
                property_data['beds'] = None
                property_data['baths'] = None
                property_data['sqft'] = None
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
    search_url = "https://www.redfin.com/city/17151/CA/San-Francisco"

    properties = scrape_redfin_area(search_url, pages=3)

    df = pd.DataFrame(properties)
    print(f"Scraped {len(df)} properties")
    df.to_csv('redfin_properties.csv', index=False)

 
