from flask import Flask, render_template, request, url_for, jsonify
import json






from instagrapi import Client


app = Flask(__name__)


@app.route("/")
def homepage():
  
    return render_template("homepage.html")

@app.route("/admin")
def admin():
    return render_template("admin.html", accounts=accounts)


@app.route("/new")
def new1():
    return render_template("new.html")

@app.route("/like_media")
def like_media():
    return render_template("like_media.html")

@app.route("/comment")
def comment():
    return render_template("comment.html")

@app.route("/add_account")
def account():
    return render_template("add_account.html")

@app.route("/add_account", methods=["POST"])
def add_account():
    new_account = request.get_json()
    accounts.append({"username": new_account["new_username"], "password": new_account["new_password"]})
    return 'Ok'

@app.route("/edit_account/<username>", methods=["PUT","PATCH"])
def edit_account(username):
    data = request.form
    # Find the account in the accounts list
    for account in accounts:
        if account["username"] == username:
            account["password"] = data["password"]
    return "Account edited"

# Route to handle the delete button and delete an existing account
@app.route("/delete_account/<username>", methods=["DELETE"])
def delete_account(username):
    # Find the account in the accounts list and remove it
    for i, account in enumerate(accounts):
        if account["username"] == username:
            del accounts[i]
            break
    return "Account deleted"




accounts = []

# Direct Message
@app.route("/call_user_id", methods=["POST"])
def call_user_id():
    
    for account in accounts:
        cl = Client()
        cl.login(account["username"], account["password"])
        data = request.get_json()
        user_id = cl.user_id_from_username(data['username'])
        user_ids = [user_id]
        cl.direct_send(data['message'], user_ids=user_ids)
    return 'Ok'

# Comment message

@app.route("/call_comment", methods=['POST'])
def call_comment():
        cl = Client()
        cl.login("leocerqueira56", "Dork8421!")
        media_url = request.form.get('media_url')
        print(media_url)
        media_id = cl.media_id(cl.media_pk_from_url(media_url))
        comment_text = request.form.get('comment_text')
        comment = cl.media_comment(media_id, str(comment_text))
        return 'Ok'

@app.route("/int_id")
def call_int_id():
    cl = Client()
    cl.login("leocerqueira56", "Dork8421!")
    user_id = cl.user_id_from_username("adw0rd")
    medias = cl.user_medias(user_id, 20)

        






# Put site in air
if __name__ == "__main__":
    app.run(debug=True)