# coding: utf-8
import os, json
import secrets
import sqlite3 as lite
from flask import request, session, url_for
from sha1 import sha1,md5
from model import privileges as mprivileges, tags as mtags
from controller import times as ctimes
import time

class User:

    STD_USER = "u"
    MOD_USER = "m"
    ADMIN_USER = "a"
    DEV_USER = "d"

    repActions = {
        "update": "Korrektur",
        "forum_vote": "Beitragsbewertung",
        "forum_accept": "Beitrag akzeptiert",
        "enroll": "Neuer Kursbesucher"
    }

    labels = {
        "beta": "Betatestender",
        "mod_active": "Moderator",
        "mod_retired": "Moderator (ehemalig)",
        "admin_active": "Administrator",
        "admin_retired": "Administrator (ehemalig)",
        "robot": "Roboter",
        "betaaccess": u"αβγδ"
    }
    possibleLabels = ["beta", "mod_active", "mod_retired", "admin_active", "admin_retired", "robot", "betaaccess"]

    BAN_REASON = {
        "rule-violation": u"wegen Regelverletzung",
        "sock-puppets": u"wegen illegaler Zweitkonten",
        "spam": u"wegen des Verbreitens von SPAM",
        "offensive": u"wegen beleidigenden Verhaltens",
        "conflicts": u"wegen andauernden Konflikten mit anderen Benutzern",
        "cool-down": u"zur Konfliktauflösung",
        "no-improvement": u"als unfähig unsere Regeln zu lernen",
        "no-positive-contribution": u"als keine Bereicherung für die Community"
    }

    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def isDev(self):
        return self.getDetail("role") == "team.dev"

    def isTeam(self):
        return self.getDetail("role").startswith("team.")

    def isAdmin(self):
        return self.isDev() or self.getDetail("role") == "administrator" or self.getDetail("role") == "team.admin"

    def isMod(self):
        return self.isAdmin() or self.getDetail("role") == "moderator" or self.getDetail("role") == "team.mod"

    def isDeleted(self):
        return self.getDetail("deleted") == 1

    def isDisabled(self):
        x = self.getDetail("banned") == 1
        if x and self.getDetail("ban_end") <= time.time():
            self.setDetail("banned", 0)
            self.setDetail("ban_end", 0)
            self.setDetail("ban_reason", "")
            self.__data = self.getInfo()
            self.addAnnotation("unban", "auto", User.from_id(-1), time.time())
            return False
        return x

    def isEnabled(self):
        return self.getDetail("banned") == 0

    def getDetail(self, d):
        return self.__data[d]


    def getShortProfileText(self):
        text = self.getDetail("aboutme")
        text = text.replace("\n", " ")
        text = text.replace("\r", " ")
        while "  " in text:
            text = text.replace("  ", " ")
        sentences = 0
        last_char = None
        allowed = []
        for t in text:
            if t == " ":
                if last_char in u".!?":
                    sentences += 1
            if sentences >= 2:
                break
            else:
                allowed.append(t)
                last_char = t
        text = "".join(allowed)

        text = text.strip()

        if len(text) > 140:
            T = text.split(" ")
            text = []
            len_ = 0
            for _ in T:
                if len(_) + len_ > 138:
                    break
                else:
                    len_ += len(_) + 1
                    text.append(_)
            text = " ".join(text).strip() + "..."

        return text.strip()

    def getRepDelta(self):
        if self.id == -3: return
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT SUM(amount) FROM reputation WHERE user_id = ? AND recognized=0", (self.id,))
            d = cur.fetchone()[0]
            if d is None:
                return 0
            return d
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    def getHTMLName(self, with_border=True):
        try:
            name = self.getDetail("realname")
        except Exception as e:
            raise SyntaxError(self.id)
        if self.isAdmin():
            if with_border:
                name = name + " <span title='Administrator'>&#11042;</span>"
            else:
                name = name + " &#11042;"
        elif self.isMod():
            if with_border:
                name = name + " <span title='Moderator'>&#11040;</span>"
            else:
                name = name + " &#11040;"
        return name

    def getBanReason(self):
        return User.BAN_REASON[self.getDetail("ban_reason")]

    def getBanEnd(self, asRelative=False):
        d = self.getDetail("ban_end")
        if asRelative:
            d = [d, ctimes.stamp2german(d), ctimes.stamp2relative(d, True)]
        return d

    def setDetail(self, d, v):
        if self.id == -3: return
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE user SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def setReputationChange(self, type, msg, amount):
        if self.id == -3: return
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO reputation (user_id, type, message, amount, recognized) VALUES (?, ?, ?, ?, 0)", (self.id, type, msg, amount))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getReputationChanges(self):
        if self.id == -3: return []
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM reputation WHERE user_id=? ORDER BY id DESC", (self.id, ))
            all = cur.fetchall()
            if all is None:
                return []
            all = list(map(dict, all))
            return all
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def getUnknownReputationChanges(self):
        if self.id == -3: return []
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM reputation WHERE user_id=? AND recognized=0 ORDER BY id DESC", (self.id, ))
            all = cur.fetchall()
            if all is None:
                return []
            all = list(map(dict, all))
            return all
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def knowReputationChanges(self):
        if self.id == -3: return []
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE reputation SET recognized=1 WHERE user_id=? AND recognized=0", (self.id, ))
            all = con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def customflag(self, msg, who):
        try:
          con = lite.connect('databases/user.db')
          con.row_factory = lite.Row
          cur = con.cursor()
          qid = None
          cur.execute("SELECT * FROM custom_flaglist WHERE item_id=? AND item_type='user' AND state=0", (self.id,))
          qid = cur.fetchone()
          if qid is None:
              cur.execute("INSERT INTO custom_flaglist (item_id, item_type, state) VALUES (?, 'user', 0)", (self.id,))
              qid = cur.lastrowid
          else:
              qid = qid["id"]
          cur.execute("INSERT INTO custom_flag (item_id, item_type, queue_id, state, flagger_id, comment) VALUES (?, 'user', ?, 0, ?, ?)", (self.id, qid, who.id, msg))
          con.commit()
          return True
        except SyntaxError as e:#lite.Error as e:
          print(e)
          return False
        finally:
          if con:
              con.close()

    def getAnnotations(self, order="id"):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            reverse = False
            if order.endswith("_reverse"):
                reverse = True
                order = order[:-8]
            if order not in ["id", "time", "creator_id", "type"]:
                order = "id"
            elif order == "time":
                order = "creation_date"
            cur.execute("SELECT * FROM annotations WHERE user_id=? ORDER BY "+order+" " + ('ASC' if reverse else 'DESC') + ", id DESC", (self.id, ))
            d = cur.fetchall()
            data = []
            for d_ in d:
                data.append({
                    "id": d_["id"],
                    "deleted": bool(d_["is_hidden"]),
                    "user_id": d_["user_id"],
                    "creator": User.from_id(d_["creator_id"]),
                    "relative_date": ctimes.stamp2relative(d_["creation_date"]),
                    "absolute_date": ctimes.stamp2german(d_["creation_date"]),
                    "content": d_["content"],
                    "type": d_["type"]
                })
            return data
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    def isReviewBanned(self, queue):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM reviewbans WHERE user_id=? AND invalidated=0 AND end_date>? AND queue=?", (self.id, time.time(), queue))
            d = cur.fetchone()
            return d is not None
        except lite.Error as e:
            raise False
        finally:
            if con:
                con.close()

    def getReviewBanEnd(self, queue, asRelative=False):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM reviewbans WHERE user_id=? AND invalidated=0 AND end_date>? AND queue=?", (self.id, time.time(), queue))
            d = cur.fetchone()["end_date"]
            if asRelative:
                d = [d, ctimes.stamp2german(d), ctimes.stamp2relative(d)]
            return d
        except lite.Error as e:
            raise False
        finally:
            if con:
                con.close()

    def imposeReviewBan(self, queue, by, msg):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM reviewbans WHERE user_id=? AND end_date>? AND invalidated=0 AND queue=? ORDER BY end_date DESC", (self.id, time.time() - (90 * 24 * 60 * 60), queue))
            d = cur.fetchone()
            if d is None:
                dur = -1
            else:
                dur = (d["end_date"] - d["start_date"]) / (60 * 60.0)
            if dur >= 24*60:
                dur += 5
            else:
                durnext = {
                    -1: 2,
                    2: 24 * 1,
                    24: 24 * 2,
                    48: 24 * 4,
                    96: 24 * 7,
                    168: 24 * 14,
                    336: 24 * 30,
                    720: 24 * 60
                }
                dur = durnext[dur]
            cur.execute("INSERT INTO reviewbans (queue, user_id, given_by, cancelled_by, start_date, end_date, invalidated, comment) VALUES (?, ?, ?, 0, ?, ?, 0, ?)", (queue, self.id, by.id, time.time(), time.time()+(60*60*dur), msg))
            con.commit()
            return True
        except lite.Error as e:
            raise False
        finally:
            if con:
                con.close()

    def invalidateReviewBan(self, queue, by):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE reviewbans SET cancelled_by=?, invalidated=1 WHERE user_id=? AND invalidated=0 AND end_date>? AND queue=?", (by.id, self.id, time.time(), queue))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            raise False
        finally:
            if con:
                con.close()

    def getReviewBanMessage(self, queue):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM reviewbans WHERE user_id=? AND invalidated=0 AND end_date>? AND queue=?", (self.id, time.time(), queue))
            d = cur.fetchone()["comment"]
            return d
        except lite.Error as e:
            raise ""
        finally:
            if con:
                con.close()

    def addAnnotation(self, type, msg, user, time):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO annotations (user_id, creator_id, creation_date, is_hidden, content, type) VALUES (?, ?, ?, 0, ?, ?)", (self.id, user.id, time, msg, type))
            con.commit()
            return True
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    def getReputation(self):
        return max(0, self.getDetail("reputation"))

    def editAnnotation(self, id, d, v):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE annotations SET "+d+"=? WHERE id=?", (v, id))
            con.commit()
            return True
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    def getInfo(self):
        if self.isLoggedIn():
            try:
                con = lite.connect('databases/user.db')
                con.row_factory = lite.Row
                cur = con.cursor()
                cur.execute("SELECT * FROM user WHERE id=?", (self.id, ))
                data = cur.fetchone()
                if data is None:
                    return {}
                return {
                    "id": data['id'],
                    "name": data["name"],
                    "realname": data['realname'],
                    "email": data['email'],
                    "deleted": data['deleted'],
                    "banned": data['banned'],
                    "ban_reason": data['ban_reason'],
                    "ban_end": data['ban_end'],
                    "role": data['role'],
                    "reputation": data['reputation'] if not data["banned"] == 1 else 0,
                    "profile_image": data["profile_image"] if data["profile_image"] is not None and data["profile_image"] != "" else ("https://www.gravatar.com/avatar/"+md5(data["email"]+"#pilearn#"+str(data["id"]))+"?d=identicon" if data["reputation"] > 100 else False),
                    "password": secrets.token_urlsafe(16) if data["password"] != "" else "",
                    "aboutme":data["aboutme"] if data["aboutme"] != None else "",
                    "frozen": bool(data["frozen"]),
                    "suspension": json.loads(data["suspension"]) if data["suspension"] is not None else [],
                    "labels": json.loads(data["labels"]) if data["labels"] is not None else [],
                    "login_provider": data["login_provider"],
                    "mergeto": data["mergeto"]
                }
            except lite.Error as e:
                #raise lite.Error from e
                raise e
            finally:
                if con:
                    con.close()
        else:
            return {
                "id": -3,
                "name": "<anonym>",
                "realname": "Anonymer Benutzer",
                "email": "",
                "deleted": 1,
                "banned": 0,
                "role": "user",
                "reputation": 0,
                "profile_image": "",
                "password":"",
                "aboutme":"",
                "suspension": [],
                "labels": [],
                "login_provider": "none"
            }

    def isLoggedIn(self):
        return self.id != -3

    def getNotifications(self):
        all = self.may("general_showAllNotifications")
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if not all and self.isDisabled():
                cur.execute("SELECT * FROM notifications WHERE user_id=? AND (visible!=0 OR type='pm')", (self.id, ))
            elif all:
                cur.execute("SELECT * FROM notifications WHERE user_id=?", (self.id, ))
            else:
                cur.execute("SELECT * FROM notifications WHERE user_id=? AND visible!=0", (self.id, ))
            return_value = []
            data = cur.fetchone()
            while data:
                return_value.append({
                    "type": data["type"],
                    "message": data["message"],
                    "link": "/notification/" + str(data["id"]) if (data["visible"] == 1 and not (self.isDisabled() and data["type"]=="pm")) else data["link"],
                    "visibility": data["visible"]
                })
                data = cur.fetchone()
            return return_value
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    def may(self, prop, ignoreSuspension=False):
        if self.isDisabled() or not self.isLoggedIn():
            return False
        rep = self.getReputation()
        if rep >= mprivileges.getOne(prop) and (prop not in self.getDetail("suspension") or ignoreSuspension):
            return True
        elif prop.startswith("forum_"):
            return self.isMod()
        else:
            return self.isAdmin()


    def notify(self, type,msg,url):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO notifications (user_id, type, message, link, visible) VALUES (?, ?, ?, ?, 2)", (self.id, type, msg, url))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def getNotification(self, id):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM notifications WHERE id=?", (id, ))
            data = cur.fetchone()
            return data
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    def hideNotification(self, id):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE notifications SET visible='0' WHERE id=?", (id, ))
            con.commit()
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    def hideNotifications(self):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE notifications SET visible='1' WHERE visible='2'")
            con.commit()
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()



    @classmethod
    def getRoleTable(cls, role):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM role_table WHERE role=?", (role,))
            data = cur.fetchall()
            DATA = []
            for d in data:
                DATA.append({
                    "id": d["id"],
                    "user": User.from_id(d["user_id"]),
                    "role": d["role"],
                    "scope_comment": d["scope_comment"],
                    "active": bool(d["active"]),
                    "shown": bool(d["shown"]),
                    "appointment_date": [d["appointment_date"], ctimes.stamp2german(d["appointment_date"]), ctimes.stamp2relative(d["appointment_date"])],
                    "election_link": d["election_link"],
                    "resignation_date": [d["resignation_date"], ctimes.stamp2german(d["resignation_date"]), ctimes.stamp2relative(d["resignation_date"])],
                    "comment": d["comment"]
                })
            return DATA
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()


    @classmethod
    def blank(cls):
        return cls(-3)

    @classmethod
    def from_id(cls, id):
        return cls(id)

    @classmethod
    def safe(cls, id):
        u = cls(id)
        if u.getDetail("mergeto"):
            u = cls(u.getDetail("mergeto"))
        return u

    @classmethod
    def login(cls, username, password):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM user WHERE name=? AND (password=? OR password='') AND login_provider='local_account'", (username, sha1(password)))
            data = cur.fetchone()
            if data is None:
                return -3
            else:
                if data["mergeto"]:
                    new_id = data["mergeto"]
                    return new_id
                if data["deleted"] == 1:
                    return -4
                else:
                    return data['id']
        except lite.Error as e:
            return -3
        finally:
            if con:
                con.close()

    @classmethod
    def oauth_login(cls, provider, email):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM user WHERE login_provider=? AND email=?", ("oauth:"+provider, email))
            data = cur.fetchone()
            if data is None:
                return -3
            else:
                if data["mergeto"]:
                    new_id = data["mergeto"]
                    return new_id
                if data["deleted"] == 1:
                    return -4
                else:
                    return data['id']
        except lite.Error as e:
            return -3
        finally:
            if con:
                con.close()

    @classmethod
    def register(cls, username, password, realname, email):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute(u"SELECT * FROM user WHERE name=? OR email=?", (username, email))
            if cur.fetchone():
                return -3
            cur.execute(u"INSERT INTO user (name, realname, email, password, banned, role, reputation, aboutme, login_provider) VALUES (?, ?, ?, ?, 0, 'user', 0, ?, 'local_account')", (username, realname, email, sha1(password), u""))
            data = cur.lastrowid
            con.commit()
            return data
        except lite.Error as e:
            print(e)
            return -3
        finally:
            if con:
                con.close()

    @classmethod
    def reset_deletion(cls, username, password):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute(u"UPDATE user SET deleted=0 WHERE name=? AND password=?", (username, sha1(password)))
            con.commit()
            cur.execute(u"SELECT id FROM user WHERE name=? AND password=?", (username, sha1(password)))
            data = cur.fetchone()["id"]
            return data
        except lite.Error as e:
            print(e)
            return -3
        finally:
            if con:
                con.close()

    @classmethod
    def exists(cls, id):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM user WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def passwdreset(cls, username, email):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE user SET password='' WHERE name=? AND email=?", (username, email))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def getByRole(cls, role):
        try:
            con = lite.connect('databases/user.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM user WHERE role=? AND banned=1", (role,))
            data = cur.fetchall()
            data = list(map(lambda x:User.from_id(x["id"]), data))
            return data
        except lite.Error as e:
            print(e)
            return []
        finally:
            if con:
                con.close()


def require_login():
    return session.get('login') is None

def getCurrentUser():
    if require_login():
        return User.blank()
    else:
        return User.from_id(session.get('login'))
