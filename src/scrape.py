import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
import csv
import src.headers as headers
import src.constants as constants
import src.url_generator as url_generator
import src.database.housedb as hdb
import src.request_headers as rh
import config as cg
import datetime

header = constants.REQUEST_HEADER
csv_headers = headers.CsvHeaders
json_props = headers.JsonProperties

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

db = hdb.HouseDatabase("redfin.db")


def map_housedb_to_scrape_house(house):
    property = {}
    property[csv_headers.PRICE.value] = house["price"]
    property[csv_headers.TAX_PRICE.value] = house["taxAssessed"]
    property[csv_headers.TAX_YEAR.value] = house["taxYear"]
    property[csv_headers.FULL_STREET_ADDRESS.value] = house["fullAddress"]
    property[csv_headers.STREET.value] = house["address"]
    property[csv_headers.CITY.value] = house["city"]
    property[csv_headers.STATE.value] = house["state"]
    property[csv_headers.ZIP_CODE.value] = house["zipCode"]
    property[csv_headers.BEDS.value] = house["bedsCount"]
    property[csv_headers.BATHS.value] = house["bathCount"]
    property[csv_headers.SQFT.value] = house["sqft"]
    property[csv_headers.COUNTY.value] = house["county"]
    return property


def map_to_housedb(property):
    # print property information before saving
    print(f"Mapping property: {property}")
    house = {}
    house["price"] = property[csv_headers.PRICE.value]
    house["taxAssessed"] = property[csv_headers.TAX_PRICE.value]
    house["taxYear"] = property[csv_headers.TAX_YEAR.value]
    house["fullAddress"] = property[csv_headers.FULL_STREET_ADDRESS.value]
    house["address"] = property[csv_headers.STREET.value]
    house["city"] = property[csv_headers.CITY.value]
    house["state"] = property[csv_headers.STATE.value]
    house["zipCode"] = property[csv_headers.ZIP_CODE.value]
    house["bedsCount"] = property[csv_headers.BEDS.value]
    house["bathCount"] = property[csv_headers.BATHS.value]
    house["sqft"] = property[csv_headers.SQFT.value]
    house["county"] = property[csv_headers.COUNTY.value]
    house["url"] = (
        property[csv_headers.URL.value] if csv_headers.URL.value in property else ""
    )
    return house


def save_property(property):
    house = map_to_housedb(property)
    db.store_house(house)


def scrape_redfin_house(property_values, url):
    """Scrape house"""
    try:
        response = requests.get(url, headers=rh.generate_headers())
        # with open("house-response.txt", "w") as text_file:
        #     text_file.write(response.text)

        found_data = {}
        for prop in list(json_props):
            pat = re.compile(f'\\"({prop.value})\\\\\\":((\\w+)|\\\\\\"([\\w\\s]+))')
            res_tax = pat.search(response.text)
            if res_tax:
                found_data[prop.value] = (
                    res_tax.group(3)
                    if res_tax.group(3)
                    else res_tax.group(4) if res_tax.group(4) else None
                )
            else:
                found_data[prop.value] = None
        tax_land = (
            int(found_data[json_props.TAX_LAND.value])
            if found_data[json_props.TAX_LAND.value]
            else 0
        )
        tax_improve = (
            int(found_data[json_props.TAX_IMPROVEMENT.value])
            if found_data[json_props.TAX_IMPROVEMENT.value]
            else 0
        )
        tax_assessed = tax_land + tax_improve
        property_values[csv_headers.TAX_PRICE.value] = tax_assessed
        property_values[csv_headers.YEAR_BUILT.value] = (
            found_data[json_props.YEAR_BUILT.value]
            if found_data[json_props.YEAR_BUILT.value]
            else None
        )
        property_values[csv_headers.PRICE.value] = (
            int(found_data[json_props.PRICE.value])
            if found_data[json_props.PRICE.value]
            else None
        )
        property_values[csv_headers.STREET.value] = (
            found_data[json_props.STREET.value]
            if found_data[json_props.STREET.value]
            else None
        )
        property_values[csv_headers.TAX_YEAR.value] = (
            found_data[json_props.TAX_YEAR.value]
            if found_data[json_props.TAX_YEAR.value]
            else None
        )
        property_values[csv_headers.CITY.value] = (
            found_data[json_props.CITY.value]
            if found_data[json_props.CITY.value]
            else None
        )
        property_values[csv_headers.STATE.value] = (
            found_data[json_props.STATE.value]
            if found_data[json_props.STATE.value]
            else None
        )
        property_values[csv_headers.ZIP_CODE.value] = (
            found_data[json_props.ZIP_CODE.value]
            if found_data[json_props.ZIP_CODE.value]
            else None
        )
        property_values[csv_headers.COUNTY.value] = (
            found_data[json_props.COUNTY.value]
            if found_data[json_props.COUNTY.value]
            else None
        )
    except Exception as e:
        print(f"Error scraping house: {e}")
        return property_values


