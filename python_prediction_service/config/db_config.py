import os

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQL_DB_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Create all database tables
    with app.app_context():
        # Create all database tables
        db.create_all()
    return 'Database initialized'
