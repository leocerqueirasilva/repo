# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_migrate import Migrate
from sys import exit
from decouple import config
from flask import Flask, render_template, request, url_for, jsonify
import json
from instagrapi import Client
from apps.config import config_dict
from apps import create_app, db
from os.path import abspath
from apps import db
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from apps import db
from sqlalchemy import create_engine
from sqlalchemy.engine import reflection
from apps.home.models import Account
import requests
from instagrapi.mixins.challenge import ChallengeChoice
from instagrapi.mixins.challenge import ChallengeRequired
from instagrapi.mixins.challenge import ChallengeResolveMixin
import instagrapi

from instagrapi.exceptions import (
    ChallengeError,
    ChallengeRedirection,
    ChallengeRequired,
    ChallengeSelfieCaptcha,
    ChallengeUnknownStep,
    LegacyForceSetNewPasswordForm,
    RecaptchaChallengeForm,
    SelectContactPointRecoveryForm,
    SubmitPhoneNumberForm,
)





app = Flask(__name__, template_folder='templates')

@app.route("/add_account")
def add_page_account():
    return render_template("add_account.html")

@app.route("/medialike")
def medialike():
    return render_template("medialiketest.html")

@app.route("/admin")
def admin():
    return render_template("admin.html", accounts=accounts)

@app.route("/tablescopy")
def tables_users():
    return render_template("tablescopy.html", accounts=accounts)







# WARNING: Don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:

    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
Migrate(app, db)

if DEBUG:
    app.logger.info('DEBUG       = ' + str(DEBUG))
    app.logger.info('Environment = ' + get_config_mode)
    app.logger.info('DBMS        = ' + app_config.SQLALCHEMY_DATABASE_URI)




## Database e accounts

@app.route("/add_account", methods=["POST"])
def add_account():
    cl = Client()
    cl.set_locale('pt_BR')
    cl.set_timezone_offset(-3 * 60 * 60)
    cl.set_country_code(55)
    new_account = request.get_json()
    accountput = Account(username=new_account["new_username"], password=new_account["new_password"])
    cl.login(accountput.username, accountput.password)
    configs = cl.get_settings()
    account = Account(username=new_account["new_username"], password=new_account["new_password"], setting=str(configs))
    db.session.add(account)
    db.session.commit()
    

    return 'Ok'


#Get and show accounts

@app.route("/get_accounts")
def get_accounts():
    accounts = Account.query.all()
    return jsonify([account.to_dict() for account in accounts])



@app.route('/delete_account/<username>', methods=['DELETE'])
def delete_account(username):
    session = db.session
    account = session.query(Account).filter_by(username=username).first()
    session.delete(account)
    session.commit()
    return jsonify({'message': 'Account deleted'}), 200
























#Comment menssage

@app.route("/call_comment", methods=['POST'])
def call_comment():
    accounts = Account.query.all()
    for account in accounts:
        settings = eval(account.setting)
        cl = Client(settings)
        # Retrieve the account information from the database
        # Pass the username and password to the cl.login function
        cl.login(account.username, account.password)
        media_url = request.form.get('media_url')
        media_id = cl.media_id(cl.media_pk_from_url(media_url))
        comment_text = request.form.get('comment_text')
        comment = cl.media_comment(media_id, str(comment_text))
        return 'Ok'

## Direct menssage

@app.route("/send_direct", methods=["POST"])
def send_direct():
    accounts = Account.query.all()
    for account in accounts:
        settings = eval(account.setting)
        cl = Client(settings)
        # Retrieve the account information from the database
        # Pass the username and password to the cl.login function
        cl.login(account.username, account.password)
        recipients = request.form.get('recipients')
        user_id = cl.user_id_from_username(recipients)
        message = request.form.get('message')
        # Use the cl.direct_send function to send a direct message
        cl.direct_send(message, user_ids=[user_id])
        return 'Ok'



## Like media





@app.route("/call_like", methods=['POST'])
def call_like():
    accounts = Account.query.all()
    for account in accounts:
        settings = eval(account.setting)
        cl = Client(settings)
        cl.login(account.username, account.password)
        media_url = request.form.get('media-url')
        media_id = cl.media_id(cl.media_pk_from_url(media_url))
        cl.media_like(media_id)
        
        

        return 'Ok'


# Follow user
@app.route("/user_follow", methods=['POST'])
def user_follow():
    
    accounts = Account.query.all()
    for account in accounts:
        settings = eval(account.setting)
        cl = Client(settings)
        cl.login(account.username, account.password)
        username = request.form.get('username')
        user_id = cl.user_id_from_username(username)
        follow = cl.user_follow(int(user_id))
        return 'Ok'

@app.route("/like_stories", methods=['POST'])
def like_stories():
    story_url = request.json['storyUrl']
    accounts = Account.query.all()
    for account in accounts:
        settings = eval(account.setting)
        cl = Client(settings)
        cl.login(account.username, account.password)
        id_storie = cl.story_pk_from_url(story_url)
        cl.story_like(id_storie)
        return jsonify({'message': 'success'})


        

        








1

## Test like media


@app.route("/test_like", methods=['GET', 'POST'])
def testlike():
    # Login to Instagram
    login_url = 'https://www.instagram.com/accounts/login/'
    username = 'paulonunesjr83'
    password = 'paulo123'
    session = requests.Session()
    session.headers.update({'Referer': 'https://www.instagram.com/',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'})


    # Get the CSRF token and the session ID
    session.get('https://www.instagram.com/')
    csrftoken = session.cookies.get_dict().get('csrftoken')

    # Login to Instagram
    login_data = {'username': username, 'password': password}
    session.headers.update({'X-CSRFToken': csrftoken})
    login_response = session.post(login_url, data=login_data, allow_redirects=True)
    print(login_response)
    print(login_response.content)


    # Like a media
    media_url = 'https://www.instagram.com/p/CoAwXMlAOB1'
    media_id = media_url.split('/')[-2]
    like_url = f'https://www.instagram.com/web/likes/{media_id}/like/'
    like_data = {'_method': 'post'}
    session.headers.update({'Referer': media_url})
    like_response = session.post(like_url, data=like_data)

    # Check if the like was successful
    if like_response.status_code == 200:
        return "Media liked successfully!"
    else:
        return "Error liking media. Response code: {}".format(like_response.status_code)








if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
    app.run(debug=True)
    

