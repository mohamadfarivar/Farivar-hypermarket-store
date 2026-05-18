import sqlite3

connection = sqlite3.connect("database.db")

cursor = connection.cursor()

products = [

    (
        "Iranian Rice",
        "$12",
        "rice-khoshbakht-india.jpg",
        "High quality Iranian rice for daily cooking."
    ),

    (
        "Cooking Oil",
        "$8",
        "oil-ladan-2litr.jpg",
        "Pure cooking oil for healthy meals."
    ),

    (
        "Fresh Milk",
        "$3",
        "milk-kale-porcharb-1litr.jpg",
        "Fresh local milk delivered daily."
    )

]

cursor.executemany("""

INSERT INTO products (
    name,
    price,
    image,
    description
)

VALUES (?, ?, ?, ?)

""", products)

connection.commit()

connection.close()

print("Products inserted successfully.")