import sqlite3
from typing import List, Dict, Optional, Tuple

class HouseDatabase:
    def __init__(self, db_name: str = "houses.db"):
        self.db_name = db_name
        self._init_database()
    
    def _init_database(self):
        """Initialize the database and create table if it doesn't exist"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS houses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fullAddress TEXT NULL,
                    address TEXT NOT NULL,
                    city TEXT NOT NULL,
                    zipCode TEXT NULL,
                    county TEXT NOT NULL,
                    state TEXT NOT NULL,
                    price DECIMAL NOT NULL,
                    taxAssessed DECIMAL NOT NULL,
                    bathCount INTEGER NOT NULL DEFAULT 0, 
                    bedsCount INTEGER NOT NULL DEFAULT 0,
                    taxYear TEXT NOT NULL,
                    sqft TEXT NOT NULL,
                    url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def store_house(self, house_data: Dict[str, str]) -> int:
        """
        Store a house record in the database
        
        Args:
            house_data: Dictionary containing house information with keys:
                       houseNumber, address, city, zipCode, county, state
        
        Returns:
            int: The ID of the inserted record
        """
        required_fields = ['fullAddress', 'address', 'city', 'zipCode', 'county', 'state', 'price', 'taxAssessed', 'taxYear', 'url']
        
        # Validate required fields
        for field in required_fields:
            if field not in house_data:
                raise ValueError(f"Missing required field: {field}")
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO houses (
                    fullAddress, 
                    address, 
                    city, 
                    zipCode, 
                    county, 
                    state,
                    price,
                    taxAssessed,
                    bathCount,
                    bedsCount,
                    taxYear,
                    sqft,
                    url
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
            ''', (
                house_data['fullAddress'],
                house_data['address'],
                house_data['city'],
                house_data['zipCode'],
                house_data['county'],
                house_data['state'],
                house_data['price'],
                house_data['taxAssessed'],
                house_data['bathCount'],
                house_data['bedsCount'],
                house_data['taxYear'],
                house_data['sqft'],
                house_data['url']
            ))
            conn.commit()
            return cursor.lastrowid or 0
    
    def get_house_by_id(self, house_id: int) -> Optional[Dict]:
        """Retrieve a house by its ID"""
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM houses WHERE id = ?', (house_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def get_all_houses(self) -> List[Dict]:
        """Retrieve all houses from the database"""
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM houses ORDER BY id')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def search_houses(self, **filters) -> List[Dict]:
        """
        Search for houses based on various criteria
        
        Args:
            **filters: Keyword arguments for filtering (e.g., city="New York", state="NY")
        
        Returns:
            List of matching house records
        """
        if not filters:
            return self.get_all_houses()
        
        query = "SELECT * FROM houses WHERE "
        conditions = []
        params = []
        
        for field, value in filters.items():
            conditions.append(f"{field} LIKE ?")
            params.append(f"%{value}%")

        query += " AND ".join(conditions) + " ORDER BY id"

        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def update_house(self, house_id: int, update_data: Dict[str, str]) -> bool:
        """
        Update a house record

        Args:
            house_id: ID of the house to update
            update_data: Dictionary of fields to update

        Returns:
            bool: True if update was successful, False otherwise
        """
        if not update_data:
            return False

        set_clause = ", ".join([f"{key} = ?" for key in update_data.keys()])
        params = list(update_data.values())
        params.append(f"{house_id}")

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE houses 
                SET {set_clause}
                WHERE id = ?
            ''', params)
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_house(self, house_id: int) -> bool:
        """Delete a house record by ID"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM houses WHERE id = ?', (house_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_houses_by_city(self, city: str) -> List[Dict]:
        """Get all houses in a specific city"""
        return self.search_houses(city=city)
    
    def get_houses_by_state(self, state: str) -> List[Dict]:
        """Get all houses in a specific state"""
        return self.search_houses(state=state)
    
    def get_houses_by_zip_code(self, zip_code: str) -> List[Dict]:
        """Get all houses with a specific zip code"""
        return self.search_houses(zipCode=zip_code)
    def get_house_by_address(self, address: str) -> Dict: 
        house_list = self.search_houses(fullAddress=address)
        if house_list.__len__() <= 0:
            return {} 
        else:
            return house_list[0]

# Example usage and demonstration
def main():
    # Initialize the database
    db = HouseDatabase()
    
    # Example house data
    sample_houses = [
        {
            'houseNumber': '123',
            'address': 'Main Street',
            'city': 'New York',
            'zipCode': '10001',
            'county': 'New York County',
            'state': 'NY'
        },
        {
            'houseNumber': '456',
            'address': 'Oak Avenue',
            'city': 'Los Angeles',
            'zipCode': '90001',
            'county': 'Los Angeles County',
            'state': 'CA'
        },
        {
            'houseNumber': '789',
            'address': 'Pine Road',
            'city': 'Chicago',
            'zipCode': '60601',
            'county': 'Cook County',
            'state': 'IL'
        }
    ]
    
    # Store sample houses
    print("Storing sample houses...")
    for house in sample_houses:
        house_id = db.store_house(house)
        print(f"Stored house with ID: {house_id}")
    
    # Retrieve all houses
    print("\nAll houses in database:")
    all_houses = db.get_all_houses()
    for house in all_houses:
        print(f"ID: {house['id']}, Address: {house['houseNumber']} {house['address']}, {house['city']}, {house['state']} {house['zipCode']}")
    
    # Search for houses in a specific city
    print("\nHouses in New York:")
    ny_houses = db.get_houses_by_city("New York")
    for house in ny_houses:
        print(f"ID: {house['id']}, Address: {house['houseNumber']} {house['address']}")
    
    # Get a specific house by ID
    print("\nGetting house with ID 1:")
    house = db.get_house_by_id(1)
    if house:
        print(f"House 1: {house['houseNumber']} {house['address']}, {house['city']}")
    
    # Search with multiple criteria
    print("\nSearching for houses in CA state:")
    ca_houses = db.search_houses(state="CA")
    for house in ca_houses:
        print(f"CA House: {house['houseNumber']} {house['address']}, {house['city']}")

if __name__ == "__main__":
    main()
