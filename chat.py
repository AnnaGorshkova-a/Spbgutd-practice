from flask import Blueprint, render_template, request, session, url_for
from flask_login import login_required, current_user
from werkzeug.utils import redirect

from database.db import db
from database.models import Room

chat_blueprint = Blueprint('chat', __name__)


@chat_blueprint.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    if request.method == 'GET' and current_user.username is None:
        return redirect(url_for('auth.login'))

    username = current_user.username

    rooms = Room.query.all()
    rooms_names = []
    for room in rooms:
        rooms_names.append(room.name)

    room = request.args.get('room', default=rooms_names[0], type=str)
    session['room'] = room
    return render_template('chat.html', session=session, rooms=rooms_names, selectedRoom=room)