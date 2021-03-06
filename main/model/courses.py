# coding: utf-8
import os, json, re
import secrets, random
import sqlite3 as lite
from flask import request, session, url_for
from sha1 import sha1
from model import privileges as mprivileges, user as muser

from flask_babel import _

class Courses:

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
            cur.execute("UPDATE courses SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getHash(self):
        return sha1("[id:" + str(self.id) + ",name:" + self.getTitle()+"]")[:15]

    def getPattern(self, use_large=False):
        course_hash = self.getHash()
        pattern = "background-image: "

        picture_url = self.getDetail("picture_url")
        if picture_url:
            pattern = pattern[:-1]
            if use_large:
                pattern += "url(" + request.url_root + "static/CourseStockImages/" + picture_url + "?novalidate=" + str(random.randint(0,10000)) + "), "
            else:
                pattern += "url(" + request.url_root + "static/CourseStockImages_small/" + picture_url + "?novalidate=" + str(random.randint(0,10000)) + "), "

        pattern +="linear-gradient("

        is_letter=(lambda x: x.lower() in "abcdefghijklmnopqrstuvxyz")
        get_direction=(lambda x: sum(map(ord, x)) % 360)

        if is_letter(course_hash[0]):
            pattern += str(get_direction(course_hash[:4])) + "deg, #" + course_hash[8:14] + ", #" +  course_hash[1:7]
        else:
            pattern += str(get_direction(course_hash[-4:])) + "deg, #" + course_hash[1:7] + ", #" +  course_hash[8:14]

        pattern += "); background-size: 100% auto;"

        return pattern

    def getForum(self):
        from . import forum as mforum
        return mforum.Forum(self.id)

    def getActivePRCount(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT Count(*) FROM pull_requests WHERE decision=0 AND course_id=? AND hide_as_spam=0", (self.id,))
            return cur.fetchone()[0]
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    @classmethod
    def getCourseList(cls):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM courses WHERE state=1 ORDER BY id * RANDOM() DESC")
            all = cur.fetchall()
            if all is None:
                return []
            all = list([Courses(x["id"]) for x in all])
            return all
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def getRandomBeloved(cls, uid):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM courses WHERE topicid IN (SELECT topics.id FROM topics, courses, enrollments WHERE courses.topicid=topics.id AND enrollments.courseid=courses.id AND enrollments.userid=? GROUP BY topics.id HAVING Count(*) >= 2) AND state=1 AND manual_enrollment IS NOT 1 ORDER BY Random() LIMIT 3", (uid,))
            all = cur.fetchall()
            if all is None:
                return []
            all = list([Courses(x["id"]) for x in all])
            return all
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def getGlobalBeloved(cls):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM (SELECT courses.id FROM courses, enrollments WHERE  courses.state=1 AND courses.manual_enrollment IS NOT 1 AND courses.id=enrollments.courseid GROUP BY courses.id HAVING Count(*)>=3 ORDER BY Count(*) DESC LIMIT 10) AS c ORDER BY Random() LIMIT 3")
            all = cur.fetchall()
            if all is None:
                return []
            all = list([Courses(x["id"]) for x in all])
            return all
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def queryNum(cls, q, add):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT COUNT(id) FROM courses WHERE " + q, add)
            return cur.fetchone()[0]
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    @classmethod
    def query(cls, q, add, from_, to):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM courses WHERE " + q + " LIMIT " + str(from_) + ", " + str(to), add)
            all = cur.fetchall()
            if all is None:
                return []
            all = list([Courses(x["id"]) for x in all])
            return all
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def getFromUser(cls, u):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM courses WHERE id IN (SELECT courseid FROM enrollments WHERE userid=?)", (u.id,))
            all = cur.fetchall()
            if all is None:
                return []
            all = list([Courses(x["id"]) for x in all])
            return all
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def getByUser(cls, u, toponly=False):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if not toponly:
                cur.execute("SELECT id FROM courses WHERE id IN (SELECT courseid FROM enrollments WHERE userid=? AND permission>=3)", (u.id,))
            else:
                cur.execute("SELECT courses.id FROM enrollments As enr, courses, enrollments As own WHERE enr.courseid=courses.id AND own.courseid=courses.id AND own.permission=4 AND own.userid=? GROUP BY courses.id HAVING Count(*) >= 3 ORDER BY Count(*) DESC LIMIT 3", (u.id,))
            all = cur.fetchall()
            if all is None:
                return []
            all = list([Courses(x["id"]) for x in all])
            return all
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def getTitle(self):
        return self.getDetail("title")

    def getShortdesc(self):
        return self.getDetail("shortdesc")

    def getByLine(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM enrollments WHERE courseid=? AND permission > 2 ORDER BY permission DESC, id ASC", (self.id,))
            data = cur.fetchall()
            val = ""
            i = 0
            for d in data:
                du = muser.User.from_id(d["userid"])
                if i == len(data) - 1 and i !=0:
                    val += " " + _("und") + " ["+du.getDetail("realname")+"](/u/"+str(du.id)+")"
                else:
                    val += ", ["+du.getDetail("realname")+"](/u/"+str(du.id)+")"
                i += 1
            val = _("von") + " " + val[2:]
            return val
        except lite.Error as e:
            return ""
        finally:
            if con:
                con.close()
        #return self.getDetail("byline")

    def getLongdesc(self):
        return self.getDetail("longdesc")

    def getRequirements(self):
        return self.getDetail("requirements")

    def getTopic(self):
        return Topic(self.getDetail("topicid"))

    def getLabel(self):
        label = self.getTitle()
        label = label.replace("π", "pi")
        label = re.sub("[^a-zA-Z0-9- ]+", "", label)
        label = re.sub("[ ]+", "-", label)
        label = label.lower()[:50].strip("-")
        return label

    def enroll(self, u):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO enrollments (courseid, userid, lastunitid, permission) VALUES (?, ?, 0, 1)", (self.id, u.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def unenroll(self, u):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("DELETE FROM enrollments WHERE courseid=? AND userid=?", (self.id, u.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def isEnrolled(self, u):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT courseid FROM enrollments WHERE courseid=? AND userid=? AND permission >= 1", (self.id, u.id))
            return cur.fetchone() is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getEnrolledCount(self):
        try:
            con = lite.connect('databases/pilearn.db')
            cur = con.cursor()
            cur.execute("SELECT COUNT(id) FROM enrollments WHERE courseid=?", (self.id,))
            return cur.fetchone()[0]
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    def getLastVisitedUnitId(self, u):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT lastunitid FROM enrollments WHERE courseid=? AND userid=?", (self.id, u.id))
            d = cur.fetchone()
            return d["lastunitid"] if d else 0
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()

    def setLastVisitedUnitId(self, u, id):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE enrollments SET lastunitid=? WHERE courseid=? AND userid=?", (id, self.id, u.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getFirstUnit(self, has_always_granted=False):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if has_always_granted:
                cur.execute("SELECT id FROM units WHERE courseid=? ORDER BY unit_order, id ASC LIMIT 1", (self.id, ))
            else:
                cur.execute("SELECT id FROM units WHERE courseid=? AND availible=1 ORDER BY unit_order, id ASC LIMIT 1", (self.id, ))
            d = cur.fetchone()
            if d is None:
                return 0
            else:
                return int(d["id"])
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()


    def getCourseRole(self, u):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM enrollments WHERE courseid=? AND userid=?", (self.id, u.id))
            d =cur.fetchone()
            if d is None:
                return 1
            return d["permission"]
        except lite.Error as e:
            return 1
        finally:
            if con:
                con.close()

    def setCourseRole(self, u, role):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE enrollments SET permission=? WHERE courseid=? AND userid=?", (role, self.id, u.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getEnrolledByPerm(self, perm):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM enrollments WHERE courseid=? AND permission=?", (self.id, perm))
            d =cur.fetchall()
            return [muser.User.from_id(_["userid"]) for _ in d]
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def getUnitsByType(self, type):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM units WHERE courseid=? AND type=? AND availible=1", (self.id,type))
            d =cur.fetchall()
            return [Units(_["id"]) for _ in d]
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def getMenu(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM units WHERE courseid=? AND parent=0 ORDER BY unit_order, id", (self.id, ))
            data = cur.fetchall()
            d = []
            for dd in data:
                dx = {
                    "id": dd["id"],
                    "title": dd["title"],
                    "availible": bool(dd["availible"]),
                    "children": [],
                    "type": dd["type"],
                    "unit_order": dd["unit_order"]
                }
                cur.execute("SELECT * FROM units WHERE courseid=? AND parent=? ORDER BY unit_order, id", (self.id, dd["id"]))
                ddd = cur.fetchall()
                for dy in ddd:
                    dx["children"].append({
                        "id": dy["id"],
                        "title": dy["title"],
                        "availible": bool(dy["availible"]),
                        "type": dy["type"],
                        "children": [],
                        "unit_order": dy["unit_order"]
                    })
                d.append(dx)
            return d
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()


    # Returns the two view ratings for this user and course.
    #
    # 1) Reached score/Possible score for all quizzes
    # 2) Visited pages/Availible pages for all units
    def getViewRatings(self, user):
        try:
            con = lite.connect('databases/pilearn.db')
            cur = con.cursor()
            cur.execute("SELECT Count(*) FROM visits WHERE courseid=? AND userid=?", (self.id, user.id))
            visited_pages = cur.fetchone()[0]

            cur.execute("SELECT Count(*) FROM units WHERE courseid=? AND availible=1", (self.id,))
            availible_pages = cur.fetchone()[0]

            cur.execute("SELECT visits.data FROM visits, units WHERE visits.courseid=? AND visits.userid=? AND units.id=visits.unitid AND units.type='quiz'", (self.id, user.id))
            quiz_max_score = 0
            quiz_reached_score = 0
            quiz_data = cur.fetchall()

            for entry in quiz_data:
                data = json.loads(entry[0])
                quiz_max_score += data["max"]
                quiz_reached_score += data["sum"]

            return [
                min(100, int(100*quiz_reached_score / quiz_max_score)) if quiz_max_score else 100,
                min(100, int(100*visited_pages / availible_pages)) if availible_pages else 0
            ]
        except lite.Error as e:
            return [None,None]
        finally:
            if con:
                con.close()

    def getInfo(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM courses WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                raise ValueError("Course not found with id " + str(self.id))
            return {
                "id": data['id'],
                "topicid": data['topicid'],
                "title": data['title'],
                "shortdesc": data['shortdesc'],
                "longdesc": data['longdesc'],
                "requirements": data['requirements'],
                "byline": data['byline'],
                "sponsorid": data['sponsorid'],
                "state": data['state'],
                "picture_url": data["picture_url"] or "",
                "manual_enrollment": bool(data["manual_enrollment"])
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
            cur.execute("SELECT * FROM courses WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

class Units:

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
            cur.execute("UPDATE units SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def getTitle(self):
        return self.getDetail("title")

    def getJSON(self):
        return json.loads(self.getDetail("content"))

    def getLabel(self):
        label = self.getTitle()
        label = label.replace("π", "pi")
        label = re.sub("[^a-zA-Z0-9- ]+", "", label)
        label = re.sub("[ ]+", "-", label)
        label = label.lower()[:50].strip("-")
        return label


    def isDisabled(self):
        return not self.getDetail("availible")

    def getType(self):
        return self.getDetail("type")

    def hasViewData(self, user):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM visits WHERE courseid=? AND unitid=? AND userid=?", (self.getDetail("courseid"), self.id, user.id))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getViewData(self, user, as_json=False):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM visits WHERE courseid=? AND unitid=? AND userid=?", (self.getDetail("courseid"), self.id, user.id))
            data = cur.fetchone()
            if not as_json:
                return data["data"]
            else:
                return json.loads(data["data"])
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()

    def addViewData(self, user, data):
        if not self.hasViewData(user):
            try:
                con = lite.connect('databases/pilearn.db')
                con.row_factory = lite.Row
                cur = con.cursor()
                cur.execute("INSERT INTO visits (courseid, unitid, userid, data) VALUES (?, ?, ?, ?)", (self.getDetail("courseid"), self.id, user.id, data))
                con.commit()
                return True
            except lite.Error as e:
                return False
            finally:
                if con:
                    con.close()
        else:
            try:
                con = lite.connect('databases/pilearn.db')
                con.row_factory = lite.Row
                cur = con.cursor()
                cur.execute("UPDATE visits SET data=? WHERE courseid=? AND unitid=? AND userid=?", (data,self.getDetail("courseid"), self.id, user.id))
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
            cur.execute("SELECT * FROM units WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                raise ValueError("Unit not found with id " + str(self.id))
            return {
                "id": data['id'],
                "title": data['title'],
                "courseid": data['courseid'],
                "content": data['content'],
                "type": data['type'],
                "parent": data['parent'],
                "availible": bool(data['availible']),
                "unit_order": data["unit_order"]
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
            cur.execute("SELECT * FROM units WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def new(cls, courseid,empty_set,type,parent):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            try:
                cur.execute("SELECT MAX(unit_order) AS o FROM units WHERE courseid=? AND parent=?", (courseid,parent))
                unit_order = 1 + cur.fetchone()["o"]
            except:
                unit_order = 1
            cur.execute("INSERT INTO units (title, courseid, content, type, parent, availible, unit_order) VALUES ('Neue Seite', ?, ?, ?, ?, 0, ?)", (courseid,empty_set,type,parent, unit_order))
            con.commit()
            return cur.lastrowid
        except lite.Error as e:
            return 0
        finally:
            if con:
                con.close()


class Topic:

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
            cur.execute("UPDATE topics SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()
    @classmethod
    def getTopicsList(cls):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM topics")
            all = cur.fetchall()
            if all is None:
                return []
            all = list([Topic(x["id"]) for x in all])
            return all
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def getCourseList(cls, topic_name):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM courses WHERE topicid="+str(cls.from_name(topic_name).id))
            all = cur.fetchall()
            if all is None:
                return []
            all = list([Courses(x["id"]) for x in all])
            return all
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def getTitle(self):
        return self.getDetail("title")

    def getName(self):
        return self.getDetail("name")

    def getExcerpt(self):
        return self.getDetail("excerpt")

    def getDescription(self):
        return self.getDetail("description")

    def isGiveable(self):
        return self.getDetail("giveable") == 1

    def getInfo(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM topics WHERE id=?", (self.id,))
            data = cur.fetchone()
            if data is None:
                raise ValueError("Topic not found with id " + str(self.id))
            return {
                "id": data['id'],
                "name": data['name'],
                "title": data['title'],
                "excerpt": data['excerpt'],
                "description": data['description'],
                "giveable": bool(data['giveable'])
            }
        except lite.Error as e:
            #raise lite.Error from e
            raise e
        finally:
            if con:
                con.close()
    @classmethod
    def exists(cls, name):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM topics WHERE name=?", (name,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def from_name(cls, name):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM topics WHERE name=?", (name,))
            data = cur.fetchone()
            if data is not None:
                return Topic(data["id"])
            return None
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()

    @classmethod
    def getAll(cls):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM topics WHERE giveable=1")
            data = cur.fetchall()
            DATA =  []
            for d in data:
                DATA.append(Topic(d["id"]))
            return DATA
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def getTrueAll(cls):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT id FROM topics")
            data = cur.fetchall()
            DATA =  []
            for d in data:
                DATA.append(Topic(d["id"]))
            return DATA
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()
