import sqlite3

con =  sqlite3.connect('test.db')
db = con.cursor()
print("Database connected!")


db.execute("CREATE TABLE 'users' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL, 'cash' NUMERIC NOT NULL DEFAULT 20 , 'admin' INTEGER NOT NULL DEFAULT 0)")

db.execute("CREATE TABLE 'inventory' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'product' TEXT, 'description' TEXT, 'cost' NUMERIC, 'price' NUMERIC, 'img_url' TEXT, 'quantity' INTEGER)")

db.execute("CREATE TABLE 'history' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'user_id' INTEGER, 'product' TEXT, 'units' INTEGER, 'sale' NUMERIC, 'cash_after' NUMERIC, 'transacted' date DEFAULT CURRENT_DATE )")

db.execute("CREATE UNIQUE INDEX 'username' ON 'users' ('username') WHERE 1")

print("Tables created")

candles = [(1, "Navy Blue", "Navy blue layered nordic candle ~ Ocean scented", 1.99, 4.99, "https://cdn.shopify.com/s/files/1/0885/7094/products/navy-blue-layered-nordic-candle-DSC_3956_2000x.jpg?v=1537476740", 20),
		   (2, "Teal", "Rustic teal nordic candle", 1.99, 4.99, "https://cdn.shopify.com/s/files/1/0885/7094/products/teal-rustic-3x4-pillar-candle-nordic-candle-DSC_3866_2000x.jpg?v=1537641718", 20),
		   (3, "Peach", "Summer peach pillar candle", 2.99, 5.99, "http://aws-website-cloudateliercom-f9jlz.s3-website-us-east-1.amazonaws.com/az-img/3L1-0715SPE.v003.jpg", 20),
		   (4, "Rose", "Small rose artesian pillar candle", 1.00, 3.99, "https://cdn.shopify.com/s/files/1/0304/4437/products/104113-00.jpg?v=1527466949", 20),
		   (5, "Gray", "Small gray artesian pillar candle", 1.00, 3.99, "https://cdn.shopify.com/s/files/1/0304/4437/products/104016-00.jpg?v=1527466949", 20)	
		  ]

print("Candles ready")

db.executemany("INSERT INTO inventory VALUES (?,?,?,?,?,?,?)", candles)
con.commit()

print("Candles added to DatBase!!!")

con.close()