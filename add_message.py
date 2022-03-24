from sqlitedict import SqliteDict
import os
import datetime
import logging

from main import Message

from pydantic import BaseModel

data_folder = 'data'

logger = logging.getLogger(__name__)

messages_table = SqliteDict(os.path.join(data_folder, 'main.db'), tablename="messages", autocommit=True)


if __name__ == "__main__":
    new_message = input("Enter new message: ")
    new_message_id = len(list(messages_table.keys())) + 1
    messages_table[new_message_id] = Message(id=new_message_id, message=new_message, last_used=datetime.datetime.now())
