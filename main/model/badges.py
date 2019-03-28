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
            con = lite.connect('databases/user.db')
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

    def getName(self): return self.getDetail("name")
    def getClass(self): return self.getDetail("class")
    def getDescription(self): return self.getDetail("description")

    def getInfo(self):
        try:
            con = lite.connect('databases/user.db')
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
            con = lite.connect('databases/user.db')
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
            con = lite.connect('databases/user.db')
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