def scrape_redfin_page(response):
    try:
        soup = BeautifulSoup(response.text, "html.parser")
        properties = []
        existing_properties = []

        # with open("main-response.txt", "w") as text_file:
        #     text_file.write(response.text)

        property_cards = soup.find_all("div", class_="HomeCardContainer")
        if not property_cards:
            print("No property cards found!")
            return []
        for card in property_cards:
            property_data = {}

            if card.find("div", class_="InlineResultStaticPlacement__adContainer"):
                continue

            address_in_a = (
                card.find("a", class_="bp-Homecard__Address").get_text(strip=True)
                if card.find("a", class_="bp-Homecard__Address")
                else None
            )
            address_in_div = (
                card.find("div", class_="bp-Homecard__Address").get_text(strip=True)
                if card.find("div", class_="bp-Homecard__Address")
                else None
            )
            property_data[csv_headers.FULL_STREET_ADDRESS.value] = (
                address_in_div
                if address_in_div
                else address_in_a if address_in_a else None
            )
            details = card.find("div", class_="bp-Homecard__Stats")
            if details:
                bed_text = details.find(
                    "span", class_="bp-Homecard__Stats--beds"
                ).get_text(strip=True)
                bath_text = property_data["baths"] = details.find(
                    "span", class_="bp-Homecard__Stats--baths"
                ).get_text(strip=True)
                property_data[csv_headers.BEDS.value] = re.sub("bed(s)*", "", bed_text)
                property_data[csv_headers.BATHS.value] = re.sub(
                    "bath(s)*", "", bath_text
                )
                property_data[csv_headers.SQFT.value] = (
                    details.find("span", class_="bp-Homecard__LockedStat--value")
                    .get_text(strip=True)
                    .replace(",", "")
                )
            else:
                property_data[csv_headers.BEDS.value] = None
                property_data[csv_headers.BATHS.value] = None
                property_data[csv_headers.SQFT.value] = None
            p = re.compile("(https:\\/\\/[a-zA-Z0-9\\.\\/\\-]+)")
            script_text = card.find("script").get_text(strip=True)
            if script_text:
                result = p.search(script_text)
                if result:
                    property_data[csv_headers.URL.value] = result.group(1)
                else:
                    property_data[csv_headers.URL.value] = None
            else:
                property_data[csv_headers.URL.value] = None
            # TODO: search for more values than just address
            house = db.get_house_by_address(
                property_data[csv_headers.FULL_STREET_ADDRESS.value].split(",")[0]
            )
            if len(house) <= 0 or house == None:
                print("adding house to be scrapped")
                properties.append(property_data)
            else:
                print("found existing home")
                existing_properties.append(house)
        for property in properties:
            (
                scrape_redfin_house(property, property[csv_headers.URL.value])
                if property[csv_headers.URL.value]
                else None
            )
            time.sleep(random.uniform(1, 3))
            house = map_to_housedb(property)
            try:
                save_property(property)
            except Exception as e:
                print(f"error saving {e}")

        print(existing_properties)
        existing_properties = list(
            map(map_housedb_to_scrape_house, existing_properties)
        )
        return properties + existing_properties
    except Exception as e:
        print(f"error scraping page: {e}")
        return []


def scrape_redfin_search_page(url: str, page_count: int = 1, total_page: int = 1):
    if page_count > total_page:
        return []
    try:
        new_url = f"{url}/page-{page_count}" if page_count > 1 else url
        print(f"scraping this url: {new_url}")
        response = requests.get(new_url, headers=rh.generate_headers())
        response.raise_for_status()
        pages_count = 1
        if page_count == 1:
            page = BeautifulSoup(response.text, "html.parser")
            page_home_count = (
                page.find("div", class_="descriptionSummary")
                .find("div", class_="homes")
                .get_text(strip=True)
            )
            page_home_count = int(page_home_count.split(" ")[0].replace(",", ""))
            print(f"Home count is: {page_home_count}")
            if page_home_count > 41:
                pages_count = page.find_all("a", class_="PageNumbers__page")
                pages_count = (
                    pages_count[len(pages_count) - 1]
                    .find("span", class_="ButtonLabel")
                    .get_text(strip=True)
                )
                pages_count = int(pages_count) if pages_count else 1
                total_page = pages_count
                print(f"total pages count: {pages_count}")

        properties = scrape_redfin_page(response)
        time.sleep(random.uniform(1, 3))
        more_properties = scrape_redfin_search_page(url, page_count + 1, total_page)
        more_properties = more_properties if more_properties else []
        return properties + more_properties
    except Exception as e:
        print(f"Error scraping page: {e}")
        return []


def filter_properties(properties: list):
    return filter(
        lambda property: (
            property[csv_headers.TAX_PRICE.value] * cg.RATE
            >= property[csv_headers.PRICE.value]
            if property[csv_headers.TAX_PRICE.value]
            and property[csv_headers.PRICE.value]
            else False
        ),
        properties,
    )


def scrape_redfin_area(list_urls: list):
    all_properties = []
    for url in list_urls:
        print(f"Scrapping URL: {url}")
        properties = scrape_redfin_search_page(url)
        properties = filter_properties(properties) if properties else []
        properties = [elem for elem in properties if elem not in all_properties]
        all_properties.extend(properties)
        time.sleep(random.uniform(2, 5))

    return all_properties


def main():
    start = time.clock_gettime(time.CLOCK_REALTIME)
    list_urls = url_generator.get_default_urls()
    # Print number of URLs generated
    print(f"Generated {len(list_urls)} URLs")

    properties = scrape_redfin_area(list_urls)

    df = pd.DataFrame(properties)
    print(f"Scraped {len(df)} properties")
    df = df[column_order]

    date = datetime.date(2025, 1, 1).today()
    df.to_csv(
        f"reports/{date}-redfin-properties.csv", index=False, quoting=csv.QUOTE_STRINGS
    )
    end = time.clock_gettime(time.CLOCK_REALTIME)
    print(end - start)


if __name__ == "__main__":
    print("hello")
