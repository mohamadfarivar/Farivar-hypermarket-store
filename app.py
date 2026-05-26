from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

import os

import sqlite3

import psycopg2

from psycopg2.extras import RealDictCursor


app = Flask(__name__)
app.secret_key = "super-secret-key"

UPLOAD_FOLDER = "static/images"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def get_sqlite_connection():

    connection = sqlite3.connect("database.db")

    connection.row_factory = sqlite3.Row

    return connection


def get_db_connection():

    connection = psycopg2.connect(

        host="localhost",

        database="farivar_store",

        user="postgres",

        password="Farivar1123@#",

        cursor_factory=RealDictCursor

    )

    return connection


@app.route("/")
def home():

    search = request.args.get("search", "")

    category = request.args.get("category", "")

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM categories"
    )

    categories = cursor.fetchall()

    query = "SELECT * FROM products WHERE 1=1"

    params = []

    if search:

        query += " AND name LIKE %s"

        params.append(f"%{search}%")

    if category:

        query += " AND category_id = %s"

        params.append(category)

    cursor.execute(
        query,
        params
    )

    products = cursor.fetchall()

    cursor.close()

    return render_template(
        "index.html",
        products=products,
        categories=categories
    )



@app.route("/product/<int:product_id>")
def product_detail(product_id):

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE id = %s",
        (product_id,)
    )

    product = cursor.fetchone()

    cursor.execute("""

    SELECT
        reviews.*,
        users.username

    FROM reviews

    JOIN users
    ON reviews.user_id = users.id

    WHERE product_id = ?

    ORDER BY created_at DESC

    """)

    reviews = cursor.fetchone()

    cursor.execute("""

    SELECT AVG(rating)
    FROM reviews

    WHERE product_id = ?

    """)

    average_rating = cursor.fetchone()

    cursor.close()

    return render_template(
        "product_detail.html",
        product=product,
        reviews=reviews,
        average_rating=average_rating
    )


@app.route("/admin", methods=["GET", "POST"])
def admin():

    if "admin" not in session:

        return redirect("/login")
    

    if request.method == "POST":

        name = request.form["name"]

        price = request.form["price"]

        description = request.form["description"]

        stock = request.form["stock"]

        image = request.files["image"]

        filename = secure_filename(image.filename)

        image.save(
            os.path.join(app.config["UPLOAD_FOLDER"], filename)
        )

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute("""

        INSERT INTO products (
            name,
            price,
            image,
            description,
            stock
        )

        VALUES (%s, %s, %s, %s, %s)

        """, (name, price, filename, description, stock))

        connection.commit()

        cursor.close()

        return redirect("/admin")

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM products"
    )

    products = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin.html",
        products=products
    )


@app.route("/delete-product/<int:product_id>")
def delete_product(product_id):

    if "admin" not in session:

        return redirect("/login")

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM products WHERE id = %s",
        (product_id,)
    )

    connection.commit()

    connection.close()

    return redirect("/admin")


@app.route("/edit-product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):

    if "admin" not in session:

        return redirect("/login")

    connection = get_db_connection()

    cursor.execute(
        "SELECT * FROM products WHERE id = %s",
        (product_id,)
    )

    product = cursor.fetchone()

    if request.method == "POST":

        name = request.form["name"]

        price = request.form["price"]

        description = request.form["description"]

        image = request.files["image"]

        filename = product["image"]

        if image.filename != "":

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        cursor.execute("""

        UPDATE products

        SET
            name = %s,
            price = %s,
            image = %s,
            description = %s

        WHERE id = %s

        """, (
            name,
            price,
            filename,
            description,
            product_id
        ))

        connection.commit()

        cursor.close()

        return redirect("/admin")

    connection.close()

    return render_template(
        "edit_product.html",
        product=product
    )

ADMIN_USERNAME = "admin"

ADMIN_PASSWORD_HASH = 'scrypt:32768:8:1$bmxZSQgciZn09EJd$bc0750fb178d5986301d9042b570cc92c518c7d3a83bebb6bccdda851150e006dea97263852b86ab962c0426129d19828cae68fd003e72bd2e3b19336a397752'


@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        if (
            username == ADMIN_USERNAME
            and check_password_hash(
                ADMIN_PASSWORD_HASH,
                password
                )
        ):

            session["admin"] = True

            return redirect("/admin")

        else:

            error = "Invalid username or password"

    return render_template(
        "login.html",
        error=error
    )


@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect("/login")


@app.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):

    if "cart" not in session:

        session["cart"] = {}

    cart = session["cart"]

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE id = %s",
        (product_id,)
    )

    product = cursor.fetchone()

    if not product:

        cursor.close()

        connection.close()

        return redirect("/")

    if product["stock"] <= 0:

        cursor.close()

        connection.close()

        return redirect("/")

    product_id = str(product_id)

    if product_id in cart:

        cart[product_id] += 1

    else:

        cart[product_id] = 1

    session["cart"] = cart

    cursor.close()

    connection.close()

    return redirect("/cart")


@app.route("/cart")
def cart():

    cart = session.get("cart", {})

    products = []

    total_price = 0

    connection = get_db_connection()

    cursor = connection.cursor()

    for product_id, quantity in cart.items():

        cursor.execute(
            "SELECT * FROM products WHERE id = %s",
            (product_id,)
        )

        product = cursor.fetchone()

        if product:

            price = product["price"]

            total = price * quantity

            total_price += total

            products.append({

                "id": product["id"],

                "name": product["name"],

                "price": product["price"],

                "image": product["image"],

                "quantity": quantity,

                "total": total

            })

    cursor.close()

    return render_template(
        "cart.html",
        products=products,
        total_price=total_price
    )


