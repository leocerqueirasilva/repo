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
from sqlalchemy import create_engine
from sqlalchemy.engine import reflection
from apps.home.models import Account, LikeHistory, CommentHistory, FollowHistory, VoteHistory
import requests
from instagrapi.mixins.challenge import ChallengeChoice
from instagrapi.mixins.challenge import ChallengeRequired
from instagrapi.mixins.challenge import ChallengeResolveMixin
import instagrapi
import os

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
from flask import Flask, request
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
from flask_mail import Mail
from flask_mail import Message
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



app = Flask(__name__, template_folder='templates')
mail = Mail(app)

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


app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'leocerqueirasilva67@gmail.com'
app.config['MAIL_PASSWORD'] = 'Dork8421!wowo2012'

@app.route('/send_email', methods=['POST'])
def send_email():
    num_accounts = request.form.get('num-accounts')
    media_url = request.form.get('media-url')
    vote_option = request.form.get('vote-option')
    
    print("Número de contas:", num_accounts)
    print("Media URL:", media_url)
    print("Vote Option:", vote_option)
    
    # Configurações do servidor SMTP da Hostinger
    smtp_server = "smtp.hostinger.com"
    smtp_port = 465
    email_address = "polls@argoncertificate.shop"  # Substitua pelo seu endereço de email corporativo
    email_password = "Dork8421!"  # Substitua pela senha do seu email corporativo

    
    # Configuração da mensagem
    subject = "Votação automática"
    message = f"Votação automática realizada com sucesso.\nNúmero de contas: {num_accounts}\nURL da mídia: {media_url}\nOpção de voto: {vote_option}"

    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = "leocerqueirasilva67@gmail.com"  # Substitua pelo e-mail do destinatário
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain', 'utf-8'))  # Adicione o parâmetro 'utf-8' aqui

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(email_address, email_password)
            server.sendmail(email_address, "leocerqueirasilva67@gmail.com", msg.as_string().encode('utf-8'))  # Adicione .encode('utf-8') aqui
        print("E-mail enviado com sucesso.")
    except Exception as e:
        print("Erro ao enviar o e-mail:", e)
        

    # Após a solicitação bem-sucedida, adicione o registro ao histórico
    history_record = VoteHistory(media_url=media_url, vote_option=vote_option, num_accounts=num_accounts)
    db.session.add(history_record)
    db.session.commit()

    return jsonify(success=True)


from flask import jsonify

@app.route('/get_last_request_date')
def get_last_request_date():

    # Obtenha o último registro de cada tabela
    last_like = LikeHistory.query.order_by(LikeHistory.timestamp.desc()).first()
    last_comment = CommentHistory.query.order_by(CommentHistory.timestamp.desc()).first()
    last_follow = FollowHistory.query.order_by(FollowHistory.created_at.desc()).first()
    last_vote = VoteHistory.query.order_by(VoteHistory.timestamp.desc()).first()

    # Obtenha o carimbo de data/hora de cada último registro
    last_like_timestamp = last_like.timestamp if last_like else None
    last_comment_timestamp = last_comment.timestamp if last_comment else None
    last_follow_timestamp = last_follow.created_at if last_follow else None
    last_vote_timestamp = last_vote.timestamp if last_vote else None

    # Encontre a data mais recente entre os registros
    last_request_date = max(filter(None, [last_like_timestamp, last_comment_timestamp, last_follow_timestamp, last_vote_timestamp]))
    print(last_request_date)
    # Retorne a data da última solicitação como uma resposta JSON
    return jsonify(last_request_date=last_request_date.isoformat())

    

@app.route('/get_total_requests')
def get_total_requests():
    # Obtenha o número total de solicitações de cada tabela
    total_likes = LikeHistory.query.count()
    total_comments = CommentHistory.query.count()
    total_follows = FollowHistory.query.count()
    total_votes = VoteHistory.query.count()

    # Some todos os totais
    total_requests = total_likes + total_comments + total_follows + total_votes

    # Retorne a soma total como uma resposta JSON
    return jsonify(total_requests=total_requests)

    

@app.route('/get_vote_history', methods=['GET'])
def get_vote_history():
    vote_history = VoteHistory.query.order_by(VoteHistory.timestamp.desc()).all()
    return jsonify([{
        'id': record.id,
        'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'media_url': record.media_url,
        'vote_option': record.vote_option,
        'num_accounts': record.num_accounts
    } for record in vote_history])



@app.route('/get_history_like', methods=['GET'])
def get_history():
    history_records = LikeHistory.query.order_by(LikeHistory.timestamp.desc()).all()
    history_data = []

    for record in history_records:
        history_data.append({
            'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'media_url': record.media_url,
            'num_likes': record.num_accounts
        })

    return jsonify(history_data)


