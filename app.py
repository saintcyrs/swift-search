import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///themes.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """Show autofill search option -- make autofill through javascript"""
    
    # Display the search feature on the homepage
    return render_template("index.html")


@app.route("/search", methods=["GET","POST"])
def search():
    """Search through the database for songs """
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("q"):
            return apology("Not a theme")

        # Query database for songs with given theme
        songs = db.execute("SELECT * FROM themes WHERE ? = 1", request.form.get("q"))

        # Render table of songs
        return render_template("search.html", songs=songs)

    # Show search page    
    return render_template("index.html")

""" @app.route("/history")
@login_required
def history():
    Show history of transactions
    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ?", session["user_id"])

    return render_template("history.html", transactions=transactions )


@app.route("/login", methods=["GET", "POST"])
def login():
    Log user in

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("theme"):
            return apology("must provide username", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM themes WHERE theme = ?", request.form.get("theme"))

        # Ensure username exists and password is correct
        if len(rows) != 1:
            return apology("invalid theme", 403)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    Log user out

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    Get a stock quote.

    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("symbol"):
            return apology("missing symbol")

        # Get stock quote
        quote = lookup(request.form.get("symbol"))
        if not quote:
            return apology("invalid symbol")

        # Display quote
        return render_template("quoted.html", quote=quote)

    # GET
    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    Register user
    
    # Forget any user_id
    session.clear()

    # Declare variables for HTML form submissions
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    if request.method == "POST":

        # Ensure a username was submitted
        if not username:
            return apology("must provide username", 400)
        
        # Ensure a password was submitted
        elif not password:
            return apology ("must provide password", 400)
        
        # Ensure user confirmed password
        elif not confirmation:
            return apology("must confirm password", 400)
        
        # Ensure passwords match
        elif password != confirmation:
            return apology("passwords must match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Check if username already exists
        if len(rows) != 0:
            return apology("username already exists", 403)
        
        else:
            # Generate hash of user's password
            pass_hash = generate_password_hash(password)

            # Insert new user into database
            db.execute("INSERT INTO users (username, hash) VALUES (?,?)", username, pass_hash)
            
            # Remember which user has registered
            # Check50 says that a user has not registered after this, but the user database updates
            session["user_id"] = rows[0]["id"]

            # Redirect user to login page
            return redirect("/login")

    return render_template("registration.html")

# My implementation of sell has failed, no one has been able to find out what is wrong. This is what I have as of now.
@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():

    # Declare variable for symbols
    symbols = [db.execute("SELECT DISTINCT symbol FROM transactions WHERE user_id = ?", session["user_id"])[0]]
    
    if request.method == "POST":

        # Declare variable for selected symbol
        symbol = request.form.get('symbol')

        # Declare variable for number of shares
        shares = int(float(request.form.get('shares')))

        # Find out how many shares of each stock owned
        owned = db.execute("SELECT SUM(shares) as shares FROM transactions WHERE user_id = ? and symbol = ?", session["user_id"], str(symbol))[0]

        # Make sure valid number of shares
        if shares <= 0 or type(shares) is not int:
            return apology("invalid number of shares", 403)
        
        # Make sure that number of shares requested to sell is less than or equal to that which you have purchased
        elif shares > owned:
            return apology("you are selling more than you have", 403)

        # Declare variables for transactions table
        price = lookup(symbol)['price']
        available_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]['cash']
        sold = shares * price
        date = db.execute("SELECT CURRENT_TIMESTAMP")[0]['CURRENT_TIMESTAMP']

        # Prevent against front-end hacks
        if request.form.get('symbol') not in symbols:
            return apology("invalid symbol", 403)
        
        # Update amount of cash
        db.execute("UPDATE users SET cash = ? WHERE id = ?", (available_cash + sold), session["user_id"])

        # Update transactions table for new sale
        db.execute("INSERT INTO transactions (userID, symbol, shares, price, value, date) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], symbol.upper(), -shares, price, sold, date)
        return redirect("/")

    else:

        # Declare variale for all symbols (get request)
        symbols = db.execute("SELECT DISTINCT symbol FROM transactions WHERE user_id = ?", session['user_id'])

        # Show form
        return render_template("sell.html", symbols=symbols)

def errorhandler(e):
    Handle error
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)"""
