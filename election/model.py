# coding: utf-8
import os, json
import secrets
import sqlite3 as lite
from flask import request, session, url_for
from sha1 import sha1
from main.model import user as muser
from main.controller import times as ctimes
import time, datetime

class Vote:

    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def setDetail(self, d, v):
        if self.id == -3: return
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE election_votes SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def getDetail(self, d):
        return self.__data[d]

    def setSecondVote(self, candidate):
        b = self.getDetail("ballot")
        b2 = {
            "first": b["first"],
            "second": candidate,
            "third": b["third"]
        }
        self.setDetail("ballot", json.dumps(b2))

    def setThirdVote(self, candidate):
        b = self.getDetail("ballot")
        b2 = {
            "first": b["first"],
            "second": b["second"],
            "third": candidate
        }
        self.setDetail("ballot", json.dumps(b2))

    def setFirstVote(self, candidate):
        b = self.getDetail("ballot")
        b2 = {
            "first": candidate,
            "second": b["second"],
            "third": b["third"]
        }
        self.setDetail("ballot", json.dumps(b2))

    def as_list(self):
        b = self.getDetail("ballot")
        return [b["first"], b["second"], b["third"]]

    def getInfo(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM election_votes WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                return
            return {
                "id": data['id'],
                "election_id": data['election_id'],
                "voter": data['voter'],
                "ballot": json.loads(data["ballot"])
            }
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    @classmethod
    def from_user(cls, election_id, user):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM election_votes WHERE election_id=? AND voter=?", (election_id, user.id))
            data = cur.fetchone()
            if data is None:
                return None
            dn = cls(data["id"])
            return dn
        except lite.Error as e:
            print(e)
            return None
        finally:
            if con:
                con.close()

    @classmethod
    def from_election(cls, election_id):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM election_votes WHERE election_id=?", (election_id,))
            data = cur.fetchall()
            dn = list(map(lambda x:cls(x["id"]),data))
            return dn
        except lite.Error as e:
            print(e)
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def new(cls, election_id, user):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO election_votes (election_id, voter, ballot) VALUES (?, ?, '{\"first\":0,\"second\":0,\"third\":0}')", (election_id, user.id))
            con.commit()
            return cls(cur.lastrowid)
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

class Question:
    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def getDetail(self, d):
        return self.__data[d]

    def getQ(self):
        return self.getDetail("question")

    def getA(self):
        return self.getDetail("answer")

    def getNomId(self):
        return self.getDetail("nomination_id")

    def setA(self, a):
        self.setDetail("answer", a)

    def setState(self, s):
        self.setDetail("state", s)

    def isLate(self):
        if self.getDetail("state") == 1:
            return True
        if self.getDetail("state") == 0 and int(time.time()) - self.getDetail("asked_date") > 2*24*60*60:
            return True
        return False

    def setDetail(self, d, v):
        if self.id == -3: return
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE election_questions SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def getInfo(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM election_questions WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                return
            return {
                "id": data['id'],
                "election_id": data['election_id'],
                "nomination_id": data['nomination_id'],
                "is_community": bool(data["is_community"]),
                "question": data['content'],
                "answer": data['answer'],
                "author": muser.User.from_id(data['author']),
                "state": data['state'],
                "asked_date": data['asked_date']
            }
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    @classmethod
    def from_nomination(cls, election_id, nomination_id):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM election_questions WHERE election_id=? AND nomination_id=?", (election_id, nomination_id))
            data = cur.fetchall()
            dd = []
            for d in data:
                dn = Question(d["id"])
                dd.append(dn)
            return dd
        except lite.Error as e:
            print(e)
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def new(cls, election_id, nomination_id, user, message, is_comm):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO election_questions (election_id, nomination_id, is_community, content, answer, state, asked_date, author) VALUES (?, ?, ?, ?, '', 0, ?, ?)", (election_id, nomination_id, is_comm, message, int(time.time()), user.id))
            con.commit()
            return cls(cur.lastrowid)
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

class Nomination:
    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def getDetail(self, d):
        return self.__data[d]

    def getCandidate(self):
        return self.getDetail("candidate")

    def isRetracted(self):
        return self.getDetail("state") == -2

    def isFailed(self):
        return self.getDetail("state") == -1

    def isElected(self):
        return self.getDetail("state") == 1

    def getMessage(self):
        return self.getDetail("message")

    def getQuestions(self):
        return Question.from_nomination(self.getDetail("election_id"), self.id)

    def setDetail(self, d, v):
        if self.id == -3: return
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE nominations SET "+d+"=? WHERE id=?", (v, self.id))
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
            cur.execute("SELECT * FROM nominations WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                return
            return {
                "id": data['id'],
                "election_id": data["election_id"],
                "message": data['message'],
                "answer_score": data['answer_score'],
                "candidate": muser.User.from_id(data['candidate']),
                "state": data['state']
            }
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    @classmethod
    def exists(cls, election_id, user):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM nominations WHERE candidate=? AND election_id=?", (user.id, election_id))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def from_election(cls, election_id):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM nominations WHERE election_id=? ORDER BY state DESC", (election_id, ))
            data = cur.fetchall()
            dd = []
            for d in data:
                dn = cls(d["id"])
                dd.append(dn)
            return dd
        except lite.Error as e:
            print(e)
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def from_user(cls, election_id, user):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM nominations WHERE election_id=? AND candidate=?", (election_id, user.id))
            data = cur.fetchone()
            dn = cls(data["id"])
            return dn
        except lite.Error as e:
            print(e)
            return None
        finally:
            if con:
                con.close()

    @classmethod
    def new(cls, election_id, user, message):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO nominations (election_id, message, answer_score, candidate, state) VALUES (?, ?, 0, ?, 0)", (election_id, message, user.id))
            con.commit()
            return cls(cur.lastrowid)
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

class Election:
    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def getDetail(self, d):
        return self.__data[d]

    def getTitle(self):
        return self.getDetail("title")

    def getMessage(self):
        return self.getDetail("message")

    def getPosition(self):
        return self.getDetail("position")

    def getState(self):
        return self.getDetail("state")

    def getCandidates(self):
        return Nomination.from_election(self.id)

    def getVotes(self):
        return Vote.from_election(self.id)

    def getPlaces(self):
        return self.getDetail("places")

    def getMinCandRep(self):
        return self.getDetail("mincandrep")

    def setDetail(self, d, v):
        if self.id == -3: return
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE elections SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def tallyVotes(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT ballot, count(*) AS vc FROM votes WHERE election_id=? GROUP BY ballot", (self.id, ))
            data = []
            d = cur.fetchall()
            for i in d:
                b = json.loads(i["ballot"])
                arr = [i["vc"], b["first"]]
                if b["second"]:
                    arr.append(b["second"])
                if b["third"]:
                    arr.append(b["third"])
                data.append(arr)
            return data
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    def updateByTime(self):
        state = self.getState()
        now = datetime.datetime.now()
        if state == 1 and self.getRelativeTime(7) < now:
            self.setDetail("state", 2)
            state = 2
        if state == 2 and self.getRelativeTime(14) < now:
            self.setDetail("state", 3)
            state = 3
        if state == 3 and self.getRelativeTime(19) < now:
            self.setDetail("state", 4)
            state = 4
        if state == 4 and self.getRelativeTime(21) < now:
            self.setDetail("state", 5)
            state = 5
        if state == 5 and self.getRelativeTime(28) < now:
            self.setDetail("state", 6)
            state = 6
        self.__data = self.getInfo()


    def getRelativeTime(self, days):
        date_original = datetime.datetime.fromtimestamp(self.getDetail("election_start_date"))
        date_proper = datetime.datetime(year=date_original.year,month=date_original.month,day=date_original.day, hour=19, minute=0, second=0)
        delta = datetime.timedelta(days)
        result = date_proper + delta
        return result

    def getScheduleDatetime(self, days):
        date = self.getRelativeTime(days)
        t = time.mktime(date.timetuple())
        return [t, ctimes.stamp2german(t), ctimes.stamp2relative(t)]

    def getInfo(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM elections WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                return
            return {
                "id": data['id'],
                "title": data["title"],
                "message": data['message'],
                "places": data['places'],
                "position": data['position'],
                "state": data['state'],
                "minvoterep": data["minvoterep"],
                "mincandrep": data["mincandrep"],
                "election_start_date": data["election_start_date"]
            }
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    @classmethod
    def new(cls):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            STDTEXT = u"""Unser Konzept ist es, dass &pi;-Learn eine Community-kontrollierte Open Learning-Plattform sein soll. Dieses Konzept wird zum ersten durch die Reputation erfüllt, eine Punktzahl, die jedem Benutzer aufgrund der Qualität seiner Inhalte zugewiesen wird. Dieser Reputation entsprechen bestimmte Privilegien, mit denen die Benutzer helfen können, diese Seite zu verwalten.

Weiterhin wollen wir, dass jeder sein Wissen gleichberechtigt mit anderen teilen darf und vermeiden es daher, den Inhalt durch von uns beauftragte Benutzer zu moderieren. Statdessen soll dieser Auftrag von den Benutzern dieser Webseite selbst kommen. Darum halten wir bei Bedarf Wahlen ab, um Moderatoren zu ernenen. Diesen Moderatoren kommt eine besondere Verantwortung zu, da sie Zugriff auf die höchsten Privilegien erhalten.

Moderatoren verwalten und kontrollieren ("moderieren") diese Webseite. Sie können dafür zum Beispiel Benutzer, die sich nicht an die Regeln halten, sperren oder sogar löschen."""
            cur.execute("INSERT INTO elections (title, message, places, position, state, minvoterep, mincandrep) VALUES ('Unbestimmte Wahl', ?, 1, 'Benutzergruppe', 1, 50, 100)", (STDTEXT,))
            con.commit()
            return cur.lastrowid
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def exists(cls, id):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM elections WHERE id=?", (id,))
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
            cur.execute("SELECT * FROM elections ORDER BY id DESC")
            data = cur.fetchall()
            l = list(map(lambda x:Election(x[0]), data))
            return l
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()
