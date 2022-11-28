from flask import Flask, flash, redirect, render_template, request, session
from datetime import timedelta
from flask_session import Session
from helpers import login_required
import helpers

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

@app.route("/")
@login_required
def index():
    return redirect("friends")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        #SMS code request
        if "phone-number" in request.form:
            phone_number = request.form.get("phone-number")

            #check if letters in phone number string
            if any(c.isalpha() for c in phone_number):
                flash("Invalid phone number")
                return render_template("login.html")

            response = helpers.get_sms_code(phone_number)
            #if SMS request was succesfull
            if response[0]:
                return render_template("login.html", sms_sent=True, vonageRequestId=response[1])
            else:
                flash("Couldn't request sms code")
                return render_template("login.html")

        #SMS code submit
        elif "sms-code" in request.form:
            sms_code = request.form.get("sms-code")

            if len(sms_code) != 6:
                flash("Invalid format sms code")
                return render_template("login.html")
            try:
                int(sms_code)
            except:
                flash("Invalid format sms code")
                return render_template("login.html")

            vonageRequestId = request.form.get("vonageRequestId")
            response = helpers.submit_sms_code(sms_code, vonageRequestId)
            #if sms code was correct
            if response[0]:
                session["auth_token"] = response[1]
                session["refresh_token"] = response[2]
                session["uid"] = response[3]
                return redirect("/")
            else:
                flash(response[1])
                return render_template("login.html")
        else:
            flash("Invalid request arguments")
            return render_template("login.html")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("User was logged out successfully")
    return redirect("/")

def get_feed(feed_type):
    if request.method == "POST":
        #maybe i can make this code more convinient
        if "add-comment" in request.form and "user-id" in request.form:
            comment = request.form.get("add-comment")
            userId = request.form.get("user-id")

            if helpers.comment_on_post(userId, comment, session["auth_token"]):
                flash("Comment added")
            else:
                flash("Comment couldn't be added")
        elif "friend-request" in request.form and feed_type == "discovery":
            fr_uid = request.form.get("friend-request")
            response = helpers.send_friend_request(fr_uid, session["auth_token"])
            if response:
                flash("Friend request sent!")
            else:
                flash("Friend request couldn't be sent")
    if feed_type == "friends":
        response = helpers.get_friends_feeds(session["auth_token"])
    else:
        response = helpers.get_discovery_feeds(session["auth_token"])

    if response[0] ==  False:
        refresh_response = helpers.get_refreshed_token(session["refresh_token"])
        if refresh_response[0]:
            session["auth_token"] = refresh_response[1]
            session["refresh_token"] = refresh_response[2]
            return redirect(f"/{feed_type}")
        else:
            flash("Couldn't get feed, try later or/and logging in and out.")

    return render_template("feed.html", response=response, uid=session["uid"], get_location=helpers.get_location, feed_type=feed_type)


@app.route("/friends", methods=["GET", "POST"])
@login_required
def friends():
    return get_feed("friends")

@app.route("/discovery", methods=["GET", "POST"])
@login_required
def discovery():
    return get_feed("discovery")
