from flask import Flask
from data import db_session
from data.restaurant import Rest


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/restaurants.db")
    restaurant = Rest()
    db_sess = db_session.create_session()
    app.run()


if __name__ == '__main__':
    main()