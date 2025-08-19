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
    YEAR_BUILT = 'year_built'
    URL = 'url'

# property_meta = ['taxableLandValue', 'taxableImprovementValue', 'yearBuilt', 'streetAddress', 'listingPrice', 'postalCode']
class JsonProperties(Enum):
    TAX_LAND = 'taxableLandValue'
    TAX_IMPROVEMENT = 'taxableImprovementValue'
    TAX_YEAR = 'rollYear'
    YEAR_BUILT = 'yearBuilt'
    STREET = 'streetAddress'
    PRICE = 'listingPrice'
    ZIP_CODE = 'postalCode'
    STATE = 'state'
    COUNTY = 'countyName'
    CITY = 'city'

