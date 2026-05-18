from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
import os
import sqlite3

app = Flask(__name__)

UPLOAD_FOLDER = "static/images"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def get_db_connection():

    connection = sqlite3.connect("database.db")

    connection.row_factory = sqlite3.Row

    return connection

@app.route("/")
def home():

    connection = get_db_connection()

    products = connection.execute(
        "SELECT * FROM products"
    ).fetchall()

    connection.close()

    return render_template(
        "index.html",
        products=products
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

    if request.method == "POST":

        name = request.form["name"]

        price = request.form["price"]

        description = request.form["description"]

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
            description
        )

        VALUES (?, ?, ?, ?)

        """, (name, price, filename, description))

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

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM products WHERE id = ?",
        (product_id,)
    )

    connection.commit()

    connection.close()

    return redirect("/admin")


if __name__ == "__main__":
    app.run(debug=True)