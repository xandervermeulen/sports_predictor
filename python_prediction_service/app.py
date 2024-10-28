import dotenv as dotenv
from flask import Flask

from webservices.tennis_api_webservice import tennis_api
from webservices.tennis_data_webservice import tennis_data_api
from webservices.ufc_api_webservice import ufc_api
from webservices.ufc_data_webservice import ufc_data_api
from config.db_config import init_db

dotenv.load_dotenv(dotenv_path=".env")


def create_app():
    flask_app = Flask(__name__)
    flask_app.register_blueprint(ufc_data_api)
    flask_app.register_blueprint(tennis_data_api)
    flask_app.register_blueprint(ufc_api)
    flask_app.register_blueprint(tennis_api)
    init_db(flask_app)
    return flask_app


create_app()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='localhost', port=5000)
