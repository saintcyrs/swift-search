from cs50 import SQL
from flask import Flask, redirect, render_template, request
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///themes.db")

#  Initialize global variable to name of each of the columns in TS database
columns = ["Traffic Lights", "Keeping Score", "Time", "Fate", "Times of Day", "Rain", "Car", "Alcohol", "Apologies", "Forever", "Calling", "Patching Things Up", "Clothing", "Comparisons", "Months", "Summer", "Dreams", "Intertwined", "Death", "Dancing", "Fire", "Memory", "Gold", "Red", "Blue", "Age", "Blood", "Screaming", "Cold", "Painting", "Lipstick", "Door", "Lots of Small Things", "City", "Twenty", "High School", "Magic", "Aging", "Heroes", "Other Families"]

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():

    # Display the search feature on the homepage
    return render_template("index.html", len=len(columns), columns = columns)

@app.route("/search", methods=["GET","POST"])
def search():
    """Search through the database for songs """
    
    if request.method == "POST":

        # Initializes a dict witha all values false
        paramValues = dict.fromkeys(columns, False)

        chosen = False

        songs = []

        for val in columns:
            if request.form.get(val):
            # The value is selected, get songs from themes
                chosen = True
                paramValues[val] = True
                valName = val.lower().replace(" ","_")
                songs.extend(db.execute(f"SELECT * FROM themes WHERE {valName}=1"))

        # Ensure user chooses a checkbox
        if not chosen:
            return redirect("/")

        # Render table of songs
        return render_template("search.html", songs=songs)

    # Show search page
    return render_template("index.html", len=len(columns), columns=columns)
