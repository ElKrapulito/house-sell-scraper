from enum import Enum

class CsvHeaders(Enum):
    PRICE = 'price'
    TAX_PRICE = 'tax_price'
    TAX_YEAR = 'tax_year'
    FULL_STREET_ADDRESS = 'street_address_raw' 
    STREET = 'street_address'
    CITY = 'city'
    STATE = 'state'
    ZIP_CODE = 'zip_code'
    BEDS = 'bedrooms_count'
    BATHS = 'bathrooms_count'
    SQFT = 'living_area'
    STATUS = 'property_status'
    DAYS_ON = 'days_on_market'
    COUNTY = 'county'
