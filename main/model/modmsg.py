# coding: utf-8
import os, json, re, time
import secrets
import sqlite3 as lite
from model import user as muser
from controller import times as ctimes

class UserMsgThread:

    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def getDetail(self, d):
        return self.__data[d]

    def setDetail(self, d, v):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE modmsg_threads SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getMessages(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM modmsg_messages WHERE thread_id=?", (self.id,))
            return [UserMsg(i["id"]) for i in cur.fetchall()]
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def isClosed(self):
        return self.getDetail("closed")

    def getContacted(self):
        return muser.User(self.getDetail("contacted_user"))

    def getInitiator(self):
        return muser.User(self.getDetail("initiated_by"))

    def getInfo(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM modmsg_threads WHERE id=?", (self.id,))
            data = cur.fetchone()
            if data is None:
                raise ValueError("UserMsgThread not found with id " + str(self.id))
            return {
                "id": data['id'],
                "initiated_by": data['initiated_by'],
                "last_activity": data['last_activity'],
                "contacted_user": data['contacted_user'],
                "closed": bool(data['closed'])
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
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM modmsg_threads WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()


    @classmethod
    def new(cls, from_, to):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO modmsg_threads (initiated_by, last_activity, contacted_user, closed) VALUES (?, ?, ?, 0)", (from_, time.time(), to))
            con.commit()
            data = cur.lastrowid
            return UserMsgThread(data)
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()


class UserMsg:

    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def getDetail(self, d):
        return self.__data[d]

    def setDetail(self, d, v):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE modmsg_messages SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()


    def getSubmitter(self):
        return muser.User(self.getDetail("submitted_by"))

    def getReceiver(self):
        return muser.User(self.getDetail("message_receiver"))

    def getContent(self):
        return self.getDetail("content")

    def getSubmissionTime(self):
        dt = int(self.getDetail("submission_time"))
        return [dt, ctimes.stamp2german(dt), ctimes.stamp2shortrelative(dt, False)]

    def getSuspensionLength(self):
        dt = self.getDetail("suspension_length")
        if not dt:
            return [0, "0", "0"]
        dt = int(dt)
        return [dt, ctimes.duration2text(dt), ctimes.duration2shorttext(dt)]

    def getTemplateName(self, alt=""):
        tid = self.getDetail("template")
        if tid == 0:
            return alt
        try:
            con = lite.connect('databases/pilearn.db')
            cur = con.cursor()
            cur.execute("SELECT title FROM modmsg_templates WHERE id=?", (tid,))
            data = cur.fetchone()
            if data:
                return data[0]
            return alt
        except lite.Error as e:
            return alt
        finally:
            if con:
                con.close()

    def getInfo(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM modmsg_messages WHERE id=?", (self.id,))
            data = cur.fetchone()
            if data is None:
                raise ValueError("UserMsgThread not found with id " + str(self.id))
            return {
                "id": data['id'],
                "submitted_by": data['submitted_by'],
                "submission_time": data['submission_time'],
                "message_receiver": data['message_receiver'],
                "content": data['content'],
                "suspension_length": data['suspension_length'],
                "template": data['template'],
                "closed_thread": bool(data['closed_thread'])
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
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM modmsg_messages WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def new(cls, thread, submittor, receiver, content, template=0):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO modmsg_messages (thread_id, submitted_by, submission_time, message_receiver, content, suspension_length, template, closed_thread) VALUES (?, ?, ?, ?, ?, 0, ?, 0)", (thread, submittor,time.time(), receiver, content, template))
            con.commit()
            data = cur.lastrowid
            return UserMsg(data)
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()


def getTemplates():
    try:
        con = lite.connect('databases/pilearn.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM modmsg_templates WHERE may_be_used=1")
        RETURN_DATA = []

        data = cur.fetchall()
        for d in data:
            RETURN_DATA.append({
                "id": d[0],
                "title": d[1],
                "content": d[2],
                "may_be_used": bool(d[3])
            })

        return RETURN_DATA
    except lite.Error as e:
        return []
    finally:
        if con:
            con.close()

def getTemplateById(id):
    try:
        con = lite.connect('databases/pilearn.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM modmsg_templates WHERE id=?", (id,))

        d = cur.fetchone()
        return {
            "id": d[0],
            "title": d[1],
            "content": d[2],
            "may_be_used": bool(d[3])
        }
    except lite.Error as e:
        return {}
    finally:
        if con:
            con.close()
