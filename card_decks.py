import sqlite3
import base64
import io

from PIL import Image

class DuplicateRecordError(Exception):
    pass

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect("card_decks.db")
    cursor = conn.cursor()

    # Create Types table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Themes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS themes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Games table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Cities table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Countries table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS countries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Numbers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS numbers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Collections table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS collections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Manufacturers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS manufacturers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Decks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS decks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_id INTEGER NOT NULL,
        number_id INTEGER NOT NULL,
        theme_id INTEGER NOT NULL,
        game_id INTEGER NOT NULL,
        city_id INTEGER NOT NULL,
        country_id INTEGER NOT NULL,
        collection_id INTEGER NOT NULL,
        manufacturer_id INTEGER NOT NULL,
        images TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (type_id) REFERENCES types (id),
        FOREIGN KEY (number_id) REFERENCES numbers (id),
        FOREIGN KEY (theme_id) REFERENCES themes (id),
        FOREIGN KEY (game_id) REFERENCES games (id),
        FOREIGN KEY (city_id) REFERENCES cities (id),
        FOREIGN KEY (country_id) REFERENCES countries (id),
        FOREIGN KEY (collection_id) REFERENCES collections (id),
        FOREIGN KEY (manufacturer_id) REFERENCES manufacturers (id)
    )
    """)

    conn.commit()
    conn.close()

# Helper functions to interact with the database
def add_record(table, name):
    try:
        conn = sqlite3.connect("card_decks.db")
        cursor = conn.cursor()

        allowed_tables = ["types", "themes", "games", "cities", "countries", "collections", "manufacturers", "numbers"]
        if table not in allowed_tables:
            raise ValueError(f"Invalid table name: {table}")

        name = name.strip().capitalize()  # Remove whitespace and capitalize

        # Case-insensitive check for existing record
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE LOWER(name) = LOWER(?)", (name,))
        count = cursor.fetchone()[0]

        if count > 0:
            print(f"Record '{name}' already exists in table '{table}'.")
            raise DuplicateRecordError(f"Record '{name}' already exists in table '{table}'.")

        cursor.execute(f"INSERT INTO {table} (name) VALUES (?)", (name,))
        conn.commit()
        print(f"Record '{name}' added to table '{table}' successfully.")
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        return False
    except ValueError as e:
        print(e)
        return False
    except DuplicateRecordError as e: # Catch DuplicateRecordError here
        print(e)
        return False
    finally:
        if conn:
            conn.close()
def get_records(table):
    try:
        conn = sqlite3.connect("card_decks.db")
        cursor = conn.cursor()

        # Sanitize the table name
        allowed_tables = ["types", "themes", "games", "cities", "countries", "collections", "manufacturers", "numbers"]
        if table not in allowed_tables:
            raise ValueError(f"Invalid table name: {table}")

        cursor.execute(f"SELECT id, name FROM {table}") # Select only necessary columns
        records = cursor.fetchall()
        return records
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []  # Return an empty list in case of error
    except ValueError as e:
        print(e)
        return []
    finally:
        if conn:
            conn.close()

def delete_record(table, record_id):
    try:
        conn = sqlite3.connect("card_decks.db")
        cursor = conn.cursor()

        # Sanitize the table name
        allowed_tables = ["types", "themes", "games", "cities", "countries", "collections", "manufacturers", "numbers"]
        if table not in allowed_tables:
            raise ValueError(f"Invalid table name: {table}")

        # Parameterized query for record_id (already correctly implemented)
        cursor.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
        conn.commit()
        print(f"Record with ID '{record_id}' deleted from table '{table}' successfully.")
        return True # Return true on success
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        return False # Return false on error
    except ValueError as e:
        print(e)
        return False
    finally:
        if conn:
            conn.close()

def add_deck(type_id, number_id, theme_id, game_id, city_id, country_id, collection_id, manufacturer_id, description, image_paths):
    try:
        conn = sqlite3.connect("card_decks.db")
        cursor = conn.cursor()

        image_data_list = []
        for path in image_paths:
            try:
                if isinstance(path, bytes):
                    image = Image.open(io.BytesIO(path))
                else:
                    image = Image.open(path)

                # Create thumbnail
                image.thumbnail((200, 200))  # Resize to max 200x200 pixels
                
                # Save thumbnail to in-memory buffer
                thumbnail_buffer = io.BytesIO()
                image.save(thumbnail_buffer, format="JPEG") # Save as JPEG for smaller size
                thumbnail_bytes = thumbnail_buffer.getvalue()

                # Encode to base64
                thumbnail_base64 = base64.b64encode(thumbnail_bytes).decode("utf-8")

                image_data_list.append(thumbnail_base64)
            except FileNotFoundError:
                print(f"Error: Image file not found: {path}")
                return False
            except Exception as e:
                print(f"Error processing image: {e}")
                return False

        images_string = ",".join(image_data_list)

        cursor.execute(
            """
            INSERT INTO decks (type_id, number_id, theme_id, game_id, city_id, country_id, collection_id, manufacturer_id, description, images)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (type_id, number_id, theme_id, game_id, city_id, country_id, collection_id, manufacturer_id, description, images_string)
        )
        conn.commit()
        print("Deck added successfully")
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_decks():
    conn = sqlite3.connect("card_decks.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT decks.id, types.name, numbers.name, themes.name, games.name, cities.name, countries.name, collections.name, manufacturers.name, decks.description, decks.images
        FROM decks
        JOIN types ON decks.type_id = types.id
        JOIN numbers ON decks.number_id = numbers.id
        JOIN themes ON decks.theme_id = themes.id
        JOIN games ON decks.game_id = games.id
        JOIN cities ON decks.city_id = cities.id
        JOIN countries ON decks.country_id = countries.id
        JOIN collections ON decks.collection_id = collections.id
        JOIN manufacturers ON decks.manufacturer_id = manufacturers.id
        """
    )
    decks = cursor.fetchall()
    conn.close()
    return decks

def get_deck_by_id(deck_id):
    try:
        # conn = sqlite3.connect('card_decks.db')
        # cursor = conn.cursor()
        # cursor.execute("SELECT * FROM decks WHERE id=?", (deck_id,))
        # deck = cursor.fetchone()
        # conn.close()
        # return deck

        conn = sqlite3.connect('card_decks.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT decks.id, types.name, numbers.name, themes.name, games.name, cities.name, countries.name, collections.name, manufacturers.name, decks.description, decks.images
            FROM decks
            JOIN types ON decks.type_id = types.id
            JOIN numbers ON decks.number_id = numbers.id
            JOIN themes ON decks.theme_id = themes.id
            JOIN games ON decks.game_id = games.id
            JOIN cities ON decks.city_id = cities.id
            JOIN countries ON decks.country_id = countries.id
            JOIN collections ON decks.collection_id = collections.id
            JOIN manufacturers ON decks.manufacturer_id = manufacturers.id
            WHERE decks.id = ?
        """, (deck_id,))
        deck = cursor.fetchone()
        conn.close()
        return deck
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

