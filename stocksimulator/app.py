import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from helpers import apology, login_required, lookup, usd, myr
import re

# Configure application
app = Flask(__name__)



# Custom filter
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["myr"] = myr

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


def get_db():
    conn = sqlite3.connect("finance.db")
    conn.row_factory = sqlite3.Row
    return conn


def is_username_taken(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()
    db.close()
    return user_id is not None


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    history = db.execute(
        "SELECT symbol, stock_name, SUM(quantity) AS quantity, price FROM history WHERE user_id = ? GROUP BY symbol HAVING SUM(quantity) >= 0",
        user_id,
    )
    print(history)
    unique_symbols = set()
    current_data = {}
    # Goes through history to get the unique symbols and stores in unique_symbols
    for item in history:
        unique_symbols.add(item["symbol"])
    # Goes through the list of unique symbols and gets the current price of the stocks
    for symbol in unique_symbols:
        data = lookup(symbol)
        if data:
            current_data[symbol] = data
    # Goes through list of unique symbols in history list and updates the price with the current price of the stock
    total_MYR = 0
    total_USD = 0
    for entry in history:
        symbol = entry["symbol"]
        if symbol in current_data:
            entry["price"] = current_data[symbol]["price"]
        quantity = entry["quantity"]
        total_price = db.execute("SELECT price, quantity, symbol FROM history WHERE symbol = ? AND transaction_type = ? ORDER BY timestamp DESC LIMIT ?", symbol, "BUY", quantity)
        print(total_price)

        #if total_price:
        #    total_price = total_price[0]['avg_price']
        #    entry["avg_price"] = round(total_price, 2)
        price = entry["price"]
        value = quantity * price
        if entry["symbol"][-3:] == ".KL":
            total_MYR += value
        else:
            total_USD += value
        # Changes symbol name to the actual company name based on another table
        name_list = current_data[symbol]["name"]
        entry["stock_name"] = name_list
        # Gets the average price bought for the quantities
         #for price in prices:
    user_cash_USD = db.execute("SELECT cash_USD FROM users WHERE id = ?", user_id)
    user_cash_MYR = db.execute("SELECT cash_MYR FROM users WHERE id = ?", user_id)
    cash_USD = user_cash_USD[0]["cash_USD"]
    cash_MYR = user_cash_MYR[0]["cash_MYR"]
    final_total_USD = int(round((total_USD + cash_USD), 2))
    final_total_MYR = int(round((total_MYR + cash_MYR), 2))
    print(history)
    return render_template("index.html", rows=history, MYR=cash_MYR, total_USD=final_total_USD, USD=cash_USD, total_MYR=final_total_MYR)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # Stock_symbol = stock_symbol;
    if request.method == "POST":
        stock_symbol = request.form.get("symbol")
        if not stock_symbol:
            return apology("Please Enter a symbol", 400)
        upper_stock_symbol = stock_symbol.upper()
        stock_quantity = request.form.get("shares")
        stock_data = lookup(upper_stock_symbol)
        if stock_data == None:
            return apology("Symbol does not exist or input is blank", 400)
        stock_name = stock_data["name"]
        while True:
            try:
                value = int(stock_quantity)
                if value <= 0:
                    return apology("Please input a number more than 0", 400)
                else:
                    break
            except ValueError:
                return apology("Please enter a valid positive integer", 400)
        user_id = session["user_id"]
        stock_price = stock_data["price"]
        if stock_data["symbol"][-3:] == ".KL":
            user_cash_myr = db.execute("SELECT cash_MYR FROM users WHERE id = :id", id=user_id)
            user_cash = user_cash_myr[0]["cash_MYR"]
        else:    
            user_cash_usd = db.execute("SELECT cash_USD FROM users WHERE id = :id", id=user_id)
            user_cash = user_cash_usd[0]["cash_USD"]
        if int(user_cash) < (int(stock_price) * int(stock_quantity)):
            return apology("Insufficient Funds to Purchase", 400)
        db.execute(
            "INSERT INTO history (user_id, quantity, transaction_type, symbol, price, stock_name) VALUES(:user_id, :quantity, :transaction_type, :symbol, :price, :stock_name)",
            user_id=user_id,
            quantity=int(stock_quantity),
            transaction_type="BUY",
            symbol=upper_stock_symbol,
            price=stock_data["price"],
            stock_name=stock_name,
        )
        update_cash = int(user_cash) - (int(stock_price) * int(stock_quantity))
        if stock_data["symbol"][-3:] == ".KL":
            db.execute(
                "UPDATE users SET cash_MYR = :update_cash WHERE id = :user_id",
                update_cash=update_cash,
                user_id=user_id,
            )
        else:
            db.execute(
                "UPDATE users SET cash_USD = :update_cash WHERE id = :user_id",
                update_cash=update_cash,
                user_id=user_id,
            )
        history = db.execute(
            "SELECT symbol, stock_name, quantity, price FROM history WHERE user_id = ? AND symbol = ? ORDER BY ID DESC LIMIT 1",
            user_id,
            upper_stock_symbol,
        )
        user_cash = db.execute("SELECT cash_USD FROM users WHERE id = ?", user_id)
        cash_USD = user_cash[0]["cash_USD"]
        user_cash = db.execute("SELECT cash_MYR FROM users WHERE id = ?", user_id)
        cash_MYR = user_cash[0]["cash_MYR"]
        total_MYR = 0
        total_USD = 0
        for entry in history:
            if entry["symbol"][-3:] == ".KL":  
                quantity = entry["quantity"]
                price = entry["price"]
                value = quantity * price
                total_MYR += value
            else:
                quantity = entry["quantity"]
                price = entry["price"]
                value = quantity * price
                total_USD += value
        final_total_MYR = int(round((total_MYR + cash_MYR), 2))
        final_total_USD = int(round((total_USD + cash_USD), 2))
        flash("Stock is successfully purchased!")
        return render_template("index.html", rows=history, MYR=cash_MYR, USD=cash_USD, total_MYR = final_total_MYR, total_USD = final_total_USD)
    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    history = db.execute(
        "SELECT symbol, stock_name, quantity, transaction_type, price, timestamp FROM history WHERE user_id = ? ORDER BY timestamp DESC",
        user_id,
    )
    return render_template("historic.html", rows=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        stock_data = lookup(symbol)
        if stock_data == None:
            return apology("Symbol does not exist", 400)
        stock_name = stock_data["name"]
        stock_price = stock_data["price"]
        stock_symbol = stock_data["symbol"]
        if stock_symbol[-3:] == ".KL":
            currency = "MYR"
        else:
            currency = "USD"
        return render_template(
            "quoted.html",
            Stock_name=stock_name,
            Stock_price=stock_price,
            Stock_symbol=stock_symbol,
            currency = currency,
        )

    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmation")
        # Check if its a unique username

        # Generate the password hash and store it
        if is_username_taken(username):
            return apology(
                "Username is already taken. Please Choose a different username.", 400
            )
        if password == "" or username == "":
            return apology("Username or Password is blank", 400)
        if password != confirm_password:
            return apology("Passwords do not match", 400)
        if password == confirm_password:
            hashed_password = generate_password_hash(password, method="sha256")
            db.execute(
                "INSERT INTO users (username, hash) VALUES (:username, :hash)",
                username=username,
                hash=hashed_password,
            )
            return render_template("login.html")

    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        user_id = session["user_id"]
        stock_list = db.execute(
            "SELECT symbol FROM history WHERE user_id = :user_id GROUP BY symbol HAVING SUM(quantity) > 0",
            user_id=user_id,
        )
        return render_template(
            "sell.html", stock_list=[row["symbol"] for row in stock_list]
        )
    if request.method == "POST":
        user_id = session["user_id"]
        stock_symbol = request.form.get("symbol").upper()
        stock_quantity = int(request.form.get("shares"))
        stock_data = lookup(stock_symbol)
        stock_name = stock_data["name"]
        stock_price = stock_data["price"]
        if stock_symbol == "" or stock_data == None:
            return apology("Symbol does not exist or input is blank", 400)
        if int(stock_quantity) <= 0:
            return apology("Please input a number more than 0", 400)
        while True:
            try:
                value = int(stock_quantity)
                if value <= 0:
                    return apology("Please input a number more than 0", 400)
                else:
                    break
            except ValueError:
                return apology("Please enter a valid positive integer", 400)
        # Check Stock Count
        stock_count = db.execute(
            "SELECT SUM(quantity) FROM history WHERE user_id = :user_id AND symbol = :symbol",
            user_id=user_id,
            symbol=stock_symbol,
        )
        act_stock_count = stock_count[0]["SUM(quantity)"]
        total_stock_count = int(act_stock_count) + (int(stock_quantity) * -1)
        if total_stock_count < 0:
            return apology("You do not have enough stock to sell", 400)
        db.execute(
            "INSERT INTO history (user_id, quantity, symbol, price, transaction_type, stock_name) VALUES(:user_id, :quantity, :symbol, :price, :trans, :stock_name)",
            user_id=user_id,
            quantity=-(int(stock_quantity)),
            symbol=stock_symbol,
            price=stock_price,
            trans="SELL",
            stock_name=stock_name,
        )
        profit = stock_price * stock_quantity
        if stock_symbol[-3:] == ".KL":
            user_cash_dict = db.execute("SELECT cash_MYR FROM users WHERE id = :id", id=user_id)
            user_cash = user_cash_dict[0]["cash_MYR"]
            total_cash = user_cash + profit
            db.execute(
            "UPDATE users SET cash_MYR = :total_cash WHERE id = :user_id",
            total_cash=total_cash,
            user_id=user_id,
            )
        else:
            user_cash_dict = db.execute("SELECT cash_USD FROM users WHERE id = :id", id=user_id)
            user_cash = user_cash_dict[0]["cash_USD"]
            total_cash = user_cash + profit
            db.execute(
            "UPDATE users SET cash_USD = :total_cash WHERE id = :user_id",
            total_cash=total_cash,
            user_id=user_id,
            )
        history = db.execute(
            "SELECT symbol, stock_name, SUM(quantity) AS quantity, price FROM history WHERE user_id = ? AND symbol = ?",
            user_id,
            stock_symbol
        )
        user_cash_USD = db.execute("SELECT cash_USD FROM users WHERE id = ?", user_id)
        cash_USD = user_cash_USD[0]["cash_USD"]
        user_cash_MYR = db.execute("SELECT cash_MYR FROM users WHERE id = ?", user_id)
        cash_MYR = user_cash_MYR[0]["cash_MYR"]

        total_MYR = 0
        total_USD = 0
        for entry in history:
            quantity = entry["quantity"]
            price = entry["price"]
            value = quantity * price
            if stock_symbol[-3:] == ".KL":
                total_MYR += value
            else:
                total_USD += value

        final_total_USD = int(round((total_USD + cash_USD), 2))
        final_total_MYR = int(round((total_MYR + cash_MYR), 2))

        flash("Stock is successfully sold!")
        return render_template("index.html", rows=history, MYR=cash_MYR, USD=cash_USD, total_MYR = final_total_MYR, total_USD = final_total_USD)


@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    """Add Cash to Users Account"""
    user_id = session["user_id"]
    user_cash = db.execute("SELECT cash_USD, cash_MYR cash_MYR FROM users WHERE id = ?", user_id)
    cash_USD = user_cash[0]["cash_USD"]
    cash_MYR = user_cash[0]["cash_MYR"]
    if request.method == "POST":
        amount = request.form.get("cash")
        currency = request.form.get("currency")
        user_id = session["user_id"]
        if currency == "USD":
            user_cash = db.execute("SELECT cash_USD FROM users WHERE id = ?", user_id)
            cash = user_cash[0]["cash_USD"]
        if currency == "MYR":
            user_cash = db.execute("SELECT cash_MYR FROM users WHERE id = ?", user_id)
            cash = user_cash[0]["cash_MYR"]
        while True:
            try:
                value = int(amount)
                if value <= 0:
                    return apology("Please input a number more than 0", 400)
                else:
                    break
            except ValueError:
                return apology("Please enter a valid positive integer", 400)
        # Add cash
        total = int(amount) + cash
        if currency == "USD":
            db.execute(
                "UPDATE users SET cash_USD = :total_cash WHERE id = :user_id",
                total_cash=total,
                user_id=user_id,
            )
            current_cash_USD = user_cash = db.execute(
                "SELECT cash_USD FROM users WHERE id = ?", user_id
            )
            current_cash_MYR = user_cash = db.execute(
                "SELECT cash_MYR FROM users WHERE id = ?", user_id
            )
            cash_MYR = current_cash_MYR[0]["cash_MYR"]
            cash_USD = current_cash_USD[0]["cash_USD"]
        if currency == "MYR":
            db.execute(
                "UPDATE users SET cash_MYR = :total_cash WHERE id = :user_id",
                total_cash=total,
                user_id=user_id,
            )
            current_cash_MYR = user_cash = db.execute(
                "SELECT cash_MYR FROM users WHERE id = ?", user_id
            )
            current_cash_USD = user_cash = db.execute(
                "SELECT cash_USD FROM users WHERE id = ?", user_id
            )
            cash_MYR = current_cash_MYR[0]["cash_MYR"]
            cash_USD = current_cash_USD[0]["cash_USD"]
        flash("Cash Successfully Added!")
        return render_template("add_cash.html", cash_MYR=cash_MYR, cash_USD=cash_USD, currency=["USD", "MYR"])

    return render_template("add_cash.html", cash_MYR=cash_MYR, cash_USD=cash_USD, currency=["USD", "MYR"])



if __name__ == '__main__':
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(debug=True)
