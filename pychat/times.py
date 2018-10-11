# coding: utf-8
"""
    Module for relative and absolute timestamps
    ===========================================
"""

import time as t

def stamp2german(stamp):
    loct = t.localtime(stamp)
    date = str(loct.tm_mday).zfill(2) + "." + \
            str(loct.tm_mon).zfill(2) + "." + \
            str(loct.tm_year) + " " + \
            str(loct.tm_hour).zfill(2) + ":" + \
            str(loct.tm_min).zfill(2) + ":" + \
            str(loct.tm_sec).zfill(2)
    return date

def stamp2relative(stamp):
    now = t.time()
    relta = stamp - now
    if relta > 0:
        prefix = "in "
    else:
        prefix = "vor "
    lang = ["zwei", "drei", "vier", u"fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", u"zwölf"]
    delta = abs(relta)
    if delta < 10:
        suffix = "wenigen Sekunden"
    elif delta < 60:
        suffix = "weniger als einer Minute"
    else:
        delta = int(delta / 60.0)
        if delta == 1:
            suffix = "einer Minute"
        elif delta < 12:
            suffix = lang[delta - 2] + " Minuten"
        elif delta < 15:
            suffix = "einer viertel Stunde"
        elif delta < 25:
            suffix = "weniger als einer halben Stunde"
        elif delta < 35:
            suffix = "einer halben Stunde"
        elif delta < 40:
            suffix = "weniger als einer dreiviertel Stunde"
        elif delta < 55:
            suffix = "einer dreiviertel Stunde"
        elif delta < 60:
            suffix = "weniger als einer halben Stunde"
        else:
            delta = int(delta / 60.0)
            if delta == 1:
                suffix = "einer Stunde"
            elif delta < 24:
                suffix = lang[delta - 2] + " Stunden"
            else:
                delta = int(delta / 24.0)
                if delta == 1:
                    if relta < 0:
                        suffix = "gestern"
                        prefix = ""
                    else:
                        suffix = "morgen"
                        prefix = ""
                elif delta < 7:
                    suffix = lang[delta - 2] + " Tagen"
                else:
                    delta = int(delta / 7.0)
                    if delta == 1:
                        suffix = "einer Woche"
                    elif delta < 4:
                        suffix = lang[delta - 2] + " Wochen"
                    else:
                        delta = int(delta / 4.0)
                        if delta == 1:
                            suffix = "einem Monat"
                        elif delta < 12:
                            suffix = lang[delta - 2] + " Monaten"
                        else:
                            delta = int(delta / 12.0)
                            if delta == 1:
                                suffix = "einem Jahr"
                            elif delta <= 3:
                                suffix = lang[delta - 2] + " Jahren"
                            else:
                                if relta > 0:
                                    prefix = "zum "
                                else:
                                    prefix = "seit dem "
                                suffix = stamp2german(stamp)
    return prefix + suffix