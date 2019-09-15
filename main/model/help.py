# coding: utf-8
import os, json, re, time, math
import secrets
import sqlite3 as lite
from flask import request, session, url_for
from sha1 import sha1
from model import user as muser
from controller import times as ctimes

class HelpCategory:

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
            cur.execute("UPDATE help_category SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getTitle(self):
        return self.getDetail("title")

    def getExcerpt(self):
        return self.getDetail("excerpt")

    def isActive(self):
        return bool(self.getDetail("active"))

    def mayAdminEdit(self):
        return bool(self.getDetail("editable_by_admin"))

    def mayAdminCreateNewpage(self):
        return bool(self.getDetail("newpage_by_admin"))

    def getUrlPart(self):
        return self.getDetail("url_part")

    def getIcon(self):
        return self.getDetail("cat_symbol")

    def getHomepage(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            DATA = []
            cur.execute("SELECT * FROM help_entry WHERE help_cat=? AND is_pinned=1 AND master_page=0 AND active=1 AND is_deprecated=0", (self.id,))
            data = cur.fetchall()
            DATA.extend([HelpEntry(d["id"]) for d in data])
            cur.execute("SELECT * FROM help_entry WHERE help_cat=? AND is_pinned=0 AND master_page=0 AND active=1 AND is_deprecated=0 ORDER BY id LIMIT ?", (self.id, min(1, 5-len(DATA))))
            data = cur.fetchall()
            DATA.extend([HelpEntry(d["id"]) for d in data])
            return DATA
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def getFullpage(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM help_entry WHERE help_cat=? AND master_page=0 ORDER BY is_pinned DESC", (self.id,))
            data = cur.fetchall()
            return [HelpEntry(d["id"]) for d in data]
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def getInfo(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM help_category WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                raise ValueError("HelpCategory not found with id " + str(self.id))
            return {
                "id": data['id'],
                "active": data['active'],
                "title": data['title'],
                "cat_symbol": data['cat_symbol'],
                "url_part": data['url_part'],
                "excerpt": data['override_excerpt'] if data["override_excerpt"] != "" else data["original_excerpt"],
                "editable_by_admin": data['editable_by_admin'],
                "newpage_by_admin": data['newpage_by_admin']
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
            cur.execute("SELECT * FROM help_category WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def exists_url(cls, url):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM help_category WHERE url_part=?", (url,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def from_url(cls, url):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM help_category WHERE url_part=?", (url,))
            data = cur.fetchone()
            return cls(data["id"])
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
            cur.execute("SELECT id FROM help_category")
            data = cur.fetchall()
            return [cls(d["id"]) for d in data]
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()


class HelpEntry:

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
            cur.execute("UPDATE help_entry SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getTitle(self):
        return self.getDetail("title")

    def getContent(self):
        return self.getDetail("content")

    def getAsJSON(self):
        return json.loads(self.getContent())

    def isPinned(self):
        return bool(self.getDetail("is_pinned"))

    def isActive(self):
        return bool(self.getDetail("active"))

    def isDeprecated(self):
        return bool(self.getDetail("is_deprecated"))

    def getUrl(self):
        return self.getDetail("url")

    def getUrlPart(self):
        return self.getDetail("url_part")

    def getTemplate(self):
        return self.getDetail("template")

    def mayAdminEdit(self):
        return bool(self.getDetail("editable_by_admin"))

    def mayAdminCreateSubpage(self):
        return bool(self.getDetail("subpage_by_admin"))

    def getInfo(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM help_entry WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                raise ValueError("HelpEntry not found with id " + str(self.id))
            return {
                "id": data['id'],
                "master_page": data['master_page'],
                "active": data['active'],
                "template": data['template'],
                "help_cat": data['help_cat'],
                "url_part": data['url_part'],
                "url": data['url'],
                "title": data['title'],
                "content": data['override_content'] if data["override_content"] != "" else data["original_content"],
                "editable_by_admin": data['editable_by_admin'],
                "subpage_by_admin": data['subpage_by_admin'],
                "is_deprecated": data['is_deprecated'],
                "is_pinned": data['is_pinned'],
                "last_change": data['last_change'],
                "last_editor": data['last_editor'],
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
            cur.execute("SELECT * FROM help_entry WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def from_url(cls, url):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM help_entry WHERE url=?", (url,))
            data = cur.fetchone()
            return cls(data["id"])
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def create_new(cls, cat, parent, title, url, tpl="default"):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO help_entry (master_page, active, template, help_cat, url_part, url, title, original_content, override_content, editable_by_admin, subpage_by_admin, is_deprecated, is_pinned, last_change, last_editor) VALUES (?, 1, ?, ?, ?, ?,?, '', '', 1, 1, 0, 0, 0, 0)", (parent,tpl,cat,url,url,title))
            con.commit()
            data = cur.lastrowid
            return cls(data)
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()

    @classmethod
    def exists_url(cls, url):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM help_entry WHERE url=?", (url,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()
