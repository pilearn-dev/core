# coding: utf-8
import time
import secrets
import sqlite3 as lite
from model import user as muser
from controller import times as ctimes

class Badge:

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
            cur.execute("UPDATE badges SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def awardTo(self, user_id, data):
        try:
            con = lite.connect('databases/pilearn.db')
            cur = con.cursor()
            cur.execute("INSERT INTO badge_associations (badgeid, userid, data, given_date, recognized) VALUES (?, ?, ?, strftime('%s','now'), 0)", (self.id,user_id, data))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def revokeFrom(self, user_id, ts):
        try:
            con = lite.connect('databases/pilearn.db')
            cur = con.cursor()
            cur.execute("DELETE FROM badge_associations WHERE badgeid=? AND userid=? AND given_date=?", (self.id,user_id, ts))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getAwardees(self):
        try:
            con = lite.connect('databases/pilearn.db')
            cur = con.cursor()
            cur.execute("SELECT * FROM badge_associations WHERE badgeid=? ORDER BY given_date DESC", (self.id,))
            data = cur.fetchall()
            d = []
            for _ in data:
                dt = _[4]
                dt = [dt, ctimes.stamp2german(dt), ctimes.stamp2shortrelative(dt, False)]
                d.append({
                    "user": muser.User.from_id(_[0]),
                    "data": _[2],
                    "time": dt
                })
                if len(d) == 40:
                    break
            return d
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def getAwardeeCount(self):
        try:
            con = lite.connect('databases/pilearn.db')
            cur = con.cursor()
            cur.execute("SELECT Count(*) FROM badge_associations WHERE badgeid=? ORDER BY given_date DESC", (self.id,))
            return cur.fetchone()[0]
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    def getName(self): return self.getDetail("name")
    def getClass(self): return self.getDetail("class")
    def getDescription(self): return self.getDetail("description")

    def getInfo(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM badges WHERE id=?", (self.id,))
            data = cur.fetchone()
            if data is None:
                raise ValueError("Badge not found with id " + str(self.id))
            return {
                "id": data['id'],
                "name": data['name'],
                "class": data['class'],
                "description": data['description'],
                "internal_id": data['internal_id']
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
            cur.execute("SELECT * FROM badges WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def getAll(cls):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM badges ORDER BY id")
            data = cur.fetchall()
            DATA =  []
            for d in data:
                DATA.append(Badge(d["id"]))
            return DATA
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def byUser(cls, u):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT badges.*, badge_associations.given_date, badge_associations.data FROM badges, badge_associations WHERE badges.id=badge_associations.badgeid AND badge_associations.userid=? ORDER BY badge_associations.given_date DESC", (u.id,))
            data = cur.fetchall()
            DATA =  []
            for d in data:
                dt = d["given_date"]
                dt = [dt, ctimes.stamp2german(dt), ctimes.stamp2shortrelative(dt, False)]
                DATA.append({
                    "id": d["id"],
                    "name": d["name"],
                    "class": d["class"],
                    "description": d["description"],
                    "given_date": dt,
                    "data": d["data"]
                })
            return DATA
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()
