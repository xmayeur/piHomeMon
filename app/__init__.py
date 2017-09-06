"""
https://www.tutorialspoint.com/flask/flask_quick_guide.htm
https://www.w3schools.com/html/default.asp
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xii-facelift
https://getbootstrap.com/docs/3.3/
https://pythonhosted.org/Flask-Security/quickstart.html
"""
from flask import Flask
from flask_socketio import SocketIO

# Create app
app = Flask(__name__)
app.config.from_object('config')
socketio = SocketIO(app, async_mode="gevent")

# Create database connection object
# db = SQLAlchemy(app)
from app import views
