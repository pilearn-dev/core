# coding: utf-8
import re, time
import sqlite3 as lite
from model import user as muser, courses as mcourses
from controller import times as ctimes, placeholder as cplaceholder
import tags as mtags
import markdown

class Answer:

    FREEZONS = [
        u"Diese Antwort wurde eingefroren, **bis alle Streitigkeiten über den Inhalt beendet sind**.",
        u"Diese Antwort wurde eingefroren, da sie eine **hohe Anzahl an Kommentaren** angezogen hat, die entfernt werden mussten.",
        u"Diese Antwort ist **kein gutes Beispiel für eine Antwort in diesem Forum**, kann aber aufgrund ihrer Verbreitung nicht entfernt werden. Daher wurde die Antwort *in der Zeit stehen gelassen* und kann nicht verändert werden.",
        u""
    ]

    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def getDetail(self, d):
        return self.__data[d]

    def addRevision(self, content, user, comment, review=-1):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO answer_revisions (forumID, answerID, articleID, editor, new_content, review_id, comment, type, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, 'edit', ?)", (self.getDetail("forumID"), self.id, self.getDetail("articleID"), user.id, content, review, comment, time.time()))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def addRevComm(self, tp, user, comment):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO answer_revisions (forumID, answerID, articleID, editor, new_content, review_id, comment, type, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (self.getDetail("forumID"), self.id, self.getDetail("articleID"), user.id, self.getContent(), -1, comment, tp, time.time()))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def hasRevision(self):
        return self.getRevisionCount() > 1

    def getRevisionCount(self, x=False):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if x:
                cur.execute("SELECT * FROM answer_revisions WHERE forumID=? AND articleID=? AND answerID=?", (self.getDetail("forumID"), self.getDetail("articleID"), self.id))
            else:
                cur.execute("SELECT * FROM answer_revisions WHERE forumID=? AND articleID=? AND answerID=? AND type='edit' OR type='static'", (self.getDetail("forumID"), self.getDetail("articleID"), self.id))
            return len(cur.fetchall())
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    def getRevision(self, id):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if id == "latest":
                cur.execute("SELECT * FROM answer_revisions WHERE forumID=? AND articleID=? AND answerID=? AND type='edit' OR type='static' ORDER BY id DESC", (self.getDetail("forumID"), self.getDetail("articleID"), self.id))
                data = cur.fetchone()
            else:
                cur.execute("SELECT * FROM answer_revisions WHERE forumID=? AND articleID=? AND answerID=? ORDER BY id ASC", (self.getDetail("forumID"), self.getDetail("articleID"), self.id))
                data = cur.fetchall()[id-1]
            data = {
                "revid": (self.getRevisionCount() if id == "latest" else id),
                "id": data["id"],
                "type": data["type"],
                "editor": muser.User.safe(data["editor"]),
                "content": data["new_content"],
                "comment": data["comment"],
                "timestamp": data["timestamp"],
                "relative_time": ctimes.stamp2shortrelative(data["timestamp"]),
                "absolute_time": ctimes.stamp2german(data["timestamp"])
            }
            return data
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def getRevisionById(self, id):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM answer_revisions WHERE answerID=? AND id=?", (self.id, id))
            data = cur.fetchone()
            data = {
                "id": data["id"],
                "type": data["type"],
                "editor": muser.User.safe(data["editor"]),
                "content": data["new_content"],
                "comment": data["comment"],
                "timestamp": data["timestamp"],
                "relative_time": ctimes.stamp2shortrelative(data["timestamp"]),
                "absolute_time": ctimes.stamp2german(data["timestamp"])
            }
            return data
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def getAllRevisions(self):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM answer_revisions WHERE forumID=? AND articleID=? AND answerID=? ORDER BY id ASC", (self.getDetail("forumID"), self.getDetail("articleID"), self.id))
            i = 0
            rev = 1
            data_ = cur.fetchall()
            data = []
            for row in data_:
                i += 1
                r =self.getRevision(i)
                if row["type"] == "edit" or row["type"] == "static":
                    r["revid"] = rev
                    rev += 1
                data.append(r)
            return data[::-1]
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def getCreationTime(self):
        t = self.getDetail("creation_date")
        return [t, ctimes.stamp2german(t), ctimes.stamp2shortrelative(t)]

    def getLastEditTime(self):
        t = self.getDetail("last_edit_date")
        return [t, ctimes.stamp2german(t), ctimes.stamp2shortrelative(t)]

    def getLastEditor(self):
        e = self.getDetail("last_editor")
        return muser.User.safe(e)

    def getComments(self, is_mod=False):
        return ForumComment.byPost("answer", self.id, is_mod)

    def getCommentCounts(self, is_mod=False):
        return ForumComment.getCommentCounts("answer", self.id)

    def getUserVote(self, u):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT direction FROM score_votes WHERE target_type='answer' AND target_id=? AND user_id=?", (self.id, u.id))
            d = cur.fetchone()
            if d is None:
                return None
            return d[0]
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    def addVote(self, u, delta):
        v = self.getUserVote(u)
        if v is None:
            try:
                con = lite.connect('databases/forum.db')
                con.row_factory = lite.Row
                cur = con.cursor()
                cur.execute("INSERT INTO score_votes (user_id, direction, reputation, target_type, target_id, nullified) VALUES (?, ?, ?, 'answer', ?, 0)", (u.id, delta, 3*delta, self.id))
                d = con.commit()
                self.setDetail("score", self.getInfo()["score"]+delta)
                au = self.getAuthor()
                if au.id != -1 and au.id != -3:
                    au.setReputationChange("forum_vote", "["+Article(self.getDetail("articleID")).getHTMLTitle()+"](/f/"+str(self.getDetail("forumID"))+"/" + str(self.getDetail("articleID")) +"#answer-"+str(self.id)+")", 3*delta)
                    au.setDetail("reputation", au.getDetail("reputation")+3*delta)
                return delta, self.getInfo()["score"]
            except lite.Error as e:
                return False
            finally:
                if con:
                    con.close()
        else:
            if v == delta:
                try:
                    con = lite.connect('databases/forum.db')
                    con.row_factory = lite.Row
                    cur = con.cursor()
                    cur.execute("DELETE FROM score_votes WHERE user_id=? AND target_id=? AND target_type='answer'", (u.id, self.id))
                    d = con.commit()
                    self.setDetail("score", self.getInfo()["score"]-delta)
                    au = self.getAuthor()
                    if au.id != -1 and au.id != -3:
                        au.setReputationChange("forum_vote", "["+Article(self.getDetail("articleID")).getHTMLTitle()+"](/f/"+str(self.getDetail("forumID"))+"/" + str(self.getDetail("articleID")) +"#answer-"+str(self.id)+")", -3*delta)
                        au.setDetail("reputation", au.getDetail("reputation")-3*delta)
                    return 0, self.getInfo()["score"]
                except lite.Error as e:
                    return False
                finally:
                    if con:
                        con.close()
            else:
                try:
                    con = lite.connect('databases/forum.db')
                    con.row_factory = lite.Row
                    cur = con.cursor()
                    cur.execute("UPDATE score_votes SET direction=?, reputation=? WHERE user_id=? AND target_id=? AND target_type='answer'", (delta, 3*delta, u.id, self.id))
                    d = con.commit()
                    self.setDetail("score", self.getInfo()["score"]+2*delta)
                    au = self.getAuthor()
                    if au.id != -1 and au.id != -3:
                        au.setReputationChange("forum_vote", "["+Article(self.getDetail("articleID")).getHTMLTitle()+"](/f/"+str(self.getDetail("forumID"))+"/" + str(self.getDetail("articleID")) +"#answer-"+str(self.id)+")", 6*delta)
                        au.setDetail("reputation", au.getDetail("reputation")+6*delta)
                    return delta, self.getInfo()["score"]
                except lite.Error as e:
                    return False
                finally:
                    if con:
                        con.close()

    def delvote(self, who, in_review_final=False):
        try:
          con = lite.connect('databases/forum.db')
          con.row_factory = lite.Row
          cur = con.cursor()
          cur.execute("INSERT INTO deletion_votes (postType, postId, voteOwner, voteCastDate, active) VALUES ('answer', ?, ?, ?, 1)", (self.id, who.id, time.time()))
          con.commit()
          cur.execute("SELECT * FROM deletion_votes WHERE postType='answer' AND postId=? AND active=1", (self.id, ))
          con.commit()
          all = cur.fetchall()
          num = len(all)
          if num == 3 + min(5,int(self.getScore()/5)) or who.isMod():
              self.setDetail("deleted", 1)
              self.setDetail("deletionReason", "vote")
              self.__data = self.getInfo()

              voter_html = ""
              index = 0
              for flag in all:
                  flagger = muser.User.safe(flag[2])
                  if 0 < index < len(all)-1:
                      voter_html += ", "
                  elif index == len(all)-1 and index != 0:
                      voter_html += " und "
                  index += 1
                  voter_html += "<a href='/u/" + str(flagger.id) + "'>" + flagger.getHTMLName(False) + "</a>"

              self.addRevComm("deleted", muser.User.from_id(-1), voter_html)
          return True
        except lite.Error as e:
          print(e)
          return False
        finally:
          if con:
              con.close()

    def getDelVotes(self):
        try:
          con = lite.connect('databases/forum.db')
          con.row_factory = lite.Row
          cur = con.cursor()
          cur.execute("SELECT Count(*) FROM deletion_votes WHERE postType='answer' AND postId=? AND active=1", (self.id, ))
          con.commit()
          return cur.fetchone()[0]
        except lite.Error as e:
          return 0
        finally:
          if con:
              con.close()

    def undelvote(self, who, in_review_final=False):
          try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            qid = None
            cur.execute("INSERT INTO undeletion_votes (postType, postId, voteOwner, voteCastDate, active) VALUES ('answer', ?, ?, ?, 1)", (self.id, who.id, time.time()))
            con.commit()
            cur.execute("SELECT * FROM undeletion_votes WHERE postType='answer' AND postId=? AND active=1", (self.id, ))
            con.commit()
            all = cur.fetchall()
            num = len(all)
            if num == 3 + min(5,int(self.getScore()/5)) or who.isMod():
                cur.execute("UPDATE deletion_votes SET active=0 WHERE postType='answer' AND postId=? AND active=1", (self.id,))
                cur.execute("UPDATE undeletion_votes SET active=0 WHERE postType='answer' AND postId=? AND active=1", (self.id,))
                con.commit()
                self.setDetail("deleted", 0)

                voter_html = ""
                index = 0
                for flag in all:
                    flagger = muser.User.safe(flag[2])
                    if 0 < index < len(all)-1:
                        voter_html += ", "
                    elif index == len(all)-1 and index != 0:
                        voter_html += " und "
                    index += 1
                    voter_html += "<a href='/u/" + str(flagger.id) + "'>" + flagger.getHTMLName(False) + "</a>"

                self.addRevComm("undeleted", muser.User.from_id(-1), voter_html)
            return True
          except lite.Error as e:
            print(e)
            return False
          finally:
            if con:
                con.close()

    def getUndelVotes(self):
        try:
          con = lite.connect('databases/forum.db')
          con.row_factory = lite.Row
          cur = con.cursor()
          cur.execute("SELECT Count(*) FROM undeletion_votes WHERE postType='answer' AND postId=? AND active=1", (self.id, ))
          con.commit()
          return cur.fetchone()[0]
        except lite.Error as e:
          return 0
        finally:
          if con:
              con.close()

    def customflag(self, msg, who):
        try:
          con = lite.connect('databases/user.db')
          con.row_factory = lite.Row
          cur = con.cursor()
          qid = None
          cur.execute("SELECT * FROM custom_flaglist WHERE item_id=? AND item_type='forum.answer' AND state=0", (self.id,))
          qid = cur.fetchone()
          if qid is None:
              cur.execute("INSERT INTO custom_flaglist (item_id, item_type, state) VALUES (?, 'forum.answer', 0)", (self.id,))
              qid = cur.lastrowid
          else:
              qid = qid["id"]
          cur.execute("INSERT INTO custom_flag (item_id, item_type, queue_id, state, flagger_id, comment) VALUES (?, 'forum.answer', ?, 0, ?, ?)", (self.id, qid, who.id, msg))
          con.commit()
          return True
        except SyntaxError as e:#lite.Error as e:
          print(e)
          return False
        finally:
          if con:
              con.close()

    def setDetail(self, d, v):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE answers SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def mayBeSeen(self, user):
        if self.isDeleted() and (user.may("general_autoMod") or user.isMod() or self.getAuthor().id == user.id):
            return True
        elif not self.isDeleted():
            return True
        else:
            return False

    def isAccepted(self):
        return self.getDetail("isAcceptedAnswer")

    def getScore(self):
        return self.getDetail("score")

    def getAward(self):
        return self.getDetail("awardRep")

    def isFrozen(self):
        return self.getDetail("frozen")

    def getFrozenBy(self):
        fb = self.getDetail("frozenBy")
        if fb == 0:
            fb = -3
        return muser.User.safe(fb)

    def getFrozenMessage(self):
        return self.getDetail("frozenMessage")

    def getContent(self):
        return self.getDetail("content")

    def getModNotice(self):
        notice = self.getDetail("moderatorNotice")
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM post_notices WHERE id=?", (notice, ))
            n = cur.fetchone()
            if n:
                return n["body"]
            return notice
        except lite.Error as e:
            return notice
        finally:
            if con:
                con.close()

    def getAuthor(self):
        return muser.User.safe(self.getDetail("author"))

    def getArticle(self):
        return Article(self.getDetail("articleID"))

    def isDeleted(self):
        return self.getDetail("deleted") == 1 or self.isDestroyed()

    def getDeleteMessage(self):
        del_reason = self.getDetail("deletionReason")
        if del_reason == "owner":
            return u"<strong>gelöscht</strong> von seinem Urheber"
        elif del_reason == "spam":
            return u"<strong>gelöscht</strong> als Werbung/beleidigender/missbräuchlicher Inhalt"
        elif del_reason == "offensive":
            return u"<strong>gelöscht</strong> als Werbung/beleidigender/missbräuchlicher Inhalt"
        elif del_reason == "dangerous":
            return u"<strong>gelöscht</strong> als Werbung/beleidigender/missbräuchlicher Inhalt"
        elif del_reason == "queue":
            return u"<strong>gelöscht</strong> aufgrund des Votums in einer Moderationsliste"
        elif del_reason == "vote":
            try:
                con = lite.connect('databases/forum.db')
                con.row_factory = lite.Row
                cur = con.cursor()
                cur.execute("SELECT * FROM deletion_votes WHERE postId=? AND postType='answer' AND active=1 ORDER BY voteCastDate", (self.id, ))
                con.commit()
                flags = cur.fetchall()
                voters = ""
                voter_html = ""
                index = 0
                maxtime = 0
                for flag in flags:
                    if flag[3] > maxtime: maxtime = flag[3]
                    flagger = muser.User.safe(flag[2])
                    if 0 < index < len(flags)-1:
                        voter_html += ", "
                    elif index == len(flags)-1 and index != 0:
                        voter_html += " und "
                    index += 1
                    if flagger.isDeleted():
                        voter_html += flagger.getHTMLName(False)
                    else:
                        voter_html += "<a href='/u/" + str(flagger.id) + "'>" + flagger.getHTMLName(False) + "</a>"

                return u"<strong>gelöscht</strong> von " + voter_html + " " + ctimes.stamp2shortrelative(maxtime)
            except lite.Error as e:
                return u"<strong>gelöscht</strong>"
            finally:
                if con:
                    con.close()
        else:
            return u"<strong>gelöscht</strong>"

    def isDestroyed(self):
        return self.getDetail("deleted") == 2

    def getInfo(self):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM answers WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                raise ValueError("Answer not found with id " + str(self.id))
            return {
                "id": data['id'],
                "forumID": data['forumID'],
                "articleID": data['articleID'],
                "author": data['author'],
                "score": data['score'],
                "content": data['content'],
                "awardRep": data['awardRep'],
                "awardBy": data['awardBy'],
                "awardMessage": data['awardMessage'],
                "isAcceptedAnswer": data['isAcceptedAnswer'],

                "frozen": data['frozen'],
                "frozenBy": data['frozenBy'],
                "frozenMessage": data['frozenMessage'],
                "deleted": data['deleted'],
                "deletionReason": data['deletionReason'],

                "moderatorNotice": data['moderatorNotice'],
                "creation_date": data['creation_date'],
                "last_edit_date": data['last_edit_date'],
                "last_editor": data['last_editor']
            }
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    @classmethod
    def exists(cls, forum_id, id=None):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if id is not None:
                cur.execute("SELECT * FROM answers WHERE id=? AND forumID=?", (id,forum_id))
            else:
                cur.execute("SELECT * FROM answers WHERE id=?", (forum_id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def createNew(cls, forumID, articleID, content, user):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO answers (forumID, articleID, author, score, content, awardRep, awardBy, awardMessage, isAcceptedAnswer, frozen, frozenBy, frozenMessage, deleted, moderatorNotice) VALUES (?, ?, ?, 0, ?, 0, 0, '', 0, 0, 0, '', 0, '')", (forumID, articleID, user.id, content))
            con.commit()
            return cls(cur.lastrowid)
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def getByUser(cls, user, deleted=False):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if not deleted:
                cur.execute("SELECT id FROM answers WHERE author=? AND deleted=0", (user.id,))
            else:
                cur.execute("SELECT id FROM answers WHERE author=?", (user.id,))
            data = list(map(lambda x: cls(x["id"]), cur.fetchall()))
            return data
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

class Article:

    FREEZONS = [
        u"Dieser Beitrag wurde eingefroren, **bis alle Streitigkeiten über den Inhalt beendet sind**.",
        u"Dieser Beitrag wurde eingefroren, da er eine **hohe Anzahl an Kommentaren** angezogen hat, die entfernt werden mussten.",
        u"Dieser Beitrag ist **kein gutes Beispiel für einen Beitrag in diesem Forum**, kann aber aufgrund seiner Verbreitung nicht entfernt werden. Daher wurden der Beitrag und seine Antworten *in der Zeit stehen gelassen* und kann nicht verändert werden.",
        u""
    ]

    CLOSURE_LABELS = {
        "off-topic": u"nicht in dieses Forum passend",
        "off-topic_glob": u"nicht in dieses Forum passend",
        "off-topic_course": u"nicht in dieses Forum passend",
        "unclear": u"unklar",
        "too-specific": u"zu spezifisch",
        "too-broad": u"zu allgemein"
    }

    OFF_TOPIC_REASONS = [
         ### --- global ---
        {
            "for_global": True,
            "for_course": False,
            "text": u"Dieser Beitrag enthält keine Frage zu &pi;-Learn im Rahmen der [*Informationen über das globale Forum*](/help/forum/global) und passt daher nicht in dieses globale Forum."
        },
        {
            "for_global": True,
            "for_course": False,
            "text": u"Dieser Beitrag enthält Fragen zu kursspezifischen Inhalten und gehört daher in das jeweilige [Kursforum](/help/forum/local)."
        }, ### --- course ---
        {
            "for_global": False,
            "for_course": True,
            "text": u"Dieser Beitrag enthält **keine Frage zum Kurs _<$>_** im Rahmen der [*Informationen über Kursforen*](/help/forum/local) und passt daher nicht in dieses Forum."
        },
        {
            "for_global": False,
            "for_course": True,
            "text": u"Dieser Beitrag enthält Fragen zu &pi;-Learn selber und gehört daher in das [globale Forum](/f/0)."
        }
    ]

    CLOSURE_TEXTS = {
        "duplicate": u"Andere Benutzer hatten dieses Problem auch und **fanden bereits eine Antwort**.\n\nWenn die folgenden Beiträge nicht helfen, dieses Problem zu lösen, *bearbeite* diesen Beitrag und beschreibe, WIESO diese Lösungsvorschläge dir nicht geholfen haben:",
        "off-topic": u"Dieser Beitrag passt nicht in dieses Forum.",
        "unclear": u"Wir verstehen die Frage-/Problemstellung des Autors nicht. Bitte bearbeite diesen Beitrag, um **alle wichtigen Informationen verständlich darzubieten**.\n\nHäufig hilft es, *konkrete Informationen*, wie das Problem *nachzuvollziehen* ist, hinzuzufügen.",
        "too-broad": u"Beiträge, **deren Lösung ein Buch füllen könnte** oder die **keine eindeutige Antwort** haben, sind für unser Format nicht geeignet.\n\nHäufig hilft es, die Fragestellung an ein **konkretes, praktisches Problem** anzuwenden.",
        "too-specific": u"Beiträge, die **nur die Lösung aber keinen Lösungsweg** für ein Problem anfordern, sind für unser Format nicht geeignet, da diese nur einer **sehr eingeschränkten Zielgruppe** helfen.\n\nHäufig hilft es, **das Problem zu abstrahieren** und nach dem *Wie* oder *Warum* anstatt nach dem *Wer*, *Was*, *Wann* oder *Wo* zu fragen."
    }

    PROTECTION_MESSAGE = {
        "wiki": u"**Dieser Beitrag und seine exzellenten Antworten sind gemeinschaftlich entstanden.**\n\nEs können keine weiteren Antworten hinzugefügt werden; siehst du etwas, das *verändert, aktualisiert oder ergänzt* werden muss, **bearbeite es**!",
        "answer": u"Antworten auf &pi;-Learn **müssen bestmöglich versuchen, das Problem zu lösen**. Um Rückfragen zu stellen, darf man nur Kommentare verwenden.\n\nUm diese Regel durchzusetzen, also *SPAM, &quot;Ich auch&quot; oder &quot;Danke&quot;-Antworten zu vermeiden*, benötigt man **mindestens 10 Reputationspunkte um diesen Beitrag zu beantworten**."
    }

    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def getDetail(self, d):
        return self.__data[d]

    def addRevision(self, title, content, tags, user, comment, review=-1):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO article_revisions (forumID, articleID, new_title, editor, new_content, new_tags, review_id, comment, type, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'edit', ?)", (self.getDetail("forumID"), self.id, title, user.id, content, tags, review, comment, time.time()))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def addRevComm(self, tp, user, comment):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO article_revisions (forumID, articleID, new_title, editor, new_content, new_tags, review_id, comment, type, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (self.getDetail("forumID"), self.id, self.getTitle(), user.id, self.getContent(), ("|".join(["["+i+"]" for i in self.getTags()])), -1, comment, tp, time.time()))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def hasRevision(self):
        return self.getRevisionCount() > 1

    def getRevisionCount(self, x=False):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if x:
                cur.execute("SELECT * FROM article_revisions WHERE forumID=? AND articleID=?", (self.getDetail("forumID"), self.id))
            else:
                cur.execute("SELECT * FROM article_revisions WHERE forumID=? AND articleID=? AND type='edit'", (self.getDetail("forumID"), self.id))
            return len(cur.fetchall())
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    def getRevision(self, id):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if id == "latest":
                cur.execute("SELECT * FROM article_revisions WHERE forumID=? AND articleID=? AND type='edit' ORDER BY id DESC", (self.getDetail("forumID"), self.id))
                data = cur.fetchone()
            else:
                cur.execute("SELECT * FROM article_revisions WHERE forumID=? AND articleID=? AND type='edit' ORDER BY id ASC", (self.getDetail("forumID"), self.id))
                data = cur.fetchall()[id-1]
                print(data["editor"])
            data = {
                "revid": (self.getRevisionCount() if id == "latest" else id),
                "id": data["id"],
                "type": data["type"],
                "editor": muser.User.safe(data["editor"]),
                "title": data["new_title"],
                "content": data["new_content"],
                "tags": data["new_tags"],
                "comment": data["comment"],
                "timestamp": data["timestamp"],
                "relative_time": ctimes.stamp2shortrelative(data["timestamp"]),
                "absolute_time": ctimes.stamp2german(data["timestamp"])
            }
            return data
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def getRevisionById(self, id):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM article_revisions WHERE forumID=? AND articleID=? AND id=?", (self.getDetail("forumID"), self.id, id))
            data = cur.fetchone()
            data = {
                "id": data["id"],
                "type": data["type"],
                "editor": muser.User.safe(data["editor"]),
                "title": data["new_title"],
                "content": data["new_content"],
                "tags": data["new_tags"],
                "comment": data["comment"],
                "timestamp": data["timestamp"],
                "relative_time": ctimes.stamp2shortrelative(data["timestamp"]),
                "absolute_time": ctimes.stamp2german(data["timestamp"])
            }
            return data
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def getAllRevisions(self):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM article_revisions WHERE forumID=? AND articleID=? ORDER BY id ASC", (self.getDetail("forumID"), self.id))
            i = 0
            rev = 1
            data_ = cur.fetchall()
            data = []
            for row in data_:
                r =self.getRevisionById(row["id"])
                if row["type"] == "edit":
                    r["revid"] = rev
                    rev += 1
                data.append(r)
            return data[::-1]
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def getCreationTime(self):
        t = self.getDetail("creation_date")
        return [t, ctimes.stamp2german(t), ctimes.stamp2shortrelative(t)]

    def getLastEditTime(self):
        t = self.getDetail("last_edit_date")
        return [t, ctimes.stamp2german(t), ctimes.stamp2shortrelative(t)]

    def getLastEditor(self):
        e = self.getDetail("last_editor")
        return muser.User.safe(e)

    def getComments(self, is_mod=False):
        return ForumComment.byPost("post", self.id, is_mod)

    def getCommentCounts(self, is_mod=False):
        return ForumComment.getCommentCounts("post", self.id)

    def getUserVote(self, u):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT direction FROM score_votes WHERE target_type='article' AND target_id=? AND user_id=?", (self.id, u.id))
            d = cur.fetchone()
            if d is None:
                return None
            return d[0]
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    def addVote(self, u, delta):
        v = self.getUserVote(u)
        if v is None:
            try:
                con = lite.connect('databases/forum.db')
                con.row_factory = lite.Row
                cur = con.cursor()
                cur.execute("INSERT INTO score_votes (user_id, direction, reputation, target_type, target_id, nullified) VALUES (?, ?, ?, 'article', ?, 0)", (u.id, delta, 3*delta, self.id))
                d = con.commit()
                self.setDetail("score", self.getInfo()["score"]+delta)
                au = self.getAuthor()
                if au.id != -1 and au.id != -3:
                    au.setReputationChange("forum_vote", "["+self.getHTMLTitle()+"](/f/"+str(self.getDetail("forumID"))+"/" + str(self.id) +")", 3*delta)
                    au.setDetail("reputation", au.getDetail("reputation")+3*delta)
                return delta, self.getInfo()["score"]
            except lite.Error as e:
                return False
            finally:
                if con:
                    con.close()
        else:
            if v == delta:
                try:
                    con = lite.connect('databases/forum.db')
                    con.row_factory = lite.Row
                    cur = con.cursor()
                    cur.execute("DELETE FROM score_votes WHERE user_id=? AND target_id=? AND target_type='article'", (u.id, self.id))
                    d = con.commit()
                    self.setDetail("score", self.getInfo()["score"]-delta)
                    au = self.getAuthor()
                    if au.id != -1 and au.id != -3:
                        au.setReputationChange("forum_vote", "["+self.getHTMLTitle()+"](/f/"+str(self.getDetail("forumID"))+"/" + str(self.id) +")", -3*delta)
                        au.setDetail("reputation", au.getDetail("reputation")+-3*delta)
                    return 0, self.getInfo()["score"]
                except lite.Error as e:
                    return False
                finally:
                    if con:
                        con.close()
            else:
                try:
                    con = lite.connect('databases/forum.db')
                    con.row_factory = lite.Row
                    cur = con.cursor()
                    cur.execute("UPDATE score_votes SET direction=?, reputation=? WHERE user_id=? AND target_id=? AND target_type='article'", (delta, 3*delta, u.id, self.id))
                    d = con.commit()
                    self.setDetail("score", self.getInfo()["score"]+2*delta)
                    au = self.getAuthor()
                    if au.id != -1 and au.id != -3:
                        au.setReputationChange("forum_vote", "["+self.getHTMLTitle()+"](/f/"+str(self.getDetail("forumID"))+"/" + str(self.id) +")", 6*delta)
                        au.setDetail("reputation", au.getDetail("reputation")+6*delta)
                    return delta, self.getInfo()["score"]
                except lite.Error as e:
                    return False
                finally:
                    if con:
                        con.close()



    def setDetail(self, d, v):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE articles SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def mayBeSeen(self, user):
        if self.isDeleted() and (user.may("general_autoMod") or user.isMod() or self.getAuthor().id == user.id):
            return True
        elif not self.isDeleted():
            return True
        else:
            return False

    def getHTMLTitle(self):
        title = ""
        if self.isDestroyed():
            title += u"<del>"
        title += self.getDetail("title")
        if self.isClosed():
            title += u" (geschlossen)"
        if self.isDestroyed():
            title += u"</del> (zerstört)"
        return title

    def hasAccepted(self):
        return self.getDetail("hasAcceptedAnswer")

    def getAccepted(self):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM answers WHERE forumID=? AND articleID=? AND isAcceptedAnswer=1", (self.getDetail("forumID"), self.id))
            data = cur.fetchone()
            if data is not None:
                return Answer(data[0])
            return None
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()

    def getScore(self):
        return self.getDetail("score")

    def getAward(self):
        return self.getDetail("awardRep")

    def isPinned(self):
        return self.getDetail("pinned")

    def isClosed(self):
        return self.getDetail("closed")

    def getClosureWarning(self, html=False):
        con = lite.connect('databases/forum.db')
        con.row_factory = lite.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM closure_flags WHERE state=1 AND type='vote' AND item_id=?", (self.id,))
        flags = cur.fetchall()
        majority_reason = self.getDetail("closureReason")
        cur.execute("SELECT * FROM closure_reasons WHERE id=?", (majority_reason,))
        majority_reason = cur.fetchone()
        voters = []
        reasons = []
        links = []
        for flag in flags:
            if flag[6] == 1 and majority_reason["id"] == 1:
                links.append(flag[7])
            elif flag[6] == 2 and majority_reason["id"] == 2:
                for r in reasons:
                    if r["text"] == flag[7]:
                        r["voters"].append(flag[4])
                        break
                else:
                    reasons.append({"text":flag[7], "voters":[flag[4]]})
            flagger = muser.User.safe(flag[4])
            voters.append(flagger)
        if html:
            response = ""
            flagger_html = ""
            index = 0
            for f in voters:
                if 0 < index < len(flagger)-1:
                    flagger_html += ", "
                elif index == len(flagger)-1 and index != 0:
                    flagger_html += " und "
                index += 1
                if f.isDeleted():
                    flagger_html += f.getHTMLName(False)
                else:
                    flagger_html += "<a href='/u/" + str(f.id) + "'>" + f.getHTMLName(False) + "</a>"

            if majority_reason["id"] == 1:
                response += "<h3 class=\"m0 f-sans fs-subheading\">als <strong>bereits gefragt und beantwortet</strong> markiert von " + flagger_html + "</h3>"
            else:
                response += "<h3 class=\"m0 f-sans fs-subheading\">als <strong>" + majority_reason["ui_name"] + "</strong> geschlossen von " + flagger_html + "</h3>"
            response += markdown.markdown(cplaceholder.parseForForum(majority_reason["description"], self.getForum()))
        else:
            response = {
                "reason_id": majority_reason["id"],
                "reason_label": majority_reason["ui_name"],
                "reason_text": cplaceholder.parseForForum(majority_reason["description"], self.getForum()),
                "voters": voters,
                "links": links,
                "subreasons": subreasons
            }

        return response
        text = "### "
        if majority_reason["id"] == 1:
            links_ = []
            for link in links:
                links_.append(u"["+Article(link).getTitle()+u"](/f/"+str(self.getDetail("forumID"))+u"/"+link+u")")
            links = u"- " + (u"\n- ".join(links_))
            text += u"Dieser Beitrag **hat bereits eine Antwort**:\n\n"+self.CLOSURE_TEXTS[majority_reason]+"\n\n"+links+"\n\n"
        elif majority_reason == "off-topic":
            rs_ = []
            for r in reasons:
                rs_.append("&quot;" + r["text"] + "&quot; <span class='name-list'>&ndash; " + (", ".join(list(map(lambda x:muser.User.safe(x).getHTMLName(), r["voters"])))) + "</span>")
            text += "Dieser Beitrag wurde als **"+self.CLOSURE_LABELS[majority_reason] +"** geschlossen\n\n- " + ("\n- ".join(rs_)) + "\n\n"
        else:
            text += "Dieser Beitrag wurde als **"+self.CLOSURE_LABELS[majority_reason] +"** geschlossen\n\n"+self.CLOSURE_TEXTS[majority_reason]+"\n\n"
        text += "<span class='name-list'>&mdash; " + voters + "</span>"
        text = text.replace("<$>", Forum(self.getDetail("forumID")).getTitle())
        #print(text)
        return text

    def isFrozen(self):
        return self.getDetail("frozen")

    def isLocked(self):
        return self.isFrozen() and self.getDetail("frozenAsLock")

    def getFrozenBy(self):
        fb = self.getDetail("frozenBy")
        if fb == 0:
            fb = -3
        return muser.User.safe(fb)

    def getFrozenMessage(self):
        return self.getDetail("frozenMessage")

    def getLabel(self):
        label = self.getTitle()
        label = label.replace(u"π", "pi")
        label = re.sub("[^a-zA-Z0-9- ]+", "", label)
        label = re.sub("[ ]+", "-", label)
        label = label.lower()[:50].strip("-")
        return label

    def getScore(self):
        return self.getDetail("score")

    def getTitle(self):
        return self.getDetail("title")

    def getTeaser(self):
        return self.getDetail("content")[:100] + ("" if len(self.getDetail("content")) < 100 else "...")

    def getContent(self):
        return self.getDetail("content")

    def getModNotice(self):
        notice = self.getDetail("moderatorNotice")
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM post_notices WHERE id=?", (notice, ))
            n = cur.fetchone()
            if n:
                return n["body"]
            return notice
        except lite.Error as e:
            return notice
        finally:
            if con:
                con.close()

    def getAuthor(self):
        return muser.User.safe(self.getDetail("author"))

    def getTags(self):
        tags = self.getDetail("tags")
        if tags == "":
            return []
        tags = tags.split("|")
        return [t[1:-1] for t in tags]

    def getTagObjects(self):
        for t in self.getTags():
            tagged = mtags.ForumTag.byName(t)
            if not tagged:
                tagged = mtags.ForumTag.byName(t, self.getDetail("forumID"))
            if not tagged:
                continue
            yield tagged

    def isDeleted(self):
        return self.getDetail("deleted") == 1 or self.isDestroyed()

    def isProtected(self):
        return self.getDetail("protected") != 0

    def isNewbieProtection(self):
        return self.getDetail("protected") == 1

    def isWikiProtection(self):
        return self.getDetail("protected") == 2

    def getProtectedBy(self):
        return muser.User.safe(self.getDetail("protectionBy"))

    def getAnswers(self):
        try:
            con = lite.connect('databases/forum.db')
            cur = con.cursor()
            cur.execute("SELECT id FROM answers WHERE forumID=? AND articleID=? ORDER BY isAcceptedAnswer DESC, deleted ASC, score DESC, RANDOM()", (self.getDetail("forumID"), self.id))
            data = cur.fetchall()
            return list(map(lambda x:Answer(x[0]), data))
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def getAnswerCount(self):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT COUNT(id) FROM answers WHERE forumID=? AND articleID=? AND deleted=0", (self.getDetail("forumID"), self.id))
            data = cur.fetchone()
            return data[0] if data is not None else 0
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    def getForum(self):
        return Forum(self.getDetail("forumID"))

    def getDeleteMessage(self):
        del_reason = self.getDetail("deletionReason")
        if del_reason == "owner":
            return u"<h3 class=\"m0 f-sans fs-subheading\"><strong>gelöscht</strong> von seinem Urheber</h3>"
        elif del_reason == "spam":
            return u"<h3 class=\"m0 f-sans fs-subheading\"><strong>gelöscht</strong> als Werbung/beleidigender/missbräuchlicher Inhalt</h3>"
        elif del_reason == "offensive":
            return u"<h3 class=\"m0 f-sans fs-subheading\"><strong>gelöscht</strong> als Werbung/beleidigender/missbräuchlicher Inhalt</h3>"
        elif del_reason == "dangerous":
            return u"<h3 class=\"m0 f-sans fs-subheading\"><strong>gelöscht</strong> als Werbung/beleidigender/missbräuchlicher Inhalt</h3>"
        elif del_reason == "queue":
            return u"<h3 class=\"m0 f-sans fs-subheading\"><strong>gelöscht</strong> aufgrund des Votums in einer Moderationsliste</h3>"
        elif del_reason == "auto:closed":
            return u"<h3 class=\"m0 f-sans fs-subheading\">automatisch <strong>gelöscht</strong> wegen Inaktivität (DeleteInactiveClosed)</h3>"
        elif del_reason == "vote":
            try:
                con = lite.connect('databases/forum.db')
                con.row_factory = lite.Row
                cur = con.cursor()
                cur.execute("SELECT * FROM deletion_votes WHERE postId=? AND postType='post' AND active=1 ORDER BY voteCastDate", (self.id, ))
                con.commit()
                flags = cur.fetchall()
                voters = ""
                voter_html = ""
                index = 0
                maxtime = 0
                for flag in flags:
                    if flag[3] > maxtime: maxtime = flag[3]
                    flagger = muser.User.safe(flag[2])
                    if 0 < index < len(flags)-1:
                        voter_html += ", "
                    elif index == len(flags)-1 and index != 0:
                        voter_html += " und "
                    index += 1
                    if flagger.isDeleted():
                        voter_html += flagger.getHTMLName(False)
                    else:
                        voter_html += "<a href='/u/" + str(flagger.id) + "'>" + flagger.getHTMLName(False) + "</a>"

                return u"<h3 class=\"m0 f-sans fs-subheading\"><strong>gelöscht</strong> von " + voter_html + " " + ctimes.stamp2shortrelative(maxtime) + "</h3>"
            except lite.Error as e:
                return u"<h3 class=\"m0 f-sans fs-subheading\"><strong>gelöscht</strong></h3>"
            finally:
                if con:
                    con.close()
        else:
            return u"<h3 class=\"m0 f-sans fs-subheading\"><strong>gelöscht</strong></h3>"

    def isDestroyed(self):
        return self.getDetail("deleted") == 2

    def getInfo(self):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM articles WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                raise ValueError("Article not found with id " + str(self.id))
            return {
                "id": data['id'],
                "forumID": data['forumID'],
                "title": data['title'],
                "title": data['title'],
                "author": data['author'],
                "score": data['score'],
                "content": data['content'],
                "tags": data['tags'],
                "awardRep": data['awardRep'],
                "awardBy": data['awardBy'],
                "awardMessage": data['awardMessage'],
                "hasAcceptedAnswer": data['hasAcceptedAnswer'],
                "pinned": bool(data['pinned']),

                "frozen": bool(data['frozen']),
                "frozenBy": data['frozenBy'],
                "frozenMessage": data['frozenMessage'],
                "frozenAsLock": bool(data['frozenAsLock']),

                "closed": bool(data['closed']),
                "closureReason": data['closureReason'],
                "deleted": data['deleted'],
                "deletionReason": data['deletionReason'],

                "protected": data["protected"],
                "protectionBy": data["protectionBy"],

                "moderatorNotice": data['moderatorNotice'],

                "creation_date": data['creation_date'],
                "last_edit_date": data['last_edit_date'],
                "last_activity_date": data['last_edit_date'],
                "last_editor": data['last_editor']
            }
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()


    def close(self, msg, who, in_review_final=False):
        try:
          con = lite.connect('databases/forum.db')
          con.row_factory = lite.Row
          cur = con.cursor()
          qid = None
          cur.execute("SELECT * FROM closure_queue WHERE item_id=? AND state=0", (self.id,))
          qid = cur.fetchone()
          if qid is None:
              cur.execute("INSERT INTO closure_queue (item_id, state, result) VALUES (?, 0, 0)", (self.id,))
              qid = cur.lastrowid
          else:
              qid = qid["id"]
          cur.execute("INSERT INTO closure_flags (item_id, queue_id, state, flagger_id, type, reason, comment) VALUES (?, ?, 0, ?, ?, ?, ?)", (self.id, qid, who.id, "vote", msg["reason"], msg["message"]))
          con.commit()
          tps = {
                  "off-topic": u"nicht in dieses Forum passend",
                  "unclear": u"unklar",
                  "too-specific": u"zu spezifisch",
                  "too-broad": u"zu allgemein"
              }
          cur.execute("SELECT * FROM closure_flags WHERE item_id=? AND type='vote' AND state=0", (self.id, ))
          con.commit()
          flags = cur.fetchall()
          num = len(flags)
          if num == 3 or who.isMod() or in_review_final:
              cur.execute("UPDATE closure_flags SET state=1 WHERE (reason!='custom' OR type='vote') AND item_id=? AND state=0", (self.id,))
              cur.execute("UPDATE closure_queue SET state=2, result=6 WHERE item_id=? AND state=0", (self.id, ))
              con.commit()
              reasons = []
              majority_reason = ""
              comtext = ""
              for flag in flags:
                  flagger = muser.User.from_id(flag[4])
                  reasons.append(flag[6])
                  if flagger.isMod():
                      majority_reason = flag[6]
              if majority_reason == "":
                  for reason in reasons:
                      if reasons.count(reason) == 2:
                          majority_reason = reason
                          break
                  if majority_reason == "":
                      majority_reason = reasons[0]
              self.setDetail("closed", 1)
              self.setDetail("closureReason", majority_reason)
              self.__data = self.getInfo()
              self.addRevComm("closure", muser.User.from_id(-1), self.getClosureWarning())
              revcount = self.getRevisionCount()
              maxClosureThreshold = 2+int(revcount/2)
              cur.execute("SELECT * FROM article_revisions WHERE articleID=? AND type='closure'", (self.id,))
              closureEventCount = len(cur.fetchall())
              print(closureEventCount)
              if closureEventCount >= maxClosureThreshold:
                  self.customflag(u"**[automatisch]**: *Umstrittene Schließung* - Dieser Beitrag wurde mehrfach geschlossen und wieder geöffnet.", muser.User.from_id(-2))
          return True
        except SyntaxError as e:#lite.Error as e:
          print(e)
          return False
        finally:
          if con:
              con.close()

    def closeflag(self, msg, who):
        try:
          con = lite.connect('databases/forum.db')
          con.row_factory = lite.Row
          cur = con.cursor()
          qid = None
          cur.execute("SELECT * FROM closure_queue WHERE item_id=? AND state=0", (self.id,))
          qid = cur.fetchone()
          if qid is None:
              cur.execute("INSERT INTO closure_queue (item_id, state, result) VALUES (?, 0, 0)", (self.id,))
              qid = cur.lastrowid
          else:
              qid = qid["id"]
          cur.execute("INSERT INTO closure_flags (item_id, queue_id, state, flagger_id, type, reason, comment) VALUES (?, ?, 0, ?, ?, ?, ?)", (self.id, qid, who.id, "flag", msg["reason"], msg["message"]))
          con.commit()
          return True
        except lite.Error as e:
          print(e)
          return False
        finally:
          if con:
              con.close()

    def delvote(self, who, in_review_final=False):
        try:
          con = lite.connect('databases/forum.db')
          con.row_factory = lite.Row
          cur = con.cursor()
          cur.execute("INSERT INTO deletion_votes (postType, postId, voteOwner, voteCastDate, active) VALUES ('post', ?, ?, ?, 1)", (self.id, who.id, time.time()))
          con.commit()
          cur.execute("SELECT * FROM deletion_votes WHERE postType='post' AND postId=? AND active=1", (self.id, ))
          con.commit()
          all = cur.fetchall()
          num = len(all)
          if num == 3 + min(5,int(self.getScore()/5)) or who.isMod():
              self.setDetail("deleted", 1)
              self.setDetail("deletionReason", "vote")
              self.__data = self.getInfo()
              voter_html = ""
              index = 0
              for flag in all:
               flagger = muser.User.safe(flag[2])
               if 0 < index < len(all)-1:
                   voter_html += ", "
               elif index == len(all)-1 and index != 0:
                   voter_html += " und "
               index += 1
               voter_html += "<a href='/u/" + str(flagger.id) + "'>" + flagger.getHTMLName(False) + "</a>"

              self.addRevComm("deleted", muser.User.from_id(-1), voter_html)
          return True
        except lite.Error as e:
          print(e)
          return False
        finally:
          if con:
              con.close()

    def getDelVotes(self):
        try:
          con = lite.connect('databases/forum.db')
          con.row_factory = lite.Row
          cur = con.cursor()
          cur.execute("SELECT Count(*) FROM deletion_votes WHERE postType='post' AND postId=? AND active=1", (self.id, ))
          con.commit()
          return cur.fetchone()[0]
        except lite.Error as e:
          return 0
        finally:
          if con:
              con.close()

    def undelvote(self, who, in_review_final=False):
          try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            qid = None
            cur.execute("INSERT INTO undeletion_votes (postType, postId, voteOwner, voteCastDate, active) VALUES ('post', ?, ?, ?, 1)", (self.id, who.id, time.time()))
            con.commit()
            cur.execute("SELECT * FROM undeletion_votes WHERE postType='post' AND postId=? AND active=1", (self.id, ))
            con.commit()
            all = cur.fetchall()
            num = len(all)
            if num == 3 + min(5,int(self.getScore()/5)) or who.isMod():
                cur.execute("UPDATE deletion_votes SET active=0 WHERE postType='post' AND postId=? AND active=1", (self.id,))
                cur.execute("UPDATE undeletion_votes SET active=0 WHERE postType='post' AND postId=? AND active=1", (self.id,))
                con.commit()
                self.setDetail("deleted", 0)

                voter_html = ""
                index = 0
                for flag in all:
                    flagger = muser.User.safe(flag[2])
                    if 0 < index < len(all)-1:
                        voter_html += ", "
                    elif index == len(all)-1 and index != 0:
                        voter_html += " und "
                    index += 1
                    voter_html += "<a href='/u/" + str(flagger.id) + "'>" + flagger.getHTMLName(False) + "</a>"

                self.addRevComm("undeleted", muser.User.from_id(-1), voter_html)
            return True
          except lite.Error as e:
            print(e)
            return False
          finally:
            if con:
                con.close()

    def getUndelVotes(self):
        try:
          con = lite.connect('databases/forum.db')
          con.row_factory = lite.Row
          cur = con.cursor()
          cur.execute("SELECT Count(*) FROM undeletion_votes WHERE postType='post' AND postId=? AND active=1", (self.id, ))
          con.commit()
          return cur.fetchone()[0]
        except lite.Error as e:
          return 0
        finally:
          if con:
              con.close()

    def customflag(self, msg, who):
        try:
          con = lite.connect('databases/user.db')
          con.row_factory = lite.Row
          cur = con.cursor()
          qid = None
          cur.execute("SELECT * FROM custom_flaglist WHERE item_id=? AND item_type='forum.question' AND state=0", (self.id,))
          qid = cur.fetchone()
          if qid is None:
              cur.execute("INSERT INTO custom_flaglist (item_id, item_type, state) VALUES (?, 'forum.question', 0)", (self.id,))
              qid = cur.lastrowid
          else:
              qid = qid["id"]
          cur.execute("INSERT INTO custom_flag (item_id, item_type, queue_id, state, flagger_id, comment) VALUES (?, 'forum.question', ?, 0, ?, ?)", (self.id, qid, who.id, msg))
          con.commit()
          return True
        except SyntaxError as e:#lite.Error as e:
          print(e)
          return False
        finally:
          if con:
              con.close()

    def reopen(self, who, in_review_final=False):
          try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            qid = None
            cur.execute("SELECT * FROM reopen_queue WHERE item_id=? AND state=0", (self.id,))
            qid = cur.fetchone()
            if qid is None:
                cur.execute("INSERT INTO reopen_queue (item_id, state, result) VALUES (?, 0, 0)", (self.id,))
                qid = cur.lastrowid
            else:
                qid = qid["id"]
            cur.execute("INSERT INTO reopen_flags (item_id, queue_id, state, flagger_id, type, reason, comment) VALUES (?, ?, 0, ?, ?, ?, ?)", (self.id, qid, who.id, "vote", "voted", ""))
            con.commit()
            cur.execute("SELECT * FROM reopen_flags WHERE item_id=? AND type='vote' AND state=0", (self.id, ))
            con.commit()
            all = cur.fetchall()
            num = len(all)
            if num == 3 or who.isMod() or in_review_final:
                cur.execute("UPDATE reopen_flags SET state=1 WHERE item_id=? AND state=0", (self.id,))
                cur.execute("UPDATE closure_flags SET state=2 WHERE item_id=? AND state=1", (self.id,))
                cur.execute("UPDATE reopen_queue SET state=2, result=6 WHERE item_id=? AND state=0", (self.id, ))
                con.commit()
                self.setDetail("closed", 0)
                voters = ""
                for flag in all:
                    if flag["type"] != "vote":
                        continue
                    flagger = muser.User.safe(flag["flagger_id"])
                    voters += ", ["+flagger.getHTMLName()+"](/u/"+str(flagger.id)+")"
                self.addRevComm("reopened", muser.User.from_id(-1), voters[2:])
            return True
          except lite.Error as e:
            print(e)
            return False
          finally:
            if con:
                con.close()

    @classmethod
    def exists(cls, forum_id, id=None):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if id is not None:
                cur.execute("SELECT * FROM articles WHERE id=? AND forumID=?", (id,forum_id))
            else:
                cur.execute("SELECT * FROM articles WHERE id=?", (forum_id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def createNew(cls, forumID, title, content, tags, user):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO articles (forumID, title, author, score, content, tags, awardRep, awardBy, awardMessage, awardStarted, awardEnded, hasAcceptedAnswer, pinned, frozen, frozenBy, frozenMessage, frozenAsLock, closed, closureReason, deleted, deletionReason, protected, protectionBy, moderatorNotice) VALUES (?, ?, ?, 0, ?, ?, 0, 0, '', 0, 0, 0, 0, 0, 0, '', 0, 0, '', 0, '', 0, 0, '')", (forumID, title, user.id, content, tags))
            con.commit()
            return cls(cur.lastrowid)
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def getAll(cls, deleted=True):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if not deleted:
                cur.execute("SELECT id FROM articles WHERE deleted=0")
            else:
                cur.execute("SELECT id FROM articles")
            data = list(map(lambda x: cls(x["id"]), cur.fetchall()))
            return data
        except lite.Error as e:
            print(e)
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def getByUser(cls, user, deleted=False):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if not deleted:
                cur.execute("SELECT id FROM articles WHERE author=? AND deleted=0", (user.id,))
            else:
                cur.execute("SELECT id FROM articles WHERE author=?", (user.id,))
            data = list(map(lambda x: cls(x["id"]), cur.fetchall()))
            return data
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

class Forum:

    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def getDetail(self, d):
        return self.__data[d]

    def getCourse(self):
        if self.id != 0:
            return mcourses.Courses(self.id)

    def getTitle(self):
        return self.getDetail("name")

    def getLabel(self):
        return self.getDetail("label")

    def getByLine(self):
        return self.getDetail("byline")

    def getTopic(self):
        if self.id == 0:
            return None

        return mcourses.Courses(self.id).getTopic()

    def getArticles(self, q=False, sort=False, tagged=None):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()

            sort_sql = "ORDER BY deleted ASC, last_activity_date DESC, creation_date DESC, id DESC"
            if sort == "latest":
                sort_sql = "ORDER BY deleted ASC, creation_date DESC, id DESC"
            elif sort == "score":
                sort_sql = "ORDER BY deleted ASC, score DESC, id DESC"

            if tagged:
                if q:
                    q = "%"+q+"%"
                    cur.execute("SELECT articles.id FROM articles, forum_tag_associations WHERE articles.id=forum_tag_associations.post_id AND forum_tag_associations.tag_id=? AND forumID=? AND (content LIKE ? OR title LIKE ?) " + sort_sql, (tagged.id, self.id, q, q))
                else:
                    cur.execute("SELECT articles.id FROM articles, forum_tag_associations WHERE articles.id=forum_tag_associations.post_id AND forum_tag_associations.tag_id=? AND forumID=? " + sort_sql, (tagged.id,self.id))
            else:
                if q:
                    q = "%"+q+"%"
                    cur.execute("SELECT id FROM articles WHERE forumID=? AND (content LIKE ? OR title LIKE ?) " + sort_sql, (self.id, q, q))
                else:
                    cur.execute("SELECT id FROM articles WHERE forumID=? " + sort_sql, (self.id, ))
            data = cur.fetchall()
            return list(map(lambda x:Article(x[0]), data))
        except lite.Error as e:
            print e
            return []
        finally:
            if con:
                con.close()

    def getAnnouncements(self, user, ignore_featured=False):
        try:
            con = lite.connect('databases/courses.db')
            cur = con.cursor()
            cur.execute("SELECT courseid FROM enrollments WHERE userid=?", (user.id, ))
            dl = cur.fetchall()
        except lite.Error as e:
            print(e)
            return []
        finally:
            if con:
                con.close()

        announcements = ForumAnnouncement.byForum(0, ignore_featured=ignore_featured)
        for d in dl:
            announcements += ForumAnnouncement.byForum(d[0], ignore_featured=ignore_featured)

        return announcements

    def getClosureReasons(self, level=None):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()

            cur.execute("SELECT * FROM closure_reasons WHERE active=1 AND parent IS ?", (level, ))
            data = cur.fetchall()
            data = map(lambda x:dict(x), data)
            final_data = []
            for d in data:
                if d["not_in_global_forum"]==1 and self.id == 0:
                    continue
                elif d["not_in_course_forum"]==1 and self.id != 0:
                    continue
                d["description"] = cplaceholder.parseForForum(d["description"], self)
                final_data.append(d)
            return final_data
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def getInfo(self):
        if self.id != 0:
            c = mcourses.Courses(self.id)
            return {
                "id": self.id,
                "name": c.getTitle(),
                "label": c.getLabel(),
                "byline": c.getByLine()
            }
        else:
            return {
                "id": self.id,
                "label":"global",
                "name": "globales Forum",
                "byline": u"für alle Fragen zu π-Learn selber und für Fehlermeldungen oder Verbesserungsideen"
            }

    @classmethod
    def global_(cls):
        return cls(0)

    @classmethod
    def from_id(cls, id):
        return cls(id)

    @classmethod
    def exists(cls, id):
        if id == 0:
            return True
        try:
            con = lite.connect('databases/courses.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM courses WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()









class ForumComment:

    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def getDetail(self, d):
        return self.__data[d]

    def setDetail(self, d, v):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE forum_comments SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getScore(self):
        return self.getDetail("comment_score")

    def getContent(self):
        return self.getDetail("content")

    def getCreationTime(self):
        t = self.getDetail("creation_time")
        return [t, ctimes.stamp2german(t), ctimes.stamp2shortrelative(t)]

    def getAuthor(self):
        return muser.User.safe(self.getDetail("comment_author"))

    def isDeleted(self):
        return self.getDetail("deleted") == 1

    def getDeletedBy(self):
        return muser.User.safe(self.getDetail("deletedby"))

    def hasVote(self, user, type=None, validated_only=True):
        try:
            con = lite.connect('databases/forum.db')
            cur = con.cursor()
            if not type:
                if validated_only:
                    cur.execute("SELECT Count(*) FROM comment_action WHERE comment_id=? AND user_id=?", (self.id, user))
                else:
                    cur.execute("SELECT Count(*) FROM comment_action WHERE comment_id=? AND user_id=? AND validated = 1", (self.id, user))
            else:
                if validated_only:
                    cur.execute("SELECT Count(*) FROM comment_action WHERE comment_id=? AND user_id=? AND action=?", (self.id, user, type))
                else:
                    cur.execute("SELECT Count(*) FROM comment_action WHERE comment_id=? AND user_id=? AND validated = 1 AND action=?", (self.id, user, type))

            data = cur.fetchone()
            return data[0] != 0
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def addVote(self, user, type, comment=None):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO comment_action (comment_id, user_id, action, comment, validated) VALUES (?, ?, ?, ?, 0)", (self.id, user, type, comment))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getInfo(self):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM forum_comments WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                raise ValueError("ForumComment not found with id " + str(self.id))
            return {
                "id": data['id'],
                "post_type": data['post_type'],
                "post_id": data['post_id'],
                "post_forum": data['post_forum'],
                "comment_score": data['comment_score'],
                "comment_author": data['comment_author'],
                "deleted": data['deleted'],
                "deletedby": data['deletedby'],
                "annoyingness": data['annoyingness'],
                "creation_time": data['creation_time'],
                "content": data['content']
            }
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    @classmethod
    def byPost(cls, post_type, post_id, is_mod):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if is_mod:
                cur.execute("SELECT * FROM forum_comments WHERE post_type=? AND post_id=?", (post_type, post_id))
            else:
                cur.execute("SELECT * FROM forum_comments WHERE post_type=? AND post_id=? AND deleted=0", (post_type, post_id))
            data = cur.fetchall()
            return [cls(_["id"]) for _ in data]
        except lite.Error as e:
            print(e)
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def createNew(cls, post_type, post_id, post_forum, author, content):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO forum_comments (post_type, post_id, post_forum, comment_score, comment_author, deleted, deletedby, annoyingness, creation_time, content) VALUES (?, ?, ?, 0, ?, 0, 0, 0, ?, ?)", (post_type, post_id, post_forum, author, time.time(), content))
            con.commit()
            return cls(cur.lastrowid)
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    @staticmethod
    def getCommentCounts(post_type, post_id):
        try:
            con = lite.connect('databases/forum.db')
            cur = con.cursor()
            cur.execute("SELECT COUNT(*), SUM(deleted), COUNT(*)-SUM(deleted) FROM forum_comments WHERE post_type=? AND post_id=?", (post_type, post_id))
            data = cur.fetchone()
            return int(data[0] if data[0] else "0"),int(data[1] if data[1] else "0"),int(data[2] if data[2] else "0")
        except lite.Error as e:
            print(e)
            return [0,0,0]
        finally:
            if con:
                con.close()



class ForumAnnouncement:

    def __init__(self, id):
        self.id = id
        self.__data = self.getInfo()

    def getDetail(self, d):
        return self.__data[d]

    def setDetail(self, d, v):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE announcements SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getShownFrom(self):
        t = self.getDetail("show_from")
        return [t, ctimes.stamp2germandate(t), ctimes.stamp2shortrelative(t)]

    def getShownFromForForm(self):
        t = self.getDetail("show_from")
        return ctimes.dateforform(t)

    def getShownUntil(self):
        t = self.getDetail("show_until")
        return [t, ctimes.stamp2germandate(t), ctimes.stamp2shortrelative(t)]

    def getShownUntilForForm(self):
        t = self.getDetail("show_until")
        return ctimes.dateforform(t)

    def getStart(self):
        t = self.getDetail("start_date")
        return [t, ctimes.stamp2germandate(t), ctimes.stamp2shortrelative(t)]

    def getStartDateForForm(self):
        t = self.getDetail("start_date")
        return ctimes.dateforform(t)

    def getEnd(self):
        t = self.getDetail("end_date")
        if not t: return None
        return [t, ctimes.stamp2germandate(t), ctimes.stamp2shortrelative(t)]

    def getEndDateForForm(self):
        t = self.getDetail("end_date")
        if not t: return None
        return ctimes.dateforform(t)

    def getForum(self):
        return Forum(self.getDetail("forum"))

    def isShown(self):
        return self.getDetail("show_from") < time.time() < self.getDetail("show_until")

    def getTitle(self):
        return self.getDetail("title")

    def getLink(self):
        return self.getDetail("link")

    def isFeaturedBanner(self):
        return self.getDetail("is_featured_banner")

    def getInfo(self):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM announcements WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                raise ValueError("ForumAnnouncement not found with id " + str(self.id))
            return {
                "id": data['id'],
                "forum": data['forum'],
                "link": data['link'],
                "title": data['title'],
                "start_date": data['start_date'],
                "end_date": data['end_date'],
                "show_from": data['show_from'],
                "show_until": data['show_until'],
                "is_featured_banner": data["is_featured_banner"]
            }
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()

    @classmethod
    def byForum(cls, forum_id, all=False, ignore_featured=False):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if ignore_featured:
                if not all:
                    cur.execute("SELECT * FROM announcements WHERE forum=? AND show_from < ? and show_until > ? AND is_featured_banner IS NOT 1", (forum_id, time.time(), time.time()))
                else:
                    cur.execute("SELECT * FROM announcements WHERE forum=? AND is_featured_banner IS NOT 1", (forum_id,))
            else:
                if not all:
                    cur.execute("SELECT * FROM announcements WHERE forum=? AND show_from < ? and show_until > ?", (forum_id, time.time(), time.time()))
                else:
                    cur.execute("SELECT * FROM announcements WHERE forum=?", (forum_id,))

            data = cur.fetchall()
            return [cls(_["id"]) for _ in data]
        except lite.Error as e:
            print(e)
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def byForumFeatured(cls, forum_id):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM announcements WHERE forum=? AND show_from < ? and show_until > ? AND is_featured_banner=1", (forum_id, time.time(), time.time()))
            data = cur.fetchall()
            return [cls(_["id"]) for _ in data]
        except lite.Error as e:
            print(e)
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def createNew(cls, forumID, title, link, show_from, show_until, start_date, end_date=None):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO announcements (forum, link, title, show_from, show_until, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?, ?)", (forumID, link, title, show_from, show_until, start_date, end_date))
            con.commit()
            return cls(cur.lastrowid)
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def exists(cls, id):
        try:
            con = lite.connect('databases/forum.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM announcements WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()
