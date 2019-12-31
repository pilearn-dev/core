# coding: utf-8
import os, json, re, time, math
import secrets
import sqlite3 as lite
from flask import request, session, url_for
from sha1 import sha1
from model import user as muser, courses as mcourses
from controller import times as ctimes

class Branch:

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
            cur.execute("UPDATE branches SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getMenu(self):
        menu = self.getCourse().getMenu()
        new_menu = self.applyMenuOverrides(menu)
        for item in new_menu:
            item["children"] = sorted(item["children"], key=lambda x: x["unit_order"])
            #print [(x["title"], x["unit_order"]) for x in item["children"]]
        new_menu = sorted(new_menu, key=lambda x: x["unit_order"])
        return new_menu

    def applyMenuOverrides(self, menu):
        new_menu = []
        for item in menu:
            item.update({
                "changed": False,
                "created": False,
                "overrides": None
            })
            for subitem in item["children"]:
                subitem.update({
                    "changed": False,
                    "created": False,
                    "overrides": None
                })
            new_menu.append(item)


        change_requests = self.getOverrides()
        last_round_changes = -1
        while last_round_changes != 0:
            while None in change_requests:
                del change_requests[change_requests.index(None)]
            last_round_changes = 0
            for request_id in range(len(change_requests)):
                request = change_requests[request_id]
                if request["overrides"]:
                    index = 0
                    for unit in new_menu:
                        if unit["id"] == request["overrides"]:
                            unit["title"] = request["title"]
                            unit["content"] = request["content"]
                            unit["unit_order"] = request["unit_order"]
                            unit["changed"] = bool(request["changed"])
                            unit["created"] = bool(request["created"])
                            unit["overrides"] = request["id"]

                            if 0 == request["parent_unit"] and not request["parent_override"]:
                                change_requests[request_id] = None
                                last_round_changes += 1
                                break
                            elif request["parent_override"]:
                                for tunit in new_menu:
                                    if tunit["overrides"] == request["parent_override"]:
                                        tunit["children"] += [unit]
                                        change_requests[request_id] = None
                                        del new_menu[index]
                                        last_round_changes += 1
                                        break
                            else:
                                for tunit in new_menu:
                                    if tunit["id"] == request["parent_unit"]:
                                        tunit["children"] += [unit]
                                        change_requests[request_id] = None
                                        del new_menu[index]
                                        last_round_changes += 1
                                        break

                        subindex = 0
                        for subunit in unit["children"]:
                            if subunit["id"] == request["overrides"]:
                                subunit["title"] = request["title"]
                                subunit["content"] = request["content"]
                                subunit["unit_order"] = request["unit_order"]
                                subunit["changed"] = bool(request["changed"])
                                subunit["created"] = bool(request["created"])
                                subunit["overrides"] = request["id"]

                                if unit["id"] == request["parent_unit"] and not request["parent_override"]:
                                    change_requests[request_id] = None
                                    last_round_changes += 1
                                    break
                                elif request["parent_override"]:
                                    for tunit in new_menu:
                                        if tunit["overrides"] == request["parent_override"]:
                                            tunit["children"] += [subunit]
                                            change_requests[request_id] = None
                                            del new_menu[index]["children"][subindex]
                                            last_round_changes += 1
                                            break
                                elif request["parent_unit"]:
                                    for tunit in new_menu:
                                        if tunit["id"] == request["parent_unit"]:
                                            tunit["children"] += [subunit]
                                            change_requests[request_id] = None
                                            del new_menu[index]["children"][subindex]
                                            last_round_changes += 1
                                            break
                                else:
                                    new_menu += [subunit]
                                    change_requests[request_id] = None
                                    del new_menu[index]["children"][subindex]
                                    last_round_changes += 1
                                    break
                            subindex += 1
                        else:
                            index += 1
                            continue
                        break
                else:
                    item = [{
                        "id": None,
                        "title": request["title"],
                        "availible": True,
                        "children": [],
                        "type": request["type"],
                        "unit_order": request["unit_order"],
                        "changed": bool(request["changed"]),
                        "created": bool(request["created"]),
                        "overrides": request["id"]
                    }]
                    if request["parent_unit"] != 0:
                        for unit in new_menu:
                            if unit["id"] == request["parent_unit"]:
                                unit["children"] += item
                                change_requests[request_id] = None
                                last_round_changes += 1
                                break

                            for subunit in unit["children"]:
                                if subunit["id"] == request["parent_unit"]:
                                    subunit["children"] += item
                                    change_requests[request_id] = None
                                    last_round_changes += 1
                                    break
                            else:
                                continue
                            break
                    elif request["parent_override"] != 0:
                        for unit in new_menu:
                            if unit["overrides"] == request["parent_override"]:
                                unit["children"] += item
                                change_requests[request_id] = None
                                last_round_changes += 1
                                break

                            for subunit in unit["children"]:
                                if subunit["overrides"] == request["parent_override"]:
                                    subunit["children"] += item
                                    change_requests[request_id] = None
                                    last_round_changes += 1
                                    break
                            else:
                                continue
                            break
                    else:
                        new_menu += item
                        change_requests[request_id] = None
                        last_round_changes += 1

        return new_menu

    def apply(self):
        change_requests = self.getOverrides()
        last_round_changes = -1
        while last_round_changes != 0:
            while None in change_requests:
                del change_requests[change_requests.index(None)]
            last_round_changes = 0

            for change in change_requests:
                if change["overrides"]:
                    if change["parent_override"] and not change["parent_unit"]:
                        continue
                    unit = mcourses.Units(change["overrides"])
                    unit.setDetail("title", change["title"])
                    unit.setDetail("content", change["content"])
                    unit.setDetail("parent", change["parent_unit"])
                    unit.setDetail("unit_order", change["unit_order"])
                else:
                    if change["parent_override"] and not change["parent_unit"]:
                        continue
                    unit = mcourses.Units.new(self.getDetail("course_id"), change["content"], change["type"], change["parent_unit"])
                    unit = mcourses.Units(unit)
                    unit.setDetail("title", change["title"])
                    unit.setDetail("unit_order", change["unit_order"])
                    unit.setDetail("availible", 1)

                    self.mapOverrideToUnit(change["id"], unit.id)

                    for chr in change_requests:
                        if chr is None: continue
                        if chr["parent_override"] == change["id"]:
                            chr["parent_unit"] = unit.id

    def calculateRepDelta(self):
        score = 0
        changes = self.getOverrides()
        for change in changes:
            if change["created"]:
                score += 10
            else:
                unit = mcourses.Units(change["overrides"])
                if unit.getTitle() != change["title"]:
                    score += 1
                if json.loads(unit.getDetail("content")) != json.loads(change["content"]):
                    score += 5
                    if len(unit.getDetail("content")) <= 2 * len(change["content"]):
                        score += 5
        if score > 50:
            score = 50
        if score < 2:
            score = 2
        self.setDetail("delta_factor", score)
        return score


    def getCourse(self):
        return mcourses.Courses(self.getDetail("course_id"))

    def getAuthor(self):
        return muser.User.safe(self.getDetail("author"))

    def isAbandoned(self): return bool(self.getDetail("abandoned"))

    def getOverrides(self, parent_unit=None, parent_override=None):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if parent_unit is not None and parent_override is not None:
                cur.execute("SELECT * FROM branch_overrides WHERE branch=? AND parent_unit=? AND parent_override = ?", (self.id, parent_unit, parent_override))
            elif parent_unit is not None:
                cur.execute("SELECT * FROM branch_overrides WHERE branch=? AND parent_unit=?", (self.id, parent_unit))
            elif parent_override is not None:
                cur.execute("SELECT * FROM branch_overrides WHERE branch=? AND parent_override=?", (self.id, parent_override))
            else:
                cur.execute("SELECT * FROM branch_overrides WHERE branch=?", (self.id,))
            return cur.fetchall()
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    def getSingleOverride(self, id):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM branch_overrides WHERE id=?", (id,))
            return cur.fetchone()
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()

    def mapOverrideToUnit(self, override_id, unit_id):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE branch_overrides SET overrides=? WHERE id=?", (unit_id, override_id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def removeOverride(self, id):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("DELETE FROM branch_overrides WHERE id=?", (id,))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def hasOverrideForUnit(self, unit_id):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM branch_overrides WHERE branch=? AND overrides=?", (self.id, unit_id))
            return cur.fetchone()
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def updateOrMakeOverride(self, unit_id, override_id, data):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if self.hasOverrideForUnit(unit_id) or override_id != "-":
                if override_id != "-":
                    cur.execute("UPDATE branch_overrides SET parent_unit=?, parent_override=?, title=?, content=?, type=?, unit_order=? WHERE id=?", (data["parent_unit"], data["parent_override"], data["title"], data["content"], data["type"], data["unit_order"], override_id))

                    rowid = override_id
                else:
                    cur.execute("UPDATE branch_overrides SET parent_unit=?, parent_override=?, title=?, content=?, type=?, unit_order=? WHERE branch=? AND overrides=?", (data["parent_unit"], data["parent_override"], data["title"], data["content"], data["type"], data["unit_order"], self.id, unit_id))

                    cur.execute("SELECT * FROM branch_overrides WHERE branch=? AND overrides=?", (self.id,unit_id))
                    rowid = cur.fetchone()["id"]
            else:
                cur.execute("INSERT INTO branch_overrides (branch, overrides, parent_unit, parent_override, title, content, type, unit_order, changed, created) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 0)", (self.id, unit_id, data["parent_unit"], data["parent_override"], data["title"], data["content"], data["type"], data["unit_order"]))
                rowid = cur.lastrowid
            con.commit()
            return rowid
        except lite.Error as e:
            print(e)
            return False
        finally:
            if con:
                con.close()

    def newUnitOverride(self, title, body, type):
        data = {
            "title": title,
            "type": type,
            "content": body,
            "parent_unit": 0,
            "parent_override": 0,
            "unit_order": self.getMenu()[-1]["unit_order"]
        }
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO branch_overrides (branch, overrides, parent_unit, parent_override, title, content, type, unit_order, changed, created) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 1)", (self.id, None, data["parent_unit"], data["parent_override"], data["title"], data["content"], data["type"], data["unit_order"]))
            rowid = cur.lastrowid
            con.commit()
            return rowid
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
            cur.execute("SELECT * FROM branches WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                raise ValueError("Branch not found with id " + str(self.id))
            return {
                "id": data['id'],
                "author": data['author'],
                "course_id": data['course_id'],
                "pull_request": data['pull_request'],
                "abandoned": data['abandoned'],
                "abandoned_date": data['abandoned_date'],
                "decision": data['decision'],
                "decision_date": data['decision_date'],
                "hide_as_spam": data['hide_as_spam'],
                "delta_factor": data['delta_factor']
            }
        except lite.Error as e:
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
            cur.execute("SELECT * FROM branches WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def getByCourseAndUser(cls, course_id, user_id, limit_to_active=False):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            if limit_to_active:
                cur.execute("SELECT id FROM branches WHERE course_id=? AND author=? AND decision=0 AND abandoned=0", (course_id, user_id))
            else:
                cur.execute("SELECT id FROM branches WHERE course_id=? AND author=?", (course_id, user_id))
            data = cur.fetchone()
            return Branch(data["id"]) if data is not None else None
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()

    @classmethod
    def new(cls, course_id, user_id):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO branches (author, course_id, pull_request, abandoned, abandoned_date, decision, decision_date, hide_as_spam, delta_factor) VALUES (?, ?, NULL, 0, 0, 0, 0, 0, 0)", (user_id, course_id))
            data = con.commit()
            return Branch(cur.lastrowid)
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()






class PullRequest:

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
            cur.execute("UPDATE pull_requests SET "+d+"=? WHERE id=?", (v, self.id))
            con.commit()
            return True
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    def getCourse(self):
        return mcourses.Courses(self.getDetail("course_id"))

    def getBranch(self):
        return Branch(self.getDetail("branch_id"))

    def getAuthor(self):
        return muser.User.safe(self.getDetail("author"))

    def isHiddenAsSpam(self):
        return bool(self.getDetail("hide_as_spam"))

    def getCreationDate(self):
        dt = self.getDetail("proposal_date")
        return [dt, ctimes.stamp2german(dt), ctimes.stamp2shortrelative(dt, False)]

    def getTitle(self): return self.getDetail("title")
    def getDescription(self): return self.getDetail("description")
    def getState(self): return self.getDetail("decision")

    def getInfo(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM pull_requests WHERE id=?", (self.id, ))
            data = cur.fetchone()
            if data is None:
                raise ValueError("PullRequest not found with id " + str(self.id))
            return {
                "id": data['id'],
                "author": data['author'],
                "branch_id": data['branch_id'],
                "course_id": data['course_id'],
                "title": data['title'],
                "description": data['description'],
                "decision": data['decision'],
                "decision_date": data['decision_date'],
                "proposal_date": data['proposal_date'],
                "hide_as_spam": data['hide_as_spam']
            }
        except lite.Error as e:
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
            cur.execute("SELECT * FROM pull_requests WHERE id=?", (id,))
            data = cur.fetchone()
            return data is not None
        except lite.Error as e:
            return False
        finally:
            if con:
                con.close()

    @classmethod
    def getByCourse(cls, course_id, limit_to_active_state):
        try:
            con = lite.connect('databases/pilearn.db')
            cur = con.cursor()
            if limit_to_active_state is True:
                cur.execute("SELECT id FROM pull_requests WHERE course_id=? AND decision=0", (course_id,))
            elif limit_to_active_state is False:
                cur.execute("SELECT id FROM pull_requests WHERE course_id=? AND decision!=0", (course_id,))
            else:
                cur.execute("SELECT id FROM pull_requests WHERE course_id=?", (course_id,))
            data = cur.fetchall()
            return [PullRequest(d[0]) for d in data]
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def getByUser(cls, user_id, limit_to_active_state):
        try:
            con = lite.connect('databases/pilearn.db')
            cur = con.cursor()
            if limit_to_active_state is True:
                cur.execute("SELECT id FROM pull_requests WHERE author=? AND decision=0", (user_id,))
            elif limit_to_active_state is False:
                cur.execute("SELECT id FROM pull_requests WHERE author=? AND decision!=0", (user_id,))
            else:
                cur.execute("SELECT id FROM pull_requests WHERE author=?", (user_id,))
            data = cur.fetchall()
            return [PullRequest(d[0]) for d in data]
        except lite.Error as e:
            return []
        finally:
            if con:
                con.close()

    @classmethod
    def new(cls, course_id, branch_id, user_id, title, description):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("INSERT INTO pull_requests (author, branch_id, course_id, title, description, decision, decision_date, hide_as_spam, proposal_date) VALUES (?, ?, ?, ?, ?, 0, 0, 0, ?)", (user_id, branch_id, course_id, title, description, time.time()))
            data = con.commit()
            return Branch(cur.lastrowid)
        except lite.Error as e:
            return None
        finally:
            if con:
                con.close()
