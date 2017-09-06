# --->!/usr/bin/env python
# -*- coding: utf-8 -*-
# from gevent import monkey
# monkey.patch_all()

import sys

# from flask_security import Security, SQLAlchemyUserDatastore, utils
from app import app, socketio


# from app import db, models


def main():
    sys.setrecursionlimit(20000)
    # Setup Flask-Security
    # user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)

    # security = Security(app, user_datastore)
    
    # Create a user to test with
    # @app.before_first_request
    # def create_user():
    #     # db.create_all()
    #     pwd = utils.hash_password('pignouf')
    #     user_datastore.create_user(email='xavier@mayeur.be', password=pwd)
    #     db.session.commit()
    
    debug = False
    for arg in sys.argv[1:]:
        if arg == '-d' or arg == '--debug':
            debug = True

    socketio.run(app, host='0.0.0.0', port=5000, debug=debug)


if __name__ == '__main__':
    main()
