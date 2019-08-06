import os
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Setup and connect database
con = sqlite3.connect('test.db')
con.close()


@app.route("/")
@login_required
def index():

    # Connect to DataBase
    con =  sqlite3.connect('test.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()

    # Store user's ID and look up in database
    user_id = session['user_id']
    db.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = db.fetchone();
    con.close()

	# Look up user's cash, store as credit
    credit = user['cash']

    # Check if user is an Admin, assign as true or false
    if user['admin'] == 1:
        admin = True
    else:
        admin = False

    # Render intex template
    return render_template("index.html", credit=credit, admin=admin)


@app.route ("/login", methods=["GET", "POST"])
def login():
    """Login user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Remember username
        username = request.form.get("username")

        # Connect to DataBase
        con =  sqlite3.connect('test.db')
        con.row_factory = sqlite3.Row
        db = con.cursor()

        # Query database for username
        db.execute("SELECT * FROM users WHERE username=?", (username,))
        rows = db.fetchall();
        con.close()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by titlesubmitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # ensure password and confirmation password match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # hash password given
        password_hash = generate_password_hash(request.form.get("password"))

        # Remember username
        username = request.form.get("username")

        # Connect to DataBase
        con =  sqlite3.connect('test.db')
        con.row_factory = sqlite3.Row
        db = con.cursor()

        try:

            # insert username and password hash into database
            db.execute("INSERT INTO users (username, hash) VALUES (?,?)", (username, password_hash))
            con.commit()
        except:
        # username has already been taken
            con.rollback()
            con.close()
            return apology("username already taken", 400)

        # Query database for username
        db.execute("SELECT * FROM users WHERE username=?", (username,))
        rows = db.fetchall();
        con.close()

        # log user in and remember user that is logged in
        session["user_id"] = rows[0]["id"]

        flash("We have given you $20 worth of store credit for signing up, thanks!")
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/products")
@login_required
def products():
    """List products that user can purchase"""

    # Connect to DataBase
    con =  sqlite3.connect('test.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()

    # Store user's ID and look up in database
    user_id = session['user_id']
    db.execute("SELECT admin FROM users WHERE id=?", (user_id,))
    user = db.fetchone();

    # Check if user is an Admin (function dissabled for admins)
    if user['admin'] == 1:
       flash("Sorry, this feature is disabled for admins")
       con.close()
       return redirect("/")

    else:
        # Look up all products in inventory that are in stock
        db.execute("SELECT * FROM inventory WHERE quantity > 0")
        products = db.fetchall()

        # Return a rendered product's template
        con.close()
        return render_template("products.html", products=products)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    # Connect to DataBase
    con =  sqlite3.connect('test.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()

    # Store user's ID and look up in database
    user_id = session['user_id']
    db.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = db.fetchone();

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Remember the name of the product and quantity being purchased
        purchased_product = request.form.get("purchasing")
        sale_quantity = int(request.form.get("quantity"))

        # Look up the product being sold in inventory database, and the user's cash
        db.execute("SELECT * FROM inventory WHERE product=?", (purchased_product,))
        product_sale = db.fetchone()
        
        cash_before = user["cash"]

        # Calculate the cost of the sale
        sale_cost = sale_quantity * product_sale['price']
        sale_cost = round(sale_cost, 2)

        # Calculate amount of product in stock remaining after sale
        stock_after = product_sale['quantity'] - sale_quantity

        # Return apology if there is not enough product in stock
        if stock_after < 0:
            return apology("sorry, not enough product in stock", 400)

        # Calculate the user's cash after sale
        cash_after = cash_before - sale_cost
        cash_after = round(cash_after, 2)

        # Return apology if the user doesn't have enough cash for transaction
        if cash_after < 0:
            return apology("sorry, not enough store credit", 400)

        try:
            units = sale_quantity * -1
            # Log transaction into history database
            db.execute("INSERT INTO history (user_id,product,units,sale,cash_after) VALUES (?,?,?,?,?)",(user_id, purchased_product, units, sale_cost, cash_after))

            # Update user's cash in the user database
            db.execute("UPDATE users SET cash=? WHERE id=?", (cash_after, user_id))

            # Update the number of products remaining in stock into the inventory database
            db.execute("UPDATE inventory SET quantity=? WHERE product=?", (stock_after, purchased_product))

            # Remember admin's username to update their cash with the revenue from sale
            admin_username = 'cldaly'
            db.execute("SELECT * FROM users WHERE username=?", (admin_username,))
            admin_cash = db.fetchone();
            admin_cash_after = admin_cash['cash']+sale_cost


            # Update admin's cash in users database
            db.execute("UPDATE users SET cash=? WHERE username=?", (admin_cash_after, admin_username))

            con.commit();
            con.close()
        except:
            con.rollback()
            con.close()
            return apology("something went wrong", 400)

        finally:
            # Set admin status to 0, to correct the layout.html
            admin_status = 0

            # Return user to purchased page

            return render_template("purchased.html", purchased_product=purchased_product, price=product_sale['price'], sale_quantity=sale_quantity, sale_cost=sale_cost, cash_after=cash_after, admin_status=admin_status)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Check if user is an Admin (function dissabled for admins)
        if user['admin'] == 1:
           flash("Sorry, this feature is disabled for admins")
           con.close()
           return redirect("/")

        else:
            # Lookup product in inventory based on the product selected on products page
            product_title = request.args.get("p")
            db.execute("SELECT * FROM inventory WHERE product=?", (product_title,))
            product_buy = db.fetchone()

            # Remember the number of units in stock for product selected
            stock_quantity = product_buy['quantity']

            # Check the user's cash
            credit = user['cash']

            # Render the buy template
            con.close()
            return render_template("buy.html", product_buy=product_buy, stock_quantity=stock_quantity, credit=credit)


@app.route("/history")
@login_required
def history():
    """Show user their purchase history"""

    # Connect to DataBase
    con =  sqlite3.connect('test.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()

    # Store user's ID and look up in database
    user_id = session['user_id']
    db.execute("SELECT admin FROM users WHERE id=?", (user_id,))
    user = db.fetchone()

    # Check if user is an Admin (function dissabled for admins)
    if user['admin'] == 1:
       flash("Sorry, this feature is disabled for admins")
       con.close()
       return redirect("/")

    else:
        # Look up all of the user's transactions in the history database
        db.execute("SELECT * FROM history WHERE user_id=?", (user_id,))
        transactions = db.fetchall()

        # Check the number of transactions, will prompt user for different response if == 0
        number_of_transactions = len(transactions)

        con.close()
        return render_template("history.html", transactions=reversed(transactions), number_of_transactions=number_of_transactions)


@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    """Change Password"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if not request.form.get("current_password"):
            return apology("please enter current password", 400)

        if not request.form.get("password"):
            return apology("please enter new password", 400)

        if not request.form.get("current_password"):
            return apology("please confirm new password", 400)

        # Connect to DataBase
        con =  sqlite3.connect('test.db')
        con.row_factory = sqlite3.Row
        db = con.cursor()

        # Store user's ID and look up in database
        user_id = session['user_id']
        db.execute("SELECT * FROM users WHERE id=?", (user_id,))
        current_user = db.fetchone()

        if not check_password_hash(current_user["hash"], request.form.get("current_password")):
            return apology("current password is incorrect", 400)

        # ensure new password and confirmation password match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("new passwords do not match", 400)

        # ensure new password and old password aren't the same
        if request.form.get("current_password") == request.form.get("password"):
            return apology("new password is same as old password", 400)

        # hash new password
        password_hash = generate_password_hash(request.form.get("password"))

        try:
            # update password hash for user
            db.execute("UPDATE users SET hash=? WHERE id=?",(password_hash, user_id))
            con.commit()
            con.close()

        except:
            con.rollback()
            con.close()
            return apology("something went wrong", 400)

        # Redirect user to home page
        flash("Password Sucessfully Changed!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("change.html")


@app.route("/admin")
@login_required
def admin():
    """Admin home page"""

    # Connect to DataBase
    con =  sqlite3.connect('test.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()

    # Store user's ID and look up in database
    user_id = session['user_id']
    db.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = db.fetchone();
    con.close()

    # Look up user's cash, store as credit
    credit = user['cash']

    if user['admin'] == 0:

       return redirect("/")

    else:
        # Check user's cash
        credit = user['cash']

        return render_template("admin.html", credit=credit)


@app.route("/account")
@login_required
def account():
    """Account settings for user"""

    # Connect to DataBase
    con =  sqlite3.connect('test.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()

    # Store user's ID and look up in database
    user_id = session['user_id']
    db.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = db.fetchone();
    con.close()

    if user['admin'] == 1:
        return redirect("/admin")

    else:
        # Look up user's cash, store as credit
        credit = user['cash']
        return render_template("account.html", credit=credit)


@app.route("/add-credits", methods=["GET", "POST"])
@login_required
def add_credits():
    """Add credits to user's database profile"""

    # Connect to DataBase
    con =  sqlite3.connect('test.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()

    # Store user's ID and look up in database
    user_id = session['user_id']
    db.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = db.fetchone();

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Remember the number of credits user wants to add
        credits_add = request.form.get("addCredits")

        # Craft response for flash
        if credits_add != '1':
            response = "$" + credits_add + " have been added to your account!"
        else:
            response = "$" + credits_add + " has been added to your account!"

        # Add credits to user's account balance, update database
        cash_after = user['cash'] + int(credits_add)
        cash_after = round(cash_after, 2)

        # Update user's current cash
        try:
            db.execute("UPDATE users SET cash=?WHERE id=?", (cash_after, user_id))
            con.commit()
            con.close()

        except:
            con.rollback()
            con.close()
            return apology("something went wrong", 400)

        # Redirect user back to account page and advise them of credits added
        flash(response)
        return redirect("/account")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        con.close()
        # Check if user is an Admin (function dissabled for admins)
        if user['admin'] == 1:
           flash("Sorry, this feature is disabled for admins")
           return redirect("/")

        else:
            # Look up user's cash, store as credit
            credit = user['cash']
            return render_template("add-credits.html", credit=credit)


@app.route("/inventory")
@login_required
def inventory():
    """List all products in inventory"""

    # Connect to DataBase
    con =  sqlite3.connect('test.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()

    # Store user's ID and look up in database
    user_id = session['user_id']
    db.execute("SELECT admin FROM users WHERE id=?", (user_id,))
    user = db.fetchone();


    # Check if user is an Admin
    if user['admin'] == 0:
        con.close()
        return redirect("/")

    # If user is an admin
    else:
        # Look up all products in inventory that are in stock
        db.execute("SELECT * FROM inventory")
        inventory_stock = db.fetchall()
        con.close()

        # Return a rendered product's template
        return render_template("inventory.html", inventory_stock=inventory_stock)


@app.route("/restock", methods=["GET", "POST"])
@login_required
def restock():

    # Connect to DataBase
    con =  sqlite3.connect('test.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()

    # Store user's ID and look up in database
    user_id = session['user_id']
    db.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = db.fetchone();

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Remember the name of the product and quantity being purchased
        purchased_product = request.form.get("purchasing")
        sale_quantity = int(request.form.get("quantity"))

        # Look up the product being purchased in inventory database, and the user's cash
        db.execute("SELECT * FROM inventory WHERE product=?", (purchased_product,))
        product_buy = db.fetchone()
        cash_before = user['cash']

        # Calculate the cost of the purchase
        sale_cost = sale_quantity * product_buy['cost']
        sale_cost = round(sale_cost,2)
        sale_cost *= -1

        # Calculate amount of product in stock after additional stock purchased
        stock_after = product_buy['quantity'] + sale_quantity

        # Calculate the user's cash after sale
        cash_after = cash_before + sale_cost
        cash_after = round(cash_after, 2)

        # Return apology if the user doesn't have enough cash for transaction
        if cash_after < 0:
            return apology("sorry, not enough cash", 400)

        try:
            # Log transaction into history database
            db.execute("INSERT INTO history (user_id, product, units, sale, cash_after) VALUES (?,?,?,?,?)",(user_id, purchased_product, sale_quantity, sale_cost, cash_after))

            # Update user's cash in the user database
            db.execute("UPDATE users SET cash=? WHERE id=?",(cash_after, user_id))

            # Update the number of products remaining in stock into the inventory database
            db.execute("UPDATE inventory SET quantity=? WHERE product=?", (stock_after, purchased_product))

            # Commit changes to database, close connection
            con.commit()
            con.close()

        except:
            con.rollback()
            con.close()
            return apology("something went wrong", 400)

        finally:
            # Set admin status to 1, user to designate admin-layout.html on purchased.html page
            admin_status = 1

            # Return user to purchased page
            return render_template("purchased.html", purchased_product=purchased_product, price=product_buy['cost'], sale_quantity=sale_quantity, sale_cost=sale_cost, cash_after=cash_after, admin_status=admin_status)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Check if user is an Admin
        if user['admin'] == 0:
            con.close()
            return redirect("/")

        # Lookup product in inventory based on the product selected on products page
        product_title = request.args.get("restock")
        db.execute("SELECT * FROM inventory WHERE product=?", (product_title,))
        product_buy = db.fetchone()
        con.close()

        # Check the user's cash
        credit = user['cash']

        # Render the buy template
        return render_template("restock.html", product_buy=product_buy, credit=credit)


@app.route("/sales")
@login_required
def sales():
    """Show admin history of all sales"""

    # Connect to DataBase
    con = sqlite3.connect('test.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()

    # Store user's ID and look up in database
    user_id = session['user_id']
    db.execute("SELECT admin FROM users WHERE id=?", (user_id,))
    user = db.fetchone();

    # Check if user is an Admin
    if user['admin'] == 0:
        con.close()
        return redirect("/")

    else:
        # Look up all of the user's transactions in the history database
        db.execute("SELECT * FROM history WHERE units<0")
        transactions = db.fetchall()
        con.close()

        # Tally the total number of units sold, and total revenue
        total_units = 0
        total_sales = 0.00

        for trans in transactions:
            total_units += (trans['units'] * -1)
            total_sales += trans['sale']

        return render_template("sales-history.html", transactions=reversed(transactions), total_units=total_units, total_sales=total_sales)


@app.route("/restock-history")
@login_required
def restock_history():
    """Show admin history of all restock purchases"""

    # Connect to DataBase
    con = sqlite3.connect('test.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()

    # Store user's ID and look up in database
    user_id = session['user_id']
    db.execute("SELECT admin FROM users WHERE id=?", (user_id,))
    user = db.fetchone();

    # Check if user is an Admin
    if user['admin'] == 0:
        con.close()
        return redirect("/")

    else:
        # Look up all of the user's transactions in the history database
        db.execute("SELECT * FROM history WHERE units>0")
        transactions = db.fetchall()
        con.close()

        # Tally the total number of units sold, and total revenue
        total_units = 0
        total_sales = 0.00

        for trans in transactions:
            total_units +=trans['units']
            total_sales += (trans['sale'] * -1)

        return render_template("restock-history.html", transactions=reversed(transactions), total_units=total_units, total_sales=total_sales)


@app.route("/new", methods=["GET", "POST"])
@login_required
def new():
    """Show admin history of all restock purchases"""

    # Connect to DataBase
    con = sqlite3.connect('test.db')
    con.row_factory = sqlite3.Row
    db = con.cursor()

    # Store user's ID and look up in database
    user_id = session['user_id']
    db.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = db.fetchone();

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Remember all product info given by user
        product = request.form.get("product")
        description = request.form.get("description")
        cost = float(request.form.get("cost"))
        price = float(request.form.get("price"))
        img_url = request.form.get("img_url")
        quantity = int(request.form.get("quantity"))

        # Canculate total cost for adding new candles
        total_cost = float(cost * quantity)
        total_cost = round(total_cost, 2)
        total_cost *= -1

        # Check user's cash, ensure they have enough to buy
        credit = user['cash']
        cash_after = credit + total_cost
        cash_after = round(cash_after, 2)

        # Return apology if the user doesn't have enough cash for transaction
        if cash_after < 0:
            return apology("sorry, not enough cash", 400)

        try:
            # Update the number of products remaining in stock into the inventory database
            db.execute("INSERT INTO inventory (product,description,cost,price,img_url,quantity) VALUES (?,?,?,?,?,?)",(product,description,cost,price,img_url,quantity))

            # Log transaction into history database
            db.execute("INSERT INTO history (user_id,product,units,sale,cash_after) VALUES (?,?,?,?,?)",(user_id,product,quantity,total_cost,cash_after))

            # Update user's cash in the user database
            db.execute("UPDATE users SET cash=? WHERE id=?",(cash_after, user_id))

            # Commit changes and close db connection
            con.commit()
            con.close()

        except:
            con.rollback()
            con.close()
            return apology("product name already taken", 400)

        finally:
            return render_template("new-confirm.html", product=product, description=description, cost=cost, price=price, img_url=img_url, quantity=quantity, total_cost=total_cost, credit=cash_after)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        con.close()
        # Check if user is an Admin
        if user['admin'] == 0:
           return redirect("/")

        else:
            # Check the user's cash
            credit = user['cash']
            return render_template("new.html", credit=credit)



def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)