import secrets

from flask import Flask, session
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO, join_room, emit, leave_room

from database.db import initialize_db
from database.models import User
from flask_session import Session


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = secrets.token_urlsafe(32)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    Session(app)
    initialize_db(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from database.models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from chat import chat_blueprint
    app.register_blueprint(chat_blueprint)

    return app


app = create_app()
socketio = SocketIO(app, manage_session=False, cors_allowed_origins="*")


@socketio.on('join', namespace='/chat')
def join(data):
    username = current_user.username
    room = session.get('room')
    join_room(room)
    emit('status', {'msg': username + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(data):
    room = session.get('room')
    username = current_user.username
    emit('message', {'msg': username + ' : ' + data['msg']}, room=room)


@socketio.on('left', namespace='/chat')
def left(data):
    room = session.get('room')
    username = current_user.username
    leave_room(room)
    session.clear()
    emit('status', {'msg': username + ' has left the room.'}, room=room)


if __name__ == '__main__':
    socketio.run(app, debug=True)
