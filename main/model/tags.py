# coding: utf-8
import sqlite3 as lite
from model.forum import Forum

class ForumTag:

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
            cur.execute("UPDATE forum_tags SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getForum(self):
        if self.getDetail("forum_id") is None:
            return None
        return Forum(self.getDetail("forum_id"))

    def isModOnly(self):
        return bool(self.getDetail("mod_only"))

    def isApplicable(self):
        return bool(self.getDetail("applicable"))

    def getName(self):
        return self.getDetail("name")

    def getExcerpt(self):
        return self.getDetail("excerpt")

    def getDeprecationWarning(self):
        return self.getDetail("deprecation_notice")

    def addAssoc(self, article_id):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO forum_tag_associations (post_id, tag_id) VALUES (?, ?);", (article_id, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def removeAssoc(self, article_id):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("DELETE FROM forum_tag_associations WHERE post_id=? AND tag_id=?;", (article_id, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getInfo(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM forum_tags WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                raise ValueError("ForumTag not found with id " + str(self.id))
            return {
                "id": data['id'],
                "forum_id": data['forum_id'],
                "name": data['name'],
                "excerpt": data['excerpt'],
                "applicable": data['applicable'],
                "mod_only": data['mod_only'],
                "deprecation_notice": data['deprecation_notice']
            }
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    @classmethod
    def byName(cls, name, forum_id=None):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if forum_id == "any":
                cur.execute("SELECT id, redirects_to FROM forum_tags WHERE name=?", (name,))
            elif forum_id is not None:
                cur.execute("SELECT id, redirects_to FROM forum_tags WHERE name=? AND forum_id = ?", (name, forum_id))
            else:
                cur.execute("SELECT id, redirects_to FROM forum_tags WHERE name=? AND forum_id Is Null", (name,))
            data = cur.fetchone()
            if not data:
                return None
            if data[1] != 0:
                id = data[1]
            else:
                id = data[0]
            return cls(id)
        except lite.Error as e:
            print(e)
            return None
        finally:
            if con:
                con.close()

    @classmethod
    def createNew(cls, name, forumID=None):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO forum_tags (forum_id, name, excerpt, deprecation_notice, redirects_to, applicable, mod_only) VALUES (?, ?, '', '', 0, 1, 0);", (forumID, name))
            con.commit()
            return cls(cur.lastrowid)
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()

    @classmethod
    def exists(cls, id):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM forum_tags WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def exists_name(cls, name):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM forum_tags WHERE name=?", (name,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

class blankTag:

    def __init__(self, name):
        self.id = -1
        self.name=name

    def getName(self): return self.name
    def isModOnly(self): return False
    def isApplicable(self): return False
    def getExcerpt(self): return ""
    def getForum(self): return None
