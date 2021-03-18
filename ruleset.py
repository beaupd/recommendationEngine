import psycopg2
from random import choice
from time import perf_counter

c = psycopg2.connect("dbname=postgres user=postgres password=admin") # postgresql connection edit naar jouw gegevens

def getRows(conn, table, values=None): # functie om rows op te vragen op basis van parameters
    cur = conn.cursor()
    if values:
        cur.execute(f"SELECT {', '.join(values)} from {table}")
    else:
        cur.execute(f"SELECT * from {table}")
    rows = cur.fetchall()
    cur.close()
    return rows

class CollaborativeFiltering(): # Collaborative filtering

    def __init__(self, conn):
        self.conn = conn

    def recommendProducts(self, product_id): # beveel een product aan
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM collaboratives WHERE '{product_id}'=ANY(products)") # kijken waar de gegeven product_id voorkomt in de array
        rows = cur.fetchall()
        res = {
            "products": list(filter(lambda p: p != product_id, [item for sublist in [r[1] for r in rows] for item in sublist])) # dit is een mooie "one-liner" die zowel een list of lists flattened en de gegeven product_id eruit filtert
        }
        return res

    def populateTable(self): # haal de data uit de tabellen en stop ze in de eerder gemaakte tabel
        rows = getRows(self.conn, "profiles_previously_viewed")
        cur = self.conn.cursor()
        print(f"Found {len(rows)} rows, inserting...")
        start_all = perf_counter()
        for idx, r in enumerate(rows):# loop door alle opgevraagde rows
            if c:# als de column niet leeg is
                # hieronder de sql insert code om een row aan te maken of van een row met dezelfde "profid" de array aan te passen(append) 
                cur.execute(f"INSERT INTO collaboratives(profid, products, length) VALUES ('{r[0]}', ARRAY['{r[1]}'], 1) ON CONFLICT (profid) DO UPDATE SET products = array_append((SELECT products from collaboratives where profid='{r[0]}'), '{r[1]}'), length = array_length(array_append((SELECT products from collaboratives where profid='{r[0]}'), '{r[1]}'), 1);")
            if idx % 500000 == 0 and idx != 0:# x aantal tussentijdse tijdsberekening en commit
                temp = perf_counter()
                print(f"On row {idx}, current time is {temp - start_all}s estimated time is {((temp-start_all)/idx)*len(rows)}s\ncommiting...")
                self.conn.commit()
        self.conn.commit()
        eind_whole = perf_counter()
        print(f"Done, total took {eind_whole - start_all} seconds...")
        print("Cleaning up data...")
        start = perf_counter()
        cur.execute(f"DELETE FROM collaboratives WHERE length = 1")# bij rows waar de array maar 1 in heeft heeft het geen zin om te kijken voor aanbevelingen omdat het gegeven product de enige aanwezige is in de array
        self.conn.commit()
        eind = perf_counter()
        print(f"Done, took {eind - start}s")
        cur.close()

    def createTable(self): # maak de nieuwe tabel aan voor de gegevens
        cur = self.conn.cursor()
        cur.execute("DROP TABLE IF EXISTS collaboratives CASCADE")
        cur.execute("""
            CREATE TABLE collaboratives (
                profid VARCHAR PRIMARY KEY,
                products VARCHAR[],
                length INT,
                FOREIGN KEY (profid) REFERENCES profiles (id)
            );
        """)
        self.conn.commit()
        cur.close()
        

class EqualContentFiltering(): # Content-Based filtering

    def __init__(self, conn):
        self.conn = conn

    def recommendProducts(self, product_id): # beveel een product aan
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM equals WHERE '{product_id}'=ANY(products)") # kijken waar de gegeven product_id voorkomt in de array
        rows = cur.fetchall()
        rows.sort(key = lambda rows: rows[-1]) # soorteren op groote array zodat we de kleinste kunnen pakken dit is meestal het meest overeenkomig qua eigenschappen.
        res = {
            "products": list(filter(lambda p: p != product_id, rows[0][2]))# product id eruit filteren
        }
        return res

    def populateTable(self): # haal de data uit de tabellen en stop ze in de eerder gemaakte tabel
        values = ["id", "brand", "type", "category", "subcategory", "subsubcategory", "targetaudience", "sellingprice", "deal"]
        
        rows = getRows(self.conn, "products", values) 
        cur = self.conn.cursor()
        print(f"Found {len(rows)} rows, inserting...")
        start_all = perf_counter()
        for idx, r in enumerate(rows): # loop door alle opgevraagde rows
            for i, c in enumerate(r[1:], 1): # loop door alle columns behalve de eerste want het id gebruiken we in de niewe tabel als identificator
                if c:# als de column niet leeg is
                    p = str(c).replace("'", "") # sommige columns hebben quote er in en dat geeft een error
                    p_id = r[0].replace("'", "") # sommige columns hebben quote er in en dat geeft een error
                    # hieronder de sql insert code om een row aan te maken of van een row met dezelfde "value" de array aan te passen(append) 
                    cur.execute(f"INSERT INTO equals(keyfield, value, products, length) VALUES ('{values[i]}', '{p}', ARRAY['{p_id}'], 1) ON CONFLICT (value) DO UPDATE SET products = array_append((SELECT products from equals where value='{p}'), '{p_id}'), length = array_length(array_append((SELECT products from equals where value='{p}'), '{p_id}'), 1);")
            if idx % 1000 == 0 and idx != 0: # x aantal executes committen vooral om efficientie te testen en om een coole tussentijdse tijden te berekenen
                temp = perf_counter()
                print(f"On row {idx}, current time is {temp - start_all}s estimated time is {((temp-start_all)/idx)*len(rows)}s\ncommiting...")
                self.conn.commit()
        self.conn.commit()
        eind_whole = perf_counter()
        print(f"Done, total took {eind_whole - start_all} seconds...")
        cur.close()
               
    def createTable(self): # maak de nieuwe tabel aan voor de gegevens
        cur = self.conn.cursor()
        cur.execute("DROP TABLE IF EXISTS equals CASCADE")
        cur.execute("""
            CREATE TABLE equals (
                keyfield VARCHAR,
                value VARCHAR PRIMARY KEY,
                products VARCHAR[],
                length INT
            );
        """)
        self.conn.commit()
        cur.close()

recommendEngine = EqualContentFiltering(c)
# recommendEngine.createTable()
# recommendEngine.populateTable()
# print(choice(equalEngine.recommendProducts("29454")))
products = recommendEngine.recommendProducts("9945")["products"]
print(choice(products))