@app.route("/get_history_comment", methods=['GET'])
def get_comment_history():
    history = CommentHistory.query.order_by(CommentHistory.timestamp.desc()).all()
    history_list = []
    for record in history:
        history_list.append({
            'timestamp': record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'media_url': record.media_url,
            'num_comments': record.num_comments,
            'comment_text': record.comment_text
        })

    return jsonify(history_list)


@app.route("/get_history_follow", methods=['GET'])
def get_history_follow():
    history = FollowHistory.query.order_by(FollowHistory.created_at.desc()).all()
    history_list = []

    for record in history:
        history_list.append({
            'timestamp': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'target_username': record.target_username,
            'num_followers': record.num_followers
        })

    return jsonify(history_list)




@app.route("/comment_form")
def comment_form():
    accounts = Account.query.all()
    return render_template("autocomment.html", accounts=accounts)






#Comment menssagee

@app.route("/call_comment", methods=['POST'])
def call_comment():
    accounts = json.loads(request.form.get('accounts'))
    media_url = request.form.get('media_url')
    comment_text = request.form.get('comment_text')
    progress = json.loads(request.form.get('progress'))

    for username in accounts:
        account = Account.query.filter_by(username=username).first()
        if account:
            settings = eval(account.setting)
            cl = Client(settings)
            cl.login(account.username, account.password)
            media_id = cl.media_id(cl.media_pk_from_url(media_url))
            cl.media_comment(media_id, comment_text)

    if progress == 0:
        # Adicionando o registro ao histórico de comentários
        history_record = CommentHistory(
            media_url=media_url,
            num_comments=len(accounts),
            comment_text=comment_text
        )
        db.session.add(history_record)
        db.session.commit()

    return jsonify(success=True)






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
    media_url = request.form.get('media-url')
    num_accounts_to_like = int(request.form.get('num-accounts'))

    all_accounts = Account.query.all()
    accounts = random.sample(all_accounts, num_accounts_to_like)

    progress = 0
    for account in accounts:
        settings = eval(account.setting)
        cl = Client(settings)
        cl.login(account.username, account.password)
        media_id = cl.media_id(cl.media_pk_from_url(media_url))
        cl.media_like(media_id)
        progress += 1
        print(account)

    # Após a solicitação de curtidas bem-sucedida, adicione o registro ao histórico
    history_record = LikeHistory(media_url=media_url, num_accounts=num_accounts_to_like)
    db.session.add(history_record)
    db.session.commit()

    return jsonify(progress=progress, total=num_accounts_to_like)

    


@app.route("/user_follow", methods=['POST'])
def user_follow():
    num_followers = int(request.form.get('num-followers'))
    username = request.form.get('username')

    accounts = Account.query.all()
    selected_accounts = random.sample(accounts, min(num_followers, len(accounts)))

    progress = 0
    for account in selected_accounts:
        settings = eval(account.setting)
        cl = Client(settings)
        cl.login(account.username, account.password)
        user_id = cl.user_id_from_username(username)
        follow = cl.user_follow(int(user_id))
        progress += 1
        print(account)

    # Após a solicitação de seguir usuário bem-sucedida, adicione o registro ao histórico
    history_record = FollowHistory(target_username=username, num_followers=num_followers)
    db.session.add(history_record)
    db.session.commit()

    return jsonify(progress=progress, total=num_followers)

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
        


        

        

@app.route("/test_vote", methods=['GET', 'POST'])
def testvote():
    # Login to Instagram
    login_url = 'https://www.instagram.com/accounts/login/'
    username = 'melissadorosario8310'
    password = 'joaolucas11'
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
    if login_response.status_code == 200:
        return "Vote submitted successfully!"
    else:
        return "Error submitting vote. Response code: {}".format(login_response.status_code)

    """  # Vote in the poll
    story_url = 'https://www.instagram.com/stories/livescore/3035819740852460379/'
    poll_url = 'https://www.instagram.com/web/stories/17894204059062139/vote/'
    poll_id = story_url.split('/')[-2]
    vote_option = '1' # replace with the index of the desired vote option
    vote_data = {'vote': vote_option}
    session.headers.update({'Referer': story_url})
    vote_response = session.post(poll_url, data=vote_data)
    print(vote_response) 

    # Check if the vote was successful
    if vote_response.status_code == 200:
        return "Vote submitted successfully!"
    else:
        return "Error submitting vote. Response code: {}".format(vote_response.status_code) """









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
     app.run(debug=True, host="0.0.0.0", port=os.getenv("PORT", default=5000))
    


### teste