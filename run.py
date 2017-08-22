# from gevent import monkey
# monkey.patch_all()

import sys

from flask_security import Security, SQLAlchemyUserDatastore, utils

from app import app, db, models, socketio

sys.setrecursionlimit(20000)
# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
security = Security(app, user_datastore)


# Create a user to test with
# @app.before_first_request
def create_user():
    # db.create_all()
    pwd = utils.hash_password('pignouf')
    user_datastore.create_user(email='xavier@mayeur.be', password=pwd)
    db.session.commit()


debug = False
for arg in sys.argv[1:]:
    if arg == '-d' or arg == '--debug':
        debug = True

certfile = 'home.mayeur.be-chain.pem'
keyfile = 'home.mayeur.be.key'
context = (certfile, keyfile)
socketio.run(app, host='0.0.0.0', port=5000, debug=debug)  # , certfile=certfile, keyfile=keyfile)
