# coding: utf-8
import os, json
import secrets
import sqlite3 as lite
from flask import request, session, url_for
from sha1 import sha1
from main.model import user as muser
import time

class Response:
    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def getDetail(self, d):
        return self.__data[d]

    def setDetail(self, d, v):
        if self.id == -3: return
        try:
            con = lite.connect('databases/helpdesk.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE responses SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def getMessage(self):
        return self.getDetail("message")

    def isOfficial(self):
        return self.getDetail("official")

    def getPoster(self):
        return muser.User.from_id(self.getDetail("poster"))

    def getInfo(self):
        try:
            con = lite.connect('databases/helpdesk.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM responses WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                return
            return {
                "id": data['id'],
                "ticket_id": data["ticket_id"],
                "message": data['message'],
                "poster": data['poster'],
                "official": bool(data['official'])
            }
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    @classmethod
    def new(cls, tickid, message, official, poster):
        try:
            con = lite.connect('databases/helpdesk.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO responses (ticket_id, message, official, poster) VALUES (?, ?, ?, ?)", (tickid, message, 1 if official else 0, poster))
            con.commit()
            return cur.lastrowid
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def exists(cls, id):
        try:
            con = lite.connect('databases/helpdesk.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM responses WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def getAll(cls, tid):
        try:
            con = lite.connect('databases/helpdesk.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM responses WHERE ticket_id=? ORDER BY id", (tid, ))
            data = cur.fetchall()
            l = list(map(lambda x:Response(x[0]), data))
            return l
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def get_by_user(cls, user, tid):
        try:
            con = lite.connect('databases/helpdesk.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM responses WHERE ticket_id=? AND poster=?", (tid, user.id))
            data = cur.fetchone()
            if data is None:
                return None
            return Response(data["id"])
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()

class Ticket:
    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def getDetail(self, d):
        return self.__data[d]

    def setDetail(self, d, v):
        if self.id == -3: return
        try:
            con = lite.connect('databases/helpdesk.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE tickets SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def isDisciplinary(self):
        return self.getDetail("type") == "pm"

    def isPing(self):
        return self.getDetail("type") == "ping"

    def isLegal(self):
        return self.getDetail("type") == "legal"

    def isClosed(self):
        return self.getDetail("closed")

    def isDeferred(self):
        return self.getDetail("deferred")

    def getTitle(self):
        return self.getDetail("title")

    def getDepartment(self):
        return self.getDetail("department")

    def isAssoced(self):
        return self.getDetail("assoc") != 0

    def isNoRepro(self):
        return self.getDetail("repro") == -1

    def getAssoc(self):
        return muser.User.from_id(self.getDetail("assoc"))

    def getHistory(self):
        return Response.getAll(self.id)

    def addViewer(self, u):
        try:
            con = lite.connect('databases/helpdesk.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO viewrights (ticket_id, person) VALUES (?, ?)", (self.id, u.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def isViewer(self, u):
        try:
            con = lite.connect('databases/helpdesk.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT ticket_id FROM viewrights WHERE person=? AND ticket_id=?", (u.id, self.id))
            data = cur.fetchone()
            return data is not None or u.id == self.getDetail("assoc");
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getViewer(self):
        try:
            con = lite.connect('databases/helpdesk.db')
            cur = con.cursor()
            cur.execute("SELECT person FROM viewrights WHERE ticket_id=?", (self.id,))
            data = cur.fetchall()
            if self.isAssoced():
                data.append([self.getDetail("assoc")])
            data = list(map(lambda x:x[0], data))
            return data
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()


    def getInfo(self):
        try:
            con = lite.connect('databases/helpdesk.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM tickets WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                return
            return {
                "id": data['id'],
                "title": data["title"],
                "department": data['department'],
                "closed": bool(data['closed']),
                "repro": data['repro'],
                "deferred": bool(data['deferred']),
                "assoc": data["assoc"],
                "type": data["type"],
                "last_response_id": data["last_response_id"]
            }
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    @classmethod
    def new(cls, title, type):
        try:
            con = lite.connect('databases/helpdesk.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO tickets (title, department, closed, repro, deferred, assoc, type, last_response_id) VALUES (?, '*nicht zugewiesen*', 0, 0, 0, 0, ?, 0)", (title, type))
            con.commit()
            return cur.lastrowid
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def exists(cls, id):
        try:
            con = lite.connect('databases/helpdesk.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM tickets WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def new(cls, title, type):
        try:
            con = lite.connect('databases/helpdesk.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO tickets (title, department, closed, repro, deferred, assoc, type, last_response_id) VALUES (?, '', 0, 0, 0, 0, ?, 0)", (title,type))
            con.commit()
            data = Ticket(cur.lastrowid)
            return data
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()

    @classmethod
    def getAll(cls):
        try:
            con = lite.connect('databases/helpdesk.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM tickets ORDER BY closed ASC, last_response_id DESC")
            data = cur.fetchall()
            l = list(map(lambda x:Ticket(x[0]), data))
            return l
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def getByUser(cls, u):
        try:
            con = lite.connect('databases/helpdesk.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM tickets WHERE id IN (SELECT ticket_id FROM viewrights WHERE person=?) OR assoc=? ORDER BY closed ASC, last_response_id DESC", (u.id, u.id))
            data = cur.fetchall()
            l = list(map(lambda x:Ticket(x["id"]), data))
            return l
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()
