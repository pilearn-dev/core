from flask import session

import sqlite3 as lite
import time as t
from times import stamp2relative, stamp2german
import json
from minimark import compile as mini_mark

class Message:

    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def getDetail(self, d):
        return self.__data[d]

    def getAuthor(self):
        return User(self.getDetail("poster_id"))

    def get(self):
        return self.getDetail("content")

    def isShown(self):
        return bool(self.getDetail("is_shown"))

    def formatTimestamp(self):
        date = stamp2german(self.getTimestamp())
        return date

    def getTimestamp(self):
        return self.getDetail("send_at")

    def setDetail(self, d, v):
        if self.id == -3: return
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE messages SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getInfo(self):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM messages WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                return
            return {
                "id": data["id"],
                "room_id": data["room_id"],
                "poster_id": data["poster_id"],
                "reply_id": data["reply_id"],
                "content": data["content"],
                "is_shown": data["is_shown"],
                "was_edited": data["was_edited"],
                "send_at": data["send_at"]
            }
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    def isLoggedIn(self):
        return self.id != -3

    @classmethod
    def exists(cls, id):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM messages WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def all(cls, room, no_deleted=True):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM messages WHERE room_id=? ORDER BY id DESC LIMIT 50", (room,))
            data = cur.fetchall()
            data = [Message(i["id"]) for i in data]
            return data[::-1]
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def room_new(cls, room, last_id, no_deleted=True):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if no_deleted:
                cur.execute("SELECT * FROM messages WHERE room_id=? AND id > ? AND is_shown=1", (room,last_id))
            else:
                cur.execute("SELECT * FROM messages WHERE room_id=? AND id > ?", (room,last_id))
            data = cur.fetchall()
            data = [Message(i["id"]) for i in data]
            return data
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    @staticmethod
    def toJSON(obj):
        author = obj.getAuthor()
        data = {
            "id": obj.id,
            "author": {
                "id": author.id,
                "name": author.getName(),
                "is_mod": author.isMod()
            },
            "md": obj.get(),
            "html": mini_mark(obj.get()),
            "timestamp": stamp2german(obj.getTimestamp())
        }
        return json.dumps(data)

    @classmethod
    def new(cls, room, author, msg):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO messages (room_id, poster_id, reply_id, is_shown, content, was_edited, send_at) VALUES (?, ?, 0, 1, ?, 0, ?)", (room,author.id, msg, int(t.time())))
            con.commit()
            data = cur.lastrowid
            data = Message(data)
            return data
        except lite.Error as e:
            print(e)
            return None
        finally:
            if con:
                con.close()

class MF:

    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def getDetail(self, d):
        return self.__data[d]

    def getFlagger(self):
        return User(self.getDetail("flagger"))

    def getMessage(self):
        return self.getDetail("message")

    def isHandled(self):
        return bool(self.getDetail("is_handled"))

    def setDetail(self, d, v):
        if self.id == -3: return
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE message_flags SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def toJSON(self):
        return {
            "message": self.getMessage()
        }

    def getInfo(self):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM message_flags WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                return
            return {
                "id": data["id"],
                "room_id": data["room_id"],
                "message_id": data["message_id"],
                "flagger": data["flagger"],
                "is_handled": data["is_handled"],
                "outcome": data["outcome"],
                "message": data["message"]
            }
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    @classmethod
    def exists(cls, id):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM message_flags WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def all(cls, room):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT DISTINCT message_id FROM message_flags WHERE room_id=? AND is_handled=0 ORDER BY id", (room,))
            data = cur.fetchall()
            SET = []
            for d in data:
                cur.execute("SELECT * FROM message_flags WHERE room_id=? AND is_handled=0 AND message_id=? ORDER BY id", (room,d["message_id"]))
                ddd = cur.fetchall()
                SET.append([Message(d["message_id"]), [MF(i["id"]) for i in ddd]])
            return SET[::-1]
            print(SET)
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def roomCount(cls, room):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM message_flags WHERE room_id=? AND is_handled=0", (room,))
            data = cur.fetchone()
            return data[0]
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    @classmethod
    def mark_by_msg(cls, msg, response):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE message_flags SET is_handled=1, outcome=? WHERE message_id=? AND is_handled=0", (response, msg))
            con.commit()
            data = cur.lastrowid
            data = MF(data)
            return data
        except lite.Error as e:
            print(e)
            return None
        finally:
            if con:
                con.close()

    @classmethod
    def new(cls, room, msg, flagger, message):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO message_flags (room_id, message_id, flagger, is_handled, outcome, message) VALUES (?, ?, ?, 0, 0, ?)", (room,msg,flagger.id, message))
            con.commit()
            data = cur.lastrowid
            data = MF(data)
            return data
        except lite.Error as e:
            print(e)
            return None
        finally:
            if con:
                con.close()

