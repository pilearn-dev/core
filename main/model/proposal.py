# coding: utf-8
import time
import secrets
import sqlite3 as lite
from flask import request, session, url_for
from sha1 import sha1
from model import privileges as mprivileges, tags as mtags, user as muser, courses as mcourses
from controller import times as ctimes

class Proposal:

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
            cur.execute("UPDATE proposals SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def hasUserCommitment(self, user):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM commitments WHERE user_id=? AND proposal_id=? AND invalidated=0", (user.id,self.id))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def addUserCommitment(self, user):
        worth = self.getUsersScore(user)
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO commitments (proposal_id, course_id, user_id, worth, fulfilled, creation_time, activation_time, invalidated) VALUES (?, 0, ?, ?, 0, ?, 0, 0)", (self.id,user.id,worth,time.time()))
            cur.execute("UPDATE proposals SET score=score+? WHERE id=?", (worth, self.id))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def createCourse(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO courses (topicid, title, shortdesc, longdesc, requirements, byline, sponsorid, state) VALUES (?, ?, ?, ?, ?, '', 0, 0)", (self.getDetail("topicid"), self.getDetail("title"), self.getDetail("shortdesc"), self.getDetail("longdesc"), self.getDetail("requirements")))
            courseid = cur.lastrowid
            cur.execute("INSERT INTO units (title, courseid, content, type, parent, availible) VALUES ('Neue Seite', ?, ?, ?, ?, 0)", (courseid,'[]','info',0))
            cur.execute("INSERT INTO enrollments (courseid, userid, lastunitid, permission) VALUES (?, ?, 0, 4)", (courseid,self.getDetail("proposer")))
            cur.execute("UPDATE commitments SET activation_time=? WHERE proposal_id=? AND invalidated=0", (time.time(), self.id))
            con.commit()
            self.setDetail("courseid", courseid)
            self.getProposer().notify("proposal_accept", "Dein Kursvorschlag '" + self.getTitle() + "' wurde angenommen. Komm und erstelle den Kurs!", "/c/" + str(courseid)+"/info")
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getTitle(self):
        return self.getDetail("title")

    def getTopic(self):
        return mcourses.Topic(self.getDetail("topicid"))

    def getCourse(self):
        print(self.getDetail("courseid"))
        return mcourses.Courses(self.getDetail("courseid"))

    def getProposer(self):
        return muser.User(self.getDetail("proposer"))

    def getCreationTime(self):
        t = self.getDetail("proposal_time")
        return [t, ctimes.stamp2german(t), ctimes.stamp2relative(t), ctimes.stamp2shortrelative(t)]

    def getScore(self):
        return self.getDetail("score")

    def getPercScore(self):
        return min(100, int((self.getScore() / 8.0) * 100))

    def getShortdesc(self):
        return self.getDetail("shortdesc")

    def getDescription(self):
        return self.getDetail("longdesc")

    def getRequirements(self):
        return self.getDetail("requirements")

    def isDeclined(self):
        return self.getDetail("declined") == 1

    def isDeleted(self):
        return self.getDetail("deleted") == 1

    def getInfo(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM proposals WHERE id=?", (self.id,))
            data = cur.fetchone()
            if data is None:
                raise ValueError("Proposal not found with id " + str(self.id))
            return {
                "id": data['id'],
                "topicid": data['topicid'],
                "title": data['title'],
                "shortdesc": data['shortdesc'],
                "longdesc": data['longdesc'],
                "requirements": data['requirements'],
                "proposer": data['proposer'],
                "score": data['score'],
                "declined": data['declined'],
                "decline_reason": data['decline_reason'],
                "deleted": data['deleted'],
                "delete_reason": data['delete_reason'],
                "courseid": data['courseid'],
                "proposal_time": data['proposal_time']
            }
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    @classmethod ### Needs to be implemented ###
    def getUsersScore(cls, user):
        #SELECT SUM(fulfilled), COUNT(*) FROM commitments WHERE user_id=? AND activation_time != 0 AND (fulfilled=1 OR activation_time < ?)#
        return 1.5


    @classmethod
    def exists(cls, id):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM proposals WHERE id=?", (id,))
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
            cur.execute("SELECT id FROM proposals WHERE deleted=0")
            data = cur.fetchall()
            DATA =  []
            for d in data:
                DATA.append(Proposal(d["id"]))
            return DATA
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def byCourse(cls, courseid):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM proposals WHERE courseid=?", (courseid,))
            data = cur.fetchone()
            return Proposal(data["id"])
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()

    @classmethod
    def byProposer(cls, proposer):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM proposals WHERE proposer=?", (proposer.id,))
            data = cur.fetchall()
            DATA =  []
            for d in data:
                DATA.append(Proposal(d["id"]))
            return DATA
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def getFeatured(cls):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM proposals WHERE deleted=0 AND declined=0 AND courseid=0 ORDER BY proposal_time ASC")
            data = cur.fetchall()
            DATA =  []
            for d in data:
                DATA.append(Proposal(d["id"]))
            return DATA
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def createNew(cls, topicid, title, shortdesc, longdesc, requirements, proposer):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO proposals (topicid, title, shortdesc, longdesc, requirements, proposer, score, declined, decline_reason, deleted, delete_reason, courseid, proposal_time) VALUES (?, ?, ?, ?, ?, ?, 0, 0, '', 0, '', 0, ?)", (topicid, title, shortdesc, longdesc, requirements, proposer.id, time.time()))
            con.commit()
            return cls(cur.lastrowid)
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()