def filter_decks(type_id=None, number_id=None, theme_id=None, game_id=None, city_id=None, country_id=None, collection_id=None, manufacturer_id=None):
    conn = sqlite3.connect("card_decks.db")
    cursor = conn.cursor()

    query = """
        SELECT decks.id, types.name, numbers.name, themes.name, games.name, cities.name, countries.name, collections.name, manufacturers.name, decks.description, decks.images
        FROM decks
        JOIN types ON decks.type_id = types.id
        JOIN numbers ON decks.number_id = numbers.id
        JOIN themes ON decks.theme_id = themes.id
        JOIN games ON decks.game_id = games.id
        JOIN cities ON decks.city_id = cities.id
        JOIN countries ON decks.country_id = countries.id
        JOIN collections ON decks.collection_id = collections.id
        JOIN manufacturers ON decks.manufacturer_id = manufacturers.id
    """
    filters = []
    params = []

    if type_id:
        filters.append("decks.type_id = ?")
        params.append(type_id)
    if number_id:
        filters.append("decks.number_id = ?")
        params.append(number_id)
    if theme_id:
        filters.append("decks.theme_id = ?")
        params.append(theme_id)
    if game_id:
        filters.append("decks.game_id = ?")
        params.append(game_id)
    if city_id:
        filters.append("decks.city_id = ?")
        params.append(city_id)
    if country_id:
        filters.append("decks.country_id = ?")
        params.append(country_id)
    if collection_id:
        filters.append("decks.collection_id = ?")
        params.append(collection_id)
    if manufacturer_id:
        filters.append("decks.manufacturer_id = ?")
        params.append(manufacturer_id)

    if filters:
        query += " WHERE " + " AND ".join(filters)

    cursor.execute(query, params)
    decks = cursor.fetchall()
    conn.close()
    return decks

def get_deck_names(filtered_decks):
    deck_names = []
    for deck in filtered_decks:
        deck_name = f"{deck[0]}. Tipo: {deck[1]}. {deck[2]} cartas. Tema: {deck[3]}. Cidade: {deck[5]}. País: {deck[6]}. Coleção: {deck[7]}. Fabricante: {deck[8]}"
        deck_names.append(deck_name)
    return deck_names

def edit_deck(deck_id, type_id, number_id, theme_id, game_id, city_id, country_id, collection_id, manufacturer_id, description, images):
    try:
        conn = sqlite3.connect('card_decks.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE decks SET
            type_id = ?, number_id = ?, theme_id = ?, game_id = ?, city_id = ?,
            country_id = ?, collection_id = ?, manufacturer_id = ?, description = ?, images = ?
            WHERE id = ?
        """, (type_id, number_id, theme_id, game_id, city_id, country_id, collection_id, manufacturer_id, description, ",".join([image.decode('latin-1') if isinstance(image, bytes) else image for image in images]), deck_id))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
