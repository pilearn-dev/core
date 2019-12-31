import os, json
import sqlite3 as lite
from flask import request, session, url_for
from sha1 import sha1
from model import privileges as mprivileges, tags as mtags
from model.user import User as muser_User

def _sl(list):
    return "(\"" + '", "'.join(list) + "\")"

class ReviewQueue:

    def __init__(self, file, core_table, finished_at):
        self.file = file
        self.core_table = core_table
        self.finished_at = finished_at

    def getOpenCount(self, u):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM "+self.core_table+"_queue WHERE state=0 AND id NOT IN (SELECT queue_id FROM "+self.core_table+"_reviews WHERE reviewer_id=?) AND id NOT IN (SELECT queue_id FROM "+self.core_table+"_flags WHERE flagger_id=?)", (u.id, u.id))
            data = len(cur.fetchall())
            return data
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    def getOpenItemId(self, u):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM "+self.core_table+"_queue WHERE state=0 AND id NOT IN (SELECT queue_id FROM "+self.core_table+"_reviews WHERE reviewer_id=?) AND id NOT IN (SELECT queue_id FROM "+self.core_table+"_flags WHERE flagger_id=?)", (u.id, u.id))
            data = cur.fetchone()
            if data is None:
                return -1
            else:
                return data["id"]
        except lite.Error as e:
            print(e)
            return -1
        finally:
            if con:
                con.close()

    def isOpenReview(self, id, u):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM "+self.core_table+"_queue WHERE state=0 AND id=? AND id NOT IN (SELECT queue_id FROM "+self.core_table+"_reviews WHERE reviewer_id=?) AND id NOT IN (SELECT queue_id FROM "+self.core_table+"_flags WHERE flagger_id=? AND state!=1)", (id, u.id, u.id))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def addReview(self, id, u, result, msg=""):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO "+self.core_table+"_reviews (queue_id, item_id, reviewer_id, result, comment) VALUES (?, ?, ?, ?, ?)", (id, self.getItemData(id)["item_id"], u.id, result, msg))
            cur.execute("SELECT * FROM "+self.core_table+"_reviews WHERE queue_id=? AND result != 1", (id,))
            not_skipped = cur.fetchall()
            count = len(not_skipped)
            if not self.isCompleted(id):
                if u.isMod() and result != 1:
                    cur.execute("UPDATE "+self.core_table+"_queue SET state=1, result=? WHERE id=?", (result, id))
                elif count > self.finished_at:
                    troc = [r["result"] for r in not_skipped]
                    outcomes = sorted(list(set([r["result"] for r in not_skipped])))
                    oc = 0
                    occ = 0
                    for outcome in outcomes:
                        if troc.count(outcome) == self.finished_at:
                            occ = troc.count(outcome)
                            oc = outcome
                    if occ != 0:
                        cur.execute("UPDATE "+self.core_table+"_queue SET state=1, result=? WHERE id=?", (oc, id))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def isCompleted(self, id):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT state FROM "+self.core_table+"_queue WHERE id=?", (id,))
            return cur.fetchone()[0] == 1
        except lite.Error as e:
            print((e + ":"))
            return False
        finally:
            if con:
                con.close()

    def markFlags(self, id, state):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE "+self.core_table+"_flags SET state=? WHERE queue_id=?", (state, id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def invalidateReview(self, id, result):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE "+self.core_table+"_queue SET state=2, result=? WHERE id=?", (result, id))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def completeReview(self, id, result):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE "+self.core_table+"_queue SET state=1, result=? WHERE id=?", (result, id))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def getItemData(self, id):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM "+self.core_table+"_queue WHERE id=?", (id,))
            data = cur.fetchone()
            if data is None:
                return -1
            else:
                return data
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getItemFlags(self, id):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM "+self.core_table+"_flags WHERE queue_id=?", (id,))
            data = cur.fetchall()
            return data
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def getReviews(self, id):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM "+self.core_table+"_reviews WHERE queue_id=?", (id,))
            data = cur.fetchall()
            return data
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def getFromUser(self, u):
        con = None
        try:
            uid = u.id
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM "+self.core_table+"_flags WHERE flagger_id=?", (uid,))
            data = cur.fetchall()
            nw_data = []
            for row in data:
                row = dict(row)
                row["flagger"] = muser_User.from_id(row["flagger_id"])
                nw_data.append(row)
            return nw_data
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

