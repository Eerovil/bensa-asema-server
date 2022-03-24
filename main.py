from flask import Flask, render_template, request
from sqlitedict import SqliteDict
import os
import datetime
import random

from typing import List, Optional
from pydantic import BaseModel

data_folder = 'data'

app = Flask(__name__, static_url_path='/static', static_folder=data_folder, template_folder='')
logger = app.logger

messages_table = SqliteDict(os.path.join(data_folder, 'main.db'), tablename="messages", autocommit=True)
main_table = SqliteDict(os.path.join(data_folder, 'main.db'), tablename="main", autocommit=True)


class Message(BaseModel):
    id: int
    message: str
    last_used: datetime.datetime


def run_tick():
    active_message = main_table.get('active_message')
    if not active_message and len(list(messages_table.keys())) > 0:
        messages_by_last_used = list(sorted(messages_table.values(), key=lambda x: x.last_used))
        logger.info(f"Messages by last used: {messages_by_last_used}")
        if len(messages_by_last_used) > 1:
            messages_by_last_used = messages_by_last_used[:-1]
        main_table['active_message'] = random.choice(messages_by_last_used).id
        message = messages_table[main_table['active_message']]
        message.last_used = datetime.datetime.now()
        messages_table[main_table['active_message']] = message
        logger.info("Selected new active message: %s", message.message)


@app.route("/")
def hello_world():
    return render_template("index.html", title = 'App')


@app.route("/message", methods=['GET'])
def get_message():
    run_tick()

    ack = request.args.get('ack')

    active_message = main_table.get('active_message')

    if ack:
        logger.info("Acked message: %s", messages_table[active_message].message)
        if str(active_message) == str(ack):
            main_table['active_message'] = None

    if active_message:
        logger.info("Returning message: %s", messages_table[active_message].message)
        return dict(messages_table[active_message])
    return ''


@app.route("/messages", methods=['GET'])
def get_messages():
    ret = {}
    for k, v in messages_table.items():
        ret[k] = dict(v)
    return ret


@app.route("/messages", methods=['POST'])
def post_message():
    message = request.form.get('message')
    if not message:
        return '', 400
    messages_table[str(len(messages_table))] = {'message': message}
    return '', 200
