from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

#config
from config import LocalDevelopmentConfig

#models
from models import User, Role

#Auth
from flask_security import Security, SQLAlchemySessionUserDatastore


url = "https://cyberinbornbrowsers.bhanani.repl.co"

import datetime
import humanize
def h(x):
    y = x.split(".")
    timestamp = datetime.datetime.strptime(y[0], "%Y-%m-%d %H:%M:%S")
    timestamp_utc = timestamp
    return humanize.naturaltime(timestamp_utc)


app = None

def create_app():
    
    app = Flask(__name__, template_folder="templates", static_folder="visualizations")
    db = SQLAlchemy()
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    # app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite3"
    api = Api(app)
    app.api = api
    app.app_context().push()
    user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
    security = Security(app, user_datastore)
    app.jinja_env.globals.update(h=h)
    return app

app = create_app()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
from controllers import *
from api import *

if __name__ == "__main__":
    # db.create_all()
    app.run("0.0.0.0", debug=True)
    
    
    
# @auth.verify_password
# def verify_password(username, password):
#     user = User.query.filter_by(user_name = username).first()
#     if user is not None and \
#             check_password_hash(user.user_password, password):
#         return user.id

# @app.route("/logout", methods=["GET"])
# def logout():
#     return "Logout", 401

# @app.route("/signup", methods = ["GET", "POST"])
# def signup():
#     if request.method == 'GET':
#         return render_template("signup.html", template_folder = "templates"), 200
#     elif request.method == 'POST':
#         (user_name, user_password) = (request.form['user_name'], request.form['user_password'])
#         user = {
#             "user_name": user_name,
#             "user_password": user_password
#         }
#         x = requests.post(url+"/api/user", data = user)
#         return redirect(url_for('trackers'))
        