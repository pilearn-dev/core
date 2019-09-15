# coding: utf-8
import os, json, re, time, math
import secrets
import sqlite3 as lite
from flask import request, session, url_for
from sha1 import sha1
from model import user as muser
from controller import times as ctimes

class Survey:

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
            cur.execute("UPDATE surveys SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def hasSubmission(self, cuser):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM survey_responses WHERE survey_id=? AND responder_id=?", (self.id, cuser.id))
            return cur.fetchone() is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def addSubmission(self, cuser, content):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO survey_responses (survey_id, responder_id, content) VALUES (?,?,?)", (self.id, cuser.id, content))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def getSubmissions(self):
        try:
            con = lite.connect('databases/pilearn.db')
            cur = con.cursor()
            cur.execute("SELECT content FROM survey_responses WHERE survey_id=?", (self.id,))
            data = cur.fetchall()
            return data
        except lite.Error as e:
            print(e)
            return []
        finally:
            if con:
                con.close()

    def getTitle(self):
        return self.getDetail("title")

    def mayBeAnswered(self):
        return (1 == self.getDetail("state"))

    def getContent(self):
        return json.loads(self.getDetail("content"))

    def hasResults(self):
        return bool(self.getDetail("results"))

    def getResults(self):
        d = json.loads(self.getDetail("results"))
        d = sorted(d.items(), key=lambda x:int(x[0]))
        return d

    def getLabel(self):
        label = self.getTitle()
        label = label.replace(u"π", "pi")
        label = re.sub("[^a-zA-Z0-9- ]+", "", label)
        label = re.sub("[ ]+", "-", label)
        label = label.lower()[:50].strip("-")
        return label

    def getInfo(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM surveys WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                raise ValueError("Survey not found with id " + str(self.id))
            return {
                "id": data['id'],
                "title": data['title'],
                "content": data['content'],
                "results": data['results'],
                "state": data['state'],
                "associated_forum": data['associated_forum'],
                "survey_owner": data['survey_owner']
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
            cur.execute("SELECT * FROM surveys WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def new(cls, forum_id, owner_id):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO surveys (title, content, results, state, associated_forum, survey_owner) VALUES ('Neue Umfrage', '[]', '', 0, ?, ?)", (forum_id,owner_id))
            data = con.commit()
            return Survey(cur.lastrowid)
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()
