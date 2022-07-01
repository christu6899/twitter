import os
config_path=os.path.abspath(os.path.dirname(__file__))
class Config:
    SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL","sqlite:///" + os.path.join(config_path,'twittor.db'))
    #SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:2J4u6vm0-@localhost:3306/demo"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'abc123'
    TWEET_PER_PAGE = 3

    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT=465
    MAIL_USE_SSL=True
    MAIL_DEFAULT_SENDER=('admin', 'christwittor689@gmail.com')
    MAIL_MAX_EMAILS=10
    MAIL_USERNAME='christwittor689'
    MAIL_PASSWORD='fzolganxpiqvdpxd'
    MAIL_SUBJECT_RESET_PASSWORD = '[Twittor] Please Reset Your Password'