class FlagQueue:

    def __init__(self, file, prefix):
        self.file = file
        self.core_table = prefix

    def getItems(self, filter=None):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            if not filter:
                cur.execute("SELECT * FROM "+self.core_table+"_flaglist ORDER BY state ASC")
            else:
                cur.execute("SELECT * FROM "+self.core_table+"_flaglist WHERE item_type IN "+_sl(filter)+" ORDER BY state ASC")
            data = cur.fetchall()
            if data is None:
                return []
            else:
                return data
        except lite.Error as e:
            print(e)
            return []
        finally:
            if con:
                con.close()

    def getOpenItemCount(self, filter=None):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            if not filter:
                cur.execute("SELECT * FROM "+self.core_table+"_flaglist WHERE state=0")
            else:
                cur.execute("SELECT * FROM "+self.core_table+"_flaglist WHERE state=0 AND item_type IN "+_sl(filter))
            data = len(cur.fetchall())
            return data
        except lite.Error as e:
            print(e)
            return 0
        finally:
            if con:
                con.close()

    def manageFlag(self, qid, fid, state, response=""):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE "+self.core_table+"_flag SET state=?, response=? WHERE id=? AND queue_id=?", (state, response, fid, qid))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def completeReview(self, id):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE "+self.core_table+"_flaglist SET state=1 WHERE id=?", (id,))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def getItemData(self, id):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM "+self.core_table+"_flaglist WHERE id=?", (id,))
            data = cur.fetchone()
            if data is None:
                return None
            else:
                return data
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getItemFlags(self, id):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM "+self.core_table+"_flag WHERE queue_id=?", (id,))
            data = cur.fetchall()
            return data
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def getItemOpenFlagsCount(self, id):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT COUNT(*) FROM "+self.core_table+"_flag WHERE state=0 AND queue_id=?", (id,))
            data = cur.fetchone()
            return data[0]
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    def getFlagData(self, id):
        con = None
        try:
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM "+self.core_table+"_flag WHERE id=?", (id,))
            data = cur.fetchone()
            return data
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()

    def getFromUser(self, u):
        con = None
        try:
            uid = u.id
            con = lite.connect('databases/'+self.file)
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM "+self.core_table+"_flag WHERE flagger_id=? ORDER BY item_type, id DESC", (uid,))
            data = cur.fetchall()
            nw_data = []
            for row in data:
                row = dict(row)
                row["flagger"] = muser_User.from_id(row["flagger_id"])
                nw_data.append(row)
            return nw_data
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

PostClosure = ReviewQueue("pilearn.db", "closure", 3)
PostReopen = ReviewQueue("pilearn.db", "reopen", 3)
PostDeletion = ReviewQueue("pilearn.db", "post_deletion", 3)
AnswerDeletion = ReviewQueue("pilearn.db", "answer_deletion", 3)
CustomQueue = FlagQueue("pilearn.db", "custom")

def getReviewItemCount(u):
    return (PostClosure.getOpenCount(u) +
           PostReopen.getOpenCount(u) +
           PostDeletion.getOpenCount(u) +
           AnswerDeletion.getOpenCount(u))

def getReviewCountState(u):
    count = getReviewItemCount(u)
    if count > 15:
        return "critical"
    elif count > 0:
        return "some"
    return "null"

def getFlaggedItemCount(u):
    if u.isMod():
        filter = None
    else:
        filter = []
    return CustomQueue.getOpenItemCount(filter)

def getFlaggedCountState(u):
    count = getFlaggedItemCount(u)
    if count > 5:
        return "critical"
    elif count > 0:
        return "some"
    return "null"
