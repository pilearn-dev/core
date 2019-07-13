# coding: utf-8
import os, json, re, time, math
import secrets
import sqlite3 as lite
from flask import request, session, url_for
from sha1 import sha1
from model import user as muser, courses as mcourses
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

    def getMenu(self):
        menu = self.getCourse().getMenu()
        new_menu = self.applyMenuOverrides(menu, 0, 0)
        new_menu = sorted(new_menu, key=lambda x: x["unit_order"])
        return new_menu

    def applyMenuOverrides(self, menu, pu, po):
        new_menu = []
        change_requests = self.getOverrides(pu,po)
        for item in menu:
            for change_request_id in range(len(change_requests)):
                change_request = change_requests[change_request_id]

                if change_request["overrides"] == item["id"]:

                    item["title"] = change_request["title"]
                    item["overrides"] = change_request["id"]
                    item["order"] = change_request["unit_order"]
                    item["children"] = sorted(self.applyMenuOverrides(self.applyMenuOverrides(item["children"], None, change_request["id"]), item["id"], None), key=lambda x: x["unit_order"])

                    item["changed"] = bool(change_request["changed"])
                    item["created"] = False

                    new_menu.append(item)

                    del change_requests[change_request_id]
                    break
            else:
                item.update({
                    "changed": False,
                    "created": False,
                    "overrides": None
                })
                item["children"] = sorted(self.applyMenuOverrides(item["children"], item["id"], None), key=lambda x: x["unit_order"])
                new_menu.append(item)
        new_menu += change_requests

        return new_menu

    def getCourse(self):
        return mcourses.Courses(self.getDetail("course_id"))

    def getAuthor(self):
        return muser.User.safe(self.getDetail("author"))

    def isAbandoned(self): return bool(self.getDetail("abandoned"))

    def getOverrides(self, parent_unit=None, parent_override=None):
        try:
            con = lite.connect('databases/courses.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if parent_unit is not None and parent_override is not None:
                cur.execute("SELECT * FROM branch_overrides WHERE branch=? AND parent_unit=? AND parent_override = ?", (self.id, parent_unit, parent_override))
            elif parent_unit is not None:
                cur.execute("SELECT * FROM branch_overrides WHERE branch=? AND parent_unit=?", (self.id, parent_unit))
            elif parent_override is not None:
                cur.execute("SELECT * FROM branch_overrides WHERE branch=? AND parent_override=?", (self.id, parent_override))
            else:
                cur.execute("SELECT * FROM branch_overrides WHERE branch=?", (self.id,))
            return cur.fetchall()
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def getSingleOverride(self, id):
        try:
            con = lite.connect('databases/courses.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM branch_overrides WHERE id=?", (id,))
            return cur.fetchone()
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()

    def hasOverrideForUnit(self, unit_id):
        try:
            con = lite.connect('databases/courses.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM branch_overrides WHERE branch=? AND overrides=?", (self.id, unit_id))
            return cur.fetchone()
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()

    def updateOrMakeOverride(self, unit_id, override_id, data):
        try:
            con = lite.connect('databases/courses.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if self.hasOverrideForUnit(unit_id) or override_id != "-":
                if override_id != "-":
                    cur.execute("UPDATE branch_overrides SET parent_unit=?, parent_override=?, title=?, content=?, type=?, unit_order=? WHERE id=?", (data["parent_unit"], data["parent_override"], data["title"], data["content"], data["type"], data["unit_order"], override_id))
                else:
                    cur.execute("UPDATE branch_overrides SET parent_unit=?, parent_override=?, title=?, content=?, type=?, unit_order=? WHERE branch=? AND overrides=?", (data["parent_unit"], data["parent_override"], data["title"], data["content"], data["type"], data["unit_order"], self.id, unit_id))

                cur.execute("SELECT * FROM branch_overrides WHERE branch=? AND overrides=?", (self.id,unit_id))
                rowid = cur.fetchone()["id"]
            else:
                cur.execute("INSERT INTO branch_overrides (branch, overrides, parent_unit, parent_override, title, content, type, unit_order, changed, created) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 0)", (self.id, unit_id, data["parent_unit"], data["parent_override"], data["title"], data["content"], data["type"], data["unit_order"]))
                rowid = cur.lastrowid
            con.commit()
            return rowid
        except lite.Error as e:
            print e
            return False
        finally:
            if con:
                con.close()

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
            cur.execute("INSERT INTO branches (author, course_id, pull_request, abandoned, abandoned_date, decision, decision_date, hide_as_spam, delta_factor) VALUES (?, ?, NULL, 0, 0, 0, 0, 0, 0)", (user_id, course_id))
            data = con.commit()
            return Branch(cur.lastrowid)
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()