class Room:

    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def getName(self):
        return self.getDetail("name")

    def getDescription(self):
        return self.getDetail("description")

    def isFrozen(self):
        return bool(self.getDetail("frozen"))

    def getDetail(self, d):
        return self.__data[d]

    def setDetail(self, d, v):
        if self.id == -3: return
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE rooms SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getInfo(self):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM rooms WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                return
            return {
                "id": data["id"],
                "name": data["name"],
                "description": data["description"],
                "frozen": data["frozen"],
                "suspended": data["suspended"],
                "suspension_end": data["suspension_end"],
                "public_read": data["public_read"],
                "public_write": data["public_write"]
            }
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    def isLoggedIn(self):
        return self.id != -3

    @classmethod
    def exists(cls, id):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM rooms WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def all(cls):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM rooms")
            data = cur.fetchall()
            data = [Room(i["id"]) for i in data]
            return data
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()


class MEQ:

    @classmethod
    def get_newest(cls, room_id, ts):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM message_events WHERE (room_id=? OR room_id=0) AND id>?", (room_id,ts))
            data = cur.fetchall()
            return data
        except lite.Error as e:
            print(e)
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def room_latest(cls, room_id):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM message_events WHERE (room_id=? OR room_id=0) ORDER BY id DESC", (room_id,))
            data = cur.fetchone()
            if not data:
                return 0
            return data["id"]
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    @classmethod
    def toJSON(cls, data):
        FULL = {
            "id": data[0],
            "room_id": data[1],
            "event": data[2],
            "message_id": data[3],
            "message": json.loads(Message.toJSON(Message(data[3]))),
            "content": data[4]
        }
        return json.dumps(FULL)

    @classmethod
    def add(cls, room_id, event, msg):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO message_events (room_id, event, message_id, content, triggered_at) VALUES (?, ?, ?, ?, ?)", (room_id,event, msg.id, msg.get(), t.time()))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()



class User:

    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def isMod(self):
        return bool(self.getDetail("is_mod"))

    def isSuspended(self):
        if bool(self.getDetail("is_suspended")) and not (t.time() < self.getDetail("suspension_end")):
            self.setDetail("is_suspended", False)
            return False
        return self.getDetail("is_suspended")

    def getSuspensionReason(self):
        return self.getDetail("suspension_reason")

    def formatSuspensionEnd(self):
        date = stamp2relative(self.getDetail("suspension_end"))
        return date

    def getSuspensionEnd(self):
        date = stamp2german(self.getDetail("suspension_end"))
        return date

    def getName(self):
        return self.getDetail("name")

    def getAssocId(self):
        return self.getDetail("assoc_id")

    def mayPost(self):
        return not(self.isSuspended()) and bool(self.getDetail("may_talk"))

    def getDetail(self, d):
        return self.__data[d]

    def setDetail(self, d, v):
        if self.id == -3: return
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE user SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getInfo(self):
        if self.isLoggedIn():
            try:
                con = lite.connect('chat.db')
                con.row_factory = lite.Row
                cur = con.cursor()
                cur.execute("SELECT * FROM user WHERE id=?", (self.id, ))
                data = cur.fetchone()
                if data is None:
                    return
                return {
                    "id": data["id"],
                    "assoc_id": data["assoc_id"],
                    "name": data["name"],
                    "may_talk": data["may_talk"],
                    "is_mod": data["is_mod"],
                    "is_suspended": data["is_suspended"],
                    "suspension_reason": data["suspension_reason"],
                    "suspension_end": data["suspension_end"]
                }
            except lite.Error as e:
                #raise lite.Error from e
                raise e
            finally:
                if con:
                    con.close()
        else:
            return {
                "id": -3,
                "assoc_id": 0,
                "name": "<anonym>",
                "may_talk": 0,
                "is_mod": 0,
                "is_suspended": 0,
                "suspension_reason": "",
                "suspension_end": 0
            }

    def isLoggedIn(self):
        return self.id != -3

    @classmethod
    def blank(cls):
        return cls(-3)

    @classmethod
    def exists(cls, id):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM user WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def from_assoc_id(cls, id):
        try:
            con = lite.connect('chat.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM user WHERE assoc_id=?", (id,))
            data = cur.fetchone()
            if data is not None:
                return cls(data["id"])
            return cls.blank()
        except lite.Error as e:
            print(e)
            return cls.blank()
        finally:
            if con:
                con.close()


def require_login():
    return session.get('login') is None


def getCurrentUser():
    if require_login():
        return User.blank()
    else:
        return User.from_assoc_id(session.get('login'))
