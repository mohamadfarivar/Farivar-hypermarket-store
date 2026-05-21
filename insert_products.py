import sqlite3

connection = sqlite3.connect("database.db")

cursor = connection.cursor()


categories = [

    ("Dairy",),

    ("Snacks",),

    ("Rice",),

    ("Drinks",)

]

cursor.executemany("""

INSERT INTO categories (name)

VALUES (?)

""", categories)


products = [

    (
        "Iranian Rice",
        "$12",
        "rice-khoshbakht-india.jpg",
        "High quality Iranian rice for daily cooking.",
        1,
        10
    ),

    (
        "Cooking Oil",
        "$8",
        "oil-ladan-2litr.jpg",
        "Pure cooking oil for healthy meals.",
        2,
        10
    ),

    (
        "Fresh Milk",
        "$3",
        "milk-kale-porcharb-1litr.jpg",
        "Fresh local milk delivered daily.",
        3,
        10
    )

]

cursor.executemany("""

INSERT INTO products (
    name,
    price,
    image,
    description,
    category_id,
    stock
)

VALUES (?, ?, ?, ?, ?, ?)

""", products)

connection.commit()

connection.close()

print("Products inserted successfully.")