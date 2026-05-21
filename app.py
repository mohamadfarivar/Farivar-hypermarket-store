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

app = Flask(__name__)
app.secret_key = "super-secret-key"

UPLOAD_FOLDER = "static/images"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def get_db_connection():

    connection = sqlite3.connect("database.db")

    connection.row_factory = sqlite3.Row

    return connection


@app.route("/")
def home():

    search = request.args.get("search", "")

    category = request.args.get("category", "")

    connection = get_db_connection()

    categories = connection.execute(
        "SELECT * FROM categories"
    ).fetchall()

    query = "SELECT * FROM products WHERE 1=1"

    params = []

    if search:

        query += " AND name LIKE ?"

        params.append(f"%{search}%")

    if category:

        query += " AND category_id = ?"

        params.append(category)

    products = connection.execute(
        query,
        params
    ).fetchall()

    connection.close()

    return render_template(
        "index.html",
        products=products,
        categories=categories
    )



@app.route("/product/<int:product_id>")
def product_detail(product_id):

    connection = get_db_connection()

    product = connection.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    connection.close()

    return render_template(
        "product.html",
        product=product
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

        connection.execute("""

        INSERT INTO products (
            name,
            price,
            image,
            description,
            stock
        )

        VALUES (?, ?, ?, ?, ?)

        """, (name, price, filename, description, stock))

        connection.commit()

        connection.close()

        return redirect("/admin")

    connection = get_db_connection()

    products = connection.execute(
        "SELECT * FROM products"
    ).fetchall()

    connection.close()

    return render_template(
        "admin.html",
        products=products
    )


@app.route("/delete-product/<int:product_id>")
def delete_product(product_id):

    if "admin" not in session:

        return redirect("/login")

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM products WHERE id = ?",
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

    product = connection.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

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

        connection.execute("""

        UPDATE products

        SET
            name = ?,
            price = ?,
            image = ?,
            description = ?

        WHERE id = ?

        """, (
            name,
            price,
            filename,
            description,
            product_id
        ))

        connection.commit()

        connection.close()

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

    product = connection.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if not product:

        connection.close()

        return redirect("/")

    if product["stock"] <= 0:

        connection.close()

        return redirect("/")

    product_id = str(product_id)

    if product_id in cart:

        cart[product_id] += 1

    else:

        cart[product_id] = 1

    session["cart"] = cart

    return redirect("/cart")


@app.route("/cart")
def cart():

    cart = session.get("cart", {})

    products = []

    total_price = 0

    connection = get_db_connection()

    for product_id, quantity in cart.items():

        product = connection.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()

        if product:

            price = int(product["price"].replace("$", ""))

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

    connection.close()

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

    if request.method == "POST":

        customer_name = request.form["customer_name"]

        phone = request.form["phone"]

        address = request.form["address"]

        connection = get_db_connection()

        total_price = 0

        products_data = []

        for product_id, quantity in cart.items():

            product = connection.execute(
                "SELECT * FROM products WHERE id = ?",
                (product_id,)
            ).fetchone()

            if product:

                price = int(
                    product["price"].replace("$", "")
                )

                total = price * quantity

                total_price += total

                products_data.append({
                    "product_id": product_id,
                    "quantity": quantity
                })

        cursor = connection.cursor()

        cursor.execute("""

        INSERT INTO orders (
            customer_name,
            phone,
            address,
            total_price
        )

        VALUES (?, ?, ?, ?)

        """, (
            customer_name,
            phone,
            address,
            total_price
        ))

        order_id = cursor.lastrowid

        for item in products_data:

            cursor.execute("""

            INSERT INTO order_items (
                order_id,
                product_id,
                quantity
            )

            VALUES (?, ?, ?)

            """, (
                order_id,
                item["product_id"],
                item["quantity"]
            ))


            cursor.execute("""

        UPDATE products

        SET stock = stock - ?

        WHERE id = ?

        """, (
            item["quantity"],
            item["product_id"]
        ))

        connection.commit()

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



if __name__ == "__main__":
    app.run(debug=True)