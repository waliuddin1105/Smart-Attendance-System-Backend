from api import app, celery
from flask_mail import Message
import ssl
import smtplib
import redis
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from api import config_parser

def is_redis():
    try:
        redis_url = app.config.get('CELERY_BROKER_URL', "redis://localhost:6379/0")
        if '://' in redis_url:
            redis_url = redis_url.split("://")[1]
        if '/' in redis_url:
            redis_url = redis_url.split('/')[0]
        if ':' in redis_url:
            host, port = redis_url.split(':')
        else:
            host = redis_url
            port = 6379

        port = int(port)
        r = redis.Redis(host = host, port = port, socket_connect_timeout=1, socket_timeout=1)
        r.ping()
        return True
    except(redis.ConnectionError, Exception) as e:
        return {"Error":f"{e}"}
    
sender_email = config_parser.get('email', 'SENDER_EMAIL')
password = config_parser.get('email', 'MAIL_PASSWORD')
mail_server = config_parser.get('email', 'MAIL_SERVER')
mail_port = config_parser.get('email', 'MAIL_PORT')

def send_mail(recipient):
    body = '''Have a good day
    Thank You!'''

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = "Test Mail"
    message["Bcc"] = recipient  #this means blind carbon copy, which means that if we send mass emails, the recipients wont be able to se eother email adresses to whom we have also sent the emails at the same time
    
    message.attach(MIMEText(body, "plain"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(mail_server, mail_port, context=context) as server:
            server.login(sender_email, password)
            print("Sending mail")
            server.sendmail(sender_email, recipient, message.as_string())
            server.quit()
            print('Mail sent')

    except Exception as e:
        print(f"Error sending mail:{e}")

def send_direct_mail(recipient):
    try:
        send_mail(recipient)
    except Exception as e:
        print(f"Direct email sending error:{e}")

@celery.task
def send_email_task(recipient):
    if is_redis():
        print("sending mail via redis")
        send_mail(recipient)
    else:
        print("Sending mail without redis/celery")
        send_direct_mail(recipient)



    