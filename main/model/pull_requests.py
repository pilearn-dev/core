# coding: utf-8
import os, json, re, time, math
import secrets
import sqlite3 as lite
from flask import request, session, url_for
from sha1 import sha1
from model import user as muser
from controller import times as ctimes

class Branch:

    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def getDetail(self, d):
        return self.__data[d]

    def setDetail(self, d, v):
        try:
            con = lite.connect('databases/courses.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE branches SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getCourse(self):
        return mcourses.Course(self.getDetail("course_id"))

    def getAuthor(self):
        return muser.User.safe(self.getDetail("author"))

    def isAbandoned(self): return bool(self.getDetail("abandoned"))

    def getInfo(self):
        try:
            con = lite.connect('databases/courses.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM branches WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                raise ValueError("Branch not found with id " + str(self.id))
            return {
                "id": data['id'],
                "author": data['author'],
                "course_id": data['course_id'],
                "pull_request": data['pull_request'],
                "abandoned": data['abandoned'],
                "abandoned_date": data['abandoned_date'],
                "decision": data['decision'],
                "decision_date": data['decision_date'],
                "hide_as_spam": data['hide_as_spam'],
                "delta_body": data['delta_body'],
                "delta_factor": data['delta_factor']
            }
        except lite.Error as e:
            raise e
        finally:
            if con:
                con.close()

    @classmethod
    def exists(cls, id):
        try:
            con = lite.connect('databases/courses.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM branches WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def getByCourseAndUser(cls, course_id, user_id):
        try:
            con = lite.connect('databases/courses.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM branches WHERE course_id=? AND author=?", (course_id, user_id))
            data = cur.fetchone()
            return Branch(data["id"]) if data is not None else None
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()

    @classmethod
    def new(cls, course_id, user_id):
        try:
            con = lite.connect('databases/courses.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO branches (author, course_id, pull_request, abandoned, abandoned_date, decision, decision_date, hide_as_spam, delta_body, delta_factor) VALUES (?, ?, NULL, 0, 0, 0, 0, 0, '', 0)", (user_id, course_id))
            data = con.commit()
            return Branch(cur.lastrowid)
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()