@app.route("/remove-from-cart/<int:product_id>")
def remove_from_cart(product_id):

    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:

        cart[product_id] -= 1

        if cart[product_id] <= 0:

            del cart[product_id]

    session["cart"] = cart

    return redirect("/cart")




@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    cart = session.get("cart", {})

    if not cart:

        return redirect("/cart")

    user_id = session.get("user_id")

    if request.method == "POST":

        customer_name = request.form["customer_name"]

        phone = request.form["phone"]

        address = request.form["address"]

        connection = get_db_connection()

        cursor = connection.cursor()

        total_price = 0

        products_data = []

        for product_id, quantity in cart.items():

            cursor.execute(

                "SELECT * FROM products WHERE id = %s",

                (product_id,)
            )

            product = cursor.fetchone()

            if product:

                price = product["price"]

                total = price * quantity

                total_price += total

                products_data.append({

                    "product_id": product_id,

                    "quantity": quantity

                })

        cursor.execute("""

        INSERT INTO orders (
            user_id,
            customer_name,
            phone,
            address,
            total_price
        )

        VALUES (%s, %s, %s, %s, %s)

        RETURNING id

        """, (
            user_id,
            customer_name,
            phone,
            address,
            total_price
        ))

        order_id = cursor.fetchone()["id"]

        for item in products_data:

            cursor.execute("""

            INSERT INTO order_items (
                order_id,
                product_id,
                quantity
            )

            VALUES (%s, %s, %s)

            """, (
                order_id,
                item["product_id"],
                item["quantity"]
            ))

            cursor.execute("""

            UPDATE products

            SET stock = stock - %s

            WHERE id = %s

            """, (
                item["quantity"],
                item["product_id"]
            ))

        connection.commit()

        cursor.close()

        connection.close()

        session["cart"] = {}

        return redirect("/success")

    return render_template("checkout.html")



@app.route("/success")
def success():

    return render_template("success.html")



@app.route("/admin/orders")
def admin_orders():

    if "admin" not in session:

        return redirect("/login")

    connection = get_db_connection()

    orders = connection.execute("""

    SELECT * FROM orders

    ORDER BY created_at DESC

    """).fetchall()

    orders_data = []

    for order in orders:

        items = connection.execute("""

        SELECT
            products.name,
            products.image,
            order_items.quantity

        FROM order_items

        JOIN products
        ON order_items.product_id = products.id

        WHERE order_items.order_id = ?

        """, (order["id"],)).fetchall()

        orders_data.append({

            "order": order,

            "items": items

        })

    connection.close()

    return render_template(
        "admin_orders.html",
        orders_data=orders_data
    )



@app.route("/update-order-status/<int:order_id>/<status>")
def update_order_status(order_id, status):

    if "admin" not in session:

        return redirect("/login")

    connection = get_db_connection()

    connection.execute("""

    UPDATE orders

    SET status = ?

    WHERE id = ?

    """, (status, order_id))

    connection.commit()

    connection.close()

    return redirect("/admin/orders")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]

        email = request.form["email"]

        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute("""

        SELECT * FROM users

        WHERE email = %s

        """, (email,))

        existing_user = cursor.fetchone()

        if existing_user:

            cursor.close()

            connection.close()

            return "Email already exists"

        cursor.execute("""

        INSERT INTO users (
            username,
            email,
            password
        )

        VALUES (%s, %s, %s)

        """, (
            username,
            email,
            hashed_password
        ))

        connection.commit()

        cursor.close()

        connection.close()

        return redirect("/user-login")

    return render_template("register.html")


@app.route("/user-login", methods=["GET", "POST"])
def user_login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute("""

        SELECT * FROM users

        WHERE email = %s

        """, (email,))

        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]

            session["username"] = user["username"]

            return redirect("/")

        return "Invalid email or password"

    return render_template("user_login.html")



@app.route("/user-logout")
def user_logout():

    session.pop("user_id", None)

    session.pop("username", None)

    return redirect("/")



@app.route("/my-orders")
def my_orders():

    if "user_id" not in session:

        return redirect("/user-login")

    user_id = session["user_id"]

    connection = get_db_connection()

    orders = connection.execute("""

    SELECT * FROM orders

    WHERE user_id = ?

    ORDER BY created_at DESC

    """, (user_id,)).fetchall()

    orders_data = []

    for order in orders:

        items = connection.execute("""

        SELECT
            products.name,
            products.image,
            products.price,
            order_items.quantity

        FROM order_items

        JOIN products
        ON order_items.product_id = products.id

        WHERE order_items.order_id = ?

        """, (order["id"],)).fetchall()

        orders_data.append({

            "order": order,

            "items": items

        })

    connection.close()

    return render_template(
        "my_orders.html",
        orders_data=orders_data
    )



@app.route("/add-review/<int:product_id>", methods=["POST"])
def add_review(product_id):

    if "user_id" not in session:

        return redirect("/user-login")

    rating = request.form["rating"]

    comment = request.form["comment"]

    user_id = session["user_id"]

    connection = get_sqlite_connection()

    connection.execute("""

    INSERT INTO reviews (
        user_id,
        product_id,
        rating,
        comment
    )

    VALUES (?, ?, ?, ?)

    """, (
        user_id,
        product_id,
        rating,
        comment
    ))

    connection.commit()

    connection.close()

    return redirect(f"/product/{product_id}")



if __name__ == "__main__":
    app.run(debug=True)


