# coding: utf-8
import os, time
import sqlite3 as lite

class UserUpload:

    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def getDetail(self, d):
        return self.__data[d]

    def getPath(self):
        return self.getDetail("file_path")

    def isDeleted(self):
        return bool(self.getDetail("removed_by"))

    def setDetail(self, d, v):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE user_uploads SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getInfo(self):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM user_uploads WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                raise ValueError("User uploaded image not found with id " + str(self.id))
            return {
                "id": data['id'],
                "user_id": data['user_id'],
                "file_path": data['file_path'],
                "removed_by": data['removed_by'],
                "upload_at": data['upload_at'],
                "file_size": data['file_size']
            }
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()
    @classmethod
    def new(cls, user, file_path, file_size):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO user_uploads (user_id, file_path, removed_by, upload_at, file_size) VALUES (?, ?, 0, ?, ?)", (user.id, file_path, time.time(), file_size))
            con.commit()
            return cur.lastrowid
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    @classmethod
    def exists(cls, id):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT count(*) AS c FROM user_uploads WHERE id=?", (id,))
            return cur.fetchone()["c"] != 0
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    @classmethod
    def has_by_user(cls, user):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT count(*) AS c FROM user_uploads WHERE user_id=?", (user.id,))
            return cur.fetchone()["c"]
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    @classmethod
    def get_by_user(cls, user):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM user_uploads WHERE user_id=?", (user.id,))
            return [UserUpload(i["id"]) for i in cur.fetchall()]
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()
