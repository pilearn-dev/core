# coding: utf-8
import os, json
import secrets
import sqlite3 as lite
from flask import request, session, url_for
from sha1 import sha1,md5
from model import privileges as mprivileges
from controller import times as ctimes
import time, random

class User:

    repActions = {
        "update": "Korrektur",
        "forum_vote": "Beitragsbewertung",
        "forum_accept": "Beitrag akzeptiert",
        "enroll": "Neuer Kursbesucher",
        "winter": "Winter 2018",
        "pr": "Pull Request"
    }

    labels = {
        "beta": "Betatestender",
        "mod_active": "Moderator",
        "mod_retired": "Moderator (ehemalig)",
        "admin_active": "Administrator",
        "admin_retired": "Administrator (ehemalig)",
        "robot": "Roboter",
        "betaaccess": "αβγδ"
    }
    possibleLabels = ["beta", "mod_active", "mod_retired", "admin_active", "admin_retired", "robot", "betaaccess"]

    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def isDev(self):
        return bool(self.getDetail("is_dev"))

    def isTeam(self):
        return bool(self.getDetail("is_team"))

    def isAdmin(self):
        return self.isMod()

    def isMod(self):
        return bool(self.getDetail("is_mod"))

    def isDeleted(self):
        return self.getDetail("deleted") != 0

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


    def getEmailHashs(self):
        email = self.getDetail("email")
        return {
            "salted": md5(email+"#pilearn#"+str(self.id)),
            "raw": md5(email)
        }


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
                if last_char in ".!?" and allowed[-2] not in "0123456789":
                    sentences += 1
            if sentences >= 4:
                break
            else:
                allowed.append(t)
                last_char = t
        text = "".join(allowed)

        text = text.strip()

        if len(text) > 200:
            T = text.split(" ")
            text = []
            len_ = 0
            for _ in T:
                if len(_) + len_ > 198:
                    break
                else:
                    len_ += len(_) + 1
                    text.append(_)
            text = " ".join(text).strip() + "..."

        return text.strip()

    def getPref(self, key, default):
        if self.id == -3: return default
        if session.get("login") == self.id and session.get("preference:"+key, False):
            return session["preference:"+key]

        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT value FROM user_preference_overrides WHERE user_id = ? AND pref_key=?", (self.id,key))
            d = cur.fetchone()
            if d is None:
                return default
            if session.get("login") == self.id:
                session["preference:"+key] = d["value"]
            return d["value"]
        except lite.Error as e:
            print(e)
            return default
        finally:
            if con:
                con.close()

    def setPref(self, key, value):
        if self.id == -3: return False
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT value FROM user_preference_overrides WHERE user_id = ? AND pref_key=?", (self.id,key))
            d = cur.fetchone()
            if d is None:
                cur.execute("INSERT INTO user_preference_overrides VALUES (?, ?, ?)", (self.id,key,value))
            else:
                cur.execute("UPDATE user_preference_overrides SET value=? WHERE user_id = ? AND pref_key=?", (value,self.id,key))
            con.commit()
            if session.get("login") == self.id:
                session["preference:"+key] = value
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def getRepDelta(self):
        if self.id == -3: return
        try:
            con = lite.connect('databases/pilearn.db')
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

    def hasUnknownBadges(self):
        if self.id == -3: return
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT Count(*) FROM badge_associations WHERE userid = ? AND recognized=0", (self.id,))
            d = cur.fetchone()[0]
            return d != 0
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getHTMLName(self, with_border=True):
        try:
            name = self.getDetail("realname")
        except Exception as e:
            raise SyntaxError(self.id)
        if self.isMod():
            if with_border:
                name = name + " <span title='Moderator'>♦</span>"
            else:
                name = name + " ♦"
        return name

    def getBanReason(self):
        return self.getDetail("ban_reason")

    def getBanEnd(self, asRelative=False):
        d = self.getDetail("ban_end")
        if asRelative:
            d = [d, ctimes.stamp2german(d), ctimes.stamp2relative(d, True)]
        else:
            d = [d, ctimes.stamp2german(d), ctimes.stamp2relative(d)]
        return d

    def setDetail(self, d, v):
        if self.id == -3: return
        try:
            con = lite.connect('databases/pilearn.db')
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
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO reputation (user_id, type, message, amount, recognized, given_date) VALUES (?, ?, ?, ?, 0, strftime('%s','now'))", (self.id, type, msg, amount))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    # Regetting the reputation will fix any possible race-condition-based discrepancy between user.reputation and the reputation table.
    # Regetting DOES NOT recalculate the users reputation history and shall only be used if there's a possible discrepancy.
    # :forall: will reget everyones reputation, otherwise only current users' one
    def regetRep(self, forall=False):
        if self.id == -3: return
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if forall:
                cur.execute("UPDATE user SET reputation = 1")
                cur.execute("UPDATE user SET reputation = 1+MAX((SELECT Sum(amount) FROM reputation WHERE reputation.user_id=user.id),0) WHERE (SELECT Count(*) FROM reputation WHERE reputation.user_id=user.id) > 0")
            else:
                cur.execute("UPDATE user SET reputation = 1 WHERE id=?", (self.id,))
                cur.execute("UPDATE user SET reputation = 1+MAX((SELECT Sum(amount) FROM reputation WHERE reputation.user_id=user.id),0) WHERE user.id=? AND (SELECT Count(*) FROM reputation WHERE reputation.user_id=user.id) > 0", (self.id,))
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
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT *, Sum(amount) AS total_amount FROM reputation WHERE user_id=? GROUP BY given_date/3600, message HAVING total_amount!=0 ORDER BY given_date DESC, id DESC", (self.id, ))
            all = cur.fetchall()
            if all is None:
                return []
            allnew = []
            for i in all:
                i = dict(i)
                i["amount"] = i["total_amount"]
                d = i["given_date"]
                i["parsed_date"] = [d, ctimes.stamp2german(d), ctimes.stamp2shortrelative(d, False)]
                allnew.append(i)
            return allnew
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def getTopbarAwards(self):
        if self.id == -3: return []
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM (SELECT \"reputation\" AS type, SUM(amount) AS data, given_date, message AS label, Null AS class, recognized FROM reputation WHERE user_id=? GROUP BY given_date/3600, label, recognized HAVING data!=0 UNION ALL SELECT \"badge\" AS type, badge_associations.data AS data, badge_associations.given_date, badges.name AS label, badges.class AS class, badge_associations.recognized AS recognized FROM badges, badge_associations WHERE userid=? AND badge_associations.badgeid=badges.id) ORDER BY given_date DESC LIMIT 50", (self.id, self.id))
            all = cur.fetchall()
            if all is None:
                return []
            allnew = []
            for i in all:
                i = dict(i)
                d = i["given_date"]
                i["parsed_date"] = [d, ctimes.stamp2german(d), ctimes.stamp2shortrelative(d, False)]
                allnew.append(i)
            return allnew
        except lite.Error as e:
            print(e)
            return []
        finally:
            if con:
                con.close()

    def getUnknownReputationChanges(self):
        if self.id == -3: return []
        try:
            con = lite.connect('databases/pilearn.db')
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
            con = lite.connect('databases/pilearn.db')
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

    def knowNewBadges(self):
        if self.id == -3: return []
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE badge_associations SET recognized=1 WHERE userid=? AND recognized=0", (self.id, ))
            all = con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def customflag(self, msg, who):
        try:
          con = lite.connect('databases/pilearn.db')
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
            con = lite.connect('databases/pilearn.db')
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
                    "relative_date": ctimes.stamp2shortrelative(d_["creation_date"]),
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
            con = lite.connect('databases/pilearn.db')
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
            con = lite.connect('databases/pilearn.db')
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
            con = lite.connect('databases/pilearn.db')
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
            con = lite.connect('databases/pilearn.db')
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
            con = lite.connect('databases/pilearn.db')
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
            con = lite.connect('databases/pilearn.db')
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
        return max(1, self.getDetail("reputation"))

    def getProfileData(self):
        return self.getDetail("profile")

    def getBadgeBreakdown(self):
        try:
            con = lite.connect('databases/pilearn.db')
            cur = con.cursor()
            cur.execute("SELECT Count(*), badges.class FROM badges, badge_associations WHERE badge_associations.badgeid=badges.id AND badge_associations.userid=? GROUP BY badges.class", (self.id, ))
            data = cur.fetchall()
            data = sorted(data, key=lambda x:["gold", "silver", "bronze"].index(x[1]))
            return data
        except lite.Error as e:
            print(e)
            return []
        finally:
            if con:
                con.close()

    def editAnnotation(self, id, d, v):
        try:
            con = lite.connect('databases/pilearn.db')
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
                con = lite.connect('databases/pilearn.db')
                con.row_factory = lite.Row
                cur = con.cursor()
                cur.execute("SELECT user.*, user_roles.is_mod, user_roles.is_dev, user_roles.is_team FROM user, user_roles WHERE user.id=? AND user.role=user_roles.id", (self.id, ))
                data = cur.fetchone()
                if data is None:
                    return {}
                return {
                    "id": data['id'],
                    "name": data["realname"],
                    "realname": data['realname'],
                    "email": data['email'],
                    "deleted": data['deleted'],
                    "banned": data['banned'],
                    "ban_reason": data['ban_reason'],
                    "ban_end": data['ban_end'],
                    "role": data['role'],
                    "reputation": data['reputation'] if not data["banned"] == 1 else 0,
                    "profile_image": data["profile_image"],
                    "password": secrets.token_urlsafe(16) if data["password"] != "" else "",
                    "aboutme":data["aboutme"] if data["aboutme"] != None else "",
                    "frozen": bool(data["frozen"]),
                    "suspension": json.loads(data["suspension"]) if data["suspension"] is not None else [],
                    "labels": json.loads(data["labels"]) if data["labels"] is not None else [],
                    "login_provider": data["login_provider"],
                    "mergeto": data["mergeto"],
                    "is_mod": data['is_mod'],
                    "is_dev": data['is_dev'],
                    "is_team": data['is_team'],
                    "profile": {
                        "place": data['profile_place'],
                        "website": data['profile_website'],
                        "twitter": data['profile_twitter'],
                        "projects": data['profile_projects'],
                    },
                    "certificate_full_name": data['certificate_full_name']
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
                "name": "Anonymer Benutzer",
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
                "login_provider": "none",
                "is_mod": False,
                "is_dev": False,
                "is_team": False
            }

    def isLoggedIn(self):
        return self.id != -3

    def getNotifications(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM notifications WHERE user_id=?", (self.id, ))
            return_value = []
            data = cur.fetchone()
            while data:
                return_value.append({
                    "type": data["type"],
                    "message": data["message"],
                    "link": "/notification/" + str(data["id"]) if (data["visible"] == 1) else data["link"],
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
        else:
            return self.isMod()


    def notify(self, type,msg,url):
        try:
            con = lite.connect('databases/pilearn.db')
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
            con = lite.connect('databases/pilearn.db')
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
            con = lite.connect('databases/pilearn.db')
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
            con = lite.connect('databases/pilearn.db')
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



    def getUserReached(self):
        if self.id == -3: return 0
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT Count(*) FROM enrollments As enr, courses, enrollments As own WHERE enr.courseid=courses.id AND own.courseid=courses.id AND own.permission=4 AND own.userid=?", (self.id, ))
            return cur.fetchone()[0]
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()


    def getForumQuestionCount(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT Count(*) FROM articles WHERE deleted=0 AND author=?", (self.id,))
            return cur.fetchone()[0]
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    def getForumAnswerCount(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT Count(*) FROM answers WHERE deleted=0 AND author=?", (self.id,))
            return cur.fetchone()[0]
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    def getForumVoteCount(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT Count(*) FROM score_votes WHERE nullified=0 AND user_id=?", (self.id,))
            return cur.fetchone()[0]
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()


    def getFlagHelpfulTotal(self):
        COUNT = 0
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT Count(*) FROM (SELECT * FROM closure_flags WHERE state=1 AND flagger_id=? UNION SELECT * FROM reopen_flags WHERE state=1 AND flagger_id=? UNION SELECT * FROM post_deletion_flags WHERE state=1 AND flagger_id=? UNION SELECT * FROM post_undeletion_flags WHERE state=1 AND flagger_id=?) As tbl", (self.id,self.id,self.id,self.id))
            COUNT += cur.fetchone()[0]
        except lite.Error as e:
            return COUNT
        finally:
            if con:
                con.close()

        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT Count(*) FROM custom_flag WHERE state=1 AND flagger_id=?", (self.id,))
            COUNT += cur.fetchone()[0]
        except lite.Error as e:
            return COUNT
        finally:
            if con:
                con.close()

        return COUNT


    def loginMethod_getAll(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id, provider, email FROM login_methods WHERE user_id=?", (self.id,))
            return list(map(dict,cur.fetchall()))
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def loginMethod_get(self, id):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id, provider, email FROM login_methods WHERE user_id=? AND id=?", (self.id,id))
            return dict(cur.fetchone())
        except lite.Error as e:
            raise e
        finally:
            if con:
                con.close()

    def loginMethod_remove(self, id):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("DELETE FROM login_methods WHERE id=? AND user_id=?", (id,self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def loginMethod_change(self, id, new_email, new_passtoken):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE login_methods SET email=?, password=? WHERE id=? AND user_id=?", (new_email, new_passtoken, id, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def loginMethod_add(self, type, email, passtoken):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO login_methods (user_id, provider, email, password) VALUES (?, ?, ?, ?)", (self.id, type, email, passtoken))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()



    @classmethod
    def getRoleTable(cls, role):
        try:
            con = lite.connect('databases/pilearn.db')
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
        if not cls.exists(id):
            u = cls.blank()
            u.id = id
            u._User__data = {
                "id": id,
                "name": "benutzer-" + str(id),
                "realname": "benutzer-" + str(id),
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
                "login_provider": "none",
                "is_mod": False,
                "is_dev": False,
                "is_team": False
            }
            return u
        u = cls(id)
        if u.getDetail("mergeto"):
            u = cls(u.getDetail("mergeto"))
        return u

    @classmethod
    def login(cls, email, password):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT user.* FROM user, login_methods WHERE login_methods.email=? AND (login_methods.password=? OR login_methods.password='') AND login_methods.provider='local_account' AND login_methods.user_id = user.id", (email, sha1(password)))
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
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT user.* FROM user, login_methods WHERE login_methods.provider=? AND login_methods.email=? AND login_methods.user_id = user.id", ("oauth:"+provider, email))
            data = cur.fetchone()
            if data is None:
                return -3
            else:
                if data["mergeto"]:
                    new_id = data["mergeto"]
                    return new_id
                if data["deleted"] != 0:
                    return -4
                else:
                    return data['id']
        except lite.Error as e:
            return -3
        finally:
            if con:
                con.close()

    @classmethod
    def register(cls, password, realname, email):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM user WHERE email=?", (email,))
            if cur.fetchone():
                return -3
            cur.execute("INSERT INTO user (name, realname, email, banned, role, reputation, aboutme, deleted, mergeto, labels, member_since) VALUES (?, ?, ?, 0, 1, 1, '', 0, 0, '[]', ?)", (realname, realname, email, time.time()))
            data = cur.lastrowid
            if password is not None:
                password = sha1(password)
                cur.execute("INSERT INTO login_methods (user_id, provider, email, password) VALUES (?, ?, ?, ?)", (data, "local_account", email, password))
            con.commit()
            return data
        except lite.Error as e:
            print(e)
            return -3
        finally:
            if con:
                con.close()

    @classmethod
    def reset_deletion(cls, email, password):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE user SET deleted=0 WHERE email=? AND password=?", (email, sha1(password)))
            con.commit()
            cur.execute("SELECT id FROM user WHERE email=? AND password=?", (email, sha1(password)))
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
            con = lite.connect('databases/pilearn.db')
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
    def passwdreset_new_request(cls, email):
        try:
            con = lite.connect('databases/pilearn.db')
            cur = con.cursor()
            cur.execute("SELECT id, user_id FROM login_methods WHERE provider='local_account' AND email=?", (email,))
            result = cur.fetchone()
            if not result: return False
            lm_id, user_id = result
            code = (str(random.randint(0,999)).zfill(3) + " " + str(random.randint(0,999)).zfill(3))
            cur.execute("INSERT INTO password_reset_requests (user_id, login_method_id, creation_date, deletion_date, verification_code) VALUES (?, ?, ?, NULL, ?)", (user_id, lm_id, time.time(), code))
            con.commit()
            return cur.lastrowid, code
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def passwdreset_has_request(cls, id):
        try:
            con = lite.connect('databases/pilearn.db')
            cur = con.cursor()
            cur.execute("SELECT id FROM password_reset_requests WHERE id=? AND deletion_date IS NULL", (id,))
            return cur.fetchone() is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def passwdreset_run_request(cls, id, code, new_pass):
        try:
            con = lite.connect('databases/pilearn.db')
            cur = con.cursor()
            cur.execute("SELECT login_method_id, user_id FROM password_reset_requests WHERE id=? AND verification_code=?", (id,code))
            result = cur.fetchone()
            if not result: return False
            lm_id, user_id = result

            cur.execute("UPDATE login_methods SET password=? WHERE id=? AND user_id=?", (sha1(new_pass), lm_id,user_id))
            cur.execute("UPDATE password_reset_requests SET deletion_date=? WHERE id=? AND verification_code=?", (time.time(),id,code))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def getByRole(cls, role):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM user WHERE role=? AND banned=1", (role,))
            data = cur.fetchall()
            data = list([User.from_id(x["id"]) for x in data])
            return data
        except lite.Error as e:
            print(e)
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def fetchOverviewList(cls, filter, page=1, size=10, is_mod=False):

        if filter not in ["reputation", "new", "moderators", "courses"]:
            if not (is_mod and filter in ["mod.suspended"]):
                filter = "reputation"

        size = int(str(size))
        if size not in [10, 20, 50]:
            size = 10

        limit = (int(str(page)) - 1) * size

        sql = "SELECT user.id FROM user WHERE deleted=0 AND mergeto=0 AND id>0 LIMIT %i,%i" %(limit,size)

        if filter == "reputation":
            sql = "SELECT user.id FROM user WHERE deleted=0 AND mergeto=0 AND id>0 ORDER BY reputation DESC LIMIT %i,%i" %(limit,size)
        elif filter == "new":
            sql = "SELECT user.id FROM user WHERE deleted=0 AND mergeto=0 AND id>0 ORDER BY id DESC LIMIT %i,%i" %(limit,size)
        elif filter == "courses":
            sql = "SELECT user.id FROM user, enrollments WHERE user.deleted=0 AND user.mergeto=0 AND user.id>0 AND enrollments.userid=user.id AND enrollments.permission >= 3 GROUP BY user.id ORDER BY Count(user.id) DESC, user.id DESC LIMIT %i,%i" %(limit,size)
        elif filter == "moderators":
            sql = "SELECT user.id FROM user, user_roles WHERE deleted=0 AND mergeto=0 AND user.id>0 AND user.role = user_roles.id AND user_roles.is_mod=1 AND user_roles.is_team=0 ORDER BY user.id DESC"
        elif filter == "mod.suspended":
            sql = "SELECT user.id FROM user WHERE deleted=0 AND mergeto=0 AND user.id>0 AND banned=1 ORDER BY ban_end DESC"

        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute(sql)
            data = cur.fetchall()
            data = list([User.from_id(x["id"]) for x in data])
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


def getRoles():
    try:
        con = lite.connect('databases/pilearn.db')
        cur = con.cursor()
        cur.execute("SELECT id, name, is_mod, is_dev, is_team FROM user_roles ORDER BY id ASC")
        data = cur.fetchall()
        DATA =  []
        for d in data:
            DATA.append({
                "id": d[0],
                "strid": str(d[0]),
                "name": d[1],
                "is_mod": bool(d[2]),
                "is_dev": bool(d[3]),
                "is_team": bool(d[4])
            })
        return DATA
    except lite.Error as e:
        return []
    finally:
        if con:
            con.close()
