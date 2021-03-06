# coding: utf-8
import os, json, re, time, math
import sqlite3 as lite

class SettingsBlueprint:

    Cache = {}
    CacheDuration = 60 # in 1s

    def set(self, k, v):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("UPDATE settings SET setting_value=? WHERE setting_key=?", (v, k))
            con.commit()
            if k in list(self.Cache.keys()):
                del self.Cache[k]
            return True
        finally:
            if con:
                con.close()

    def get(self, k, vd=None):
        if k in list(self.Cache.keys()):
            entry = self.Cache[k]
            if time.time() - entry[1] < self.CacheDuration:
                return entry[0]
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT setting_value FROM settings WHERE setting_key=?", (k,))
            value = cur.fetchone()
            value = value[0] if value else vd
            self.Cache[k] = [value, time.time()]
            return value
        finally:
            if con:
                con.close()

    def getAllSettingsGrouped(self):
        try:
            con = lite.connect('databases/pilearn.db')
            con.row_factory = lite.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM settings ORDER BY setting_group")

            result = []
            last_group = ""

            for setting in cur.fetchall():
                if setting[0] != last_group:
                    last_group = setting[0]
                    result.append(["group", last_group])

                result.append(["setting", setting])

            return result
        finally:
            if con:
                con.close()


Settings = SettingsBlueprint()
