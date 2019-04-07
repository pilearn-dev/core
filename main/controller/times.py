# coding: utf-8
"""
    Module for relative and absolute timestamps
    ===========================================
"""

import time as t


def duration2text(dur):
    lang = ["zwei", "drei", "vier", u"fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", u"zwölf"]
    if dur == 1:
      return "eine Sekunde"
    if dur <= 12:
      return lang[dur - 2] + " Sekunden"
    elif dur < 60:
      return str(dur) + " Sekunden"
    else:
      dur = int(0.5+dur / 60.0)
      if dur == 1:
          return "eine Minute"
      elif dur <= 12:
          return lang[dur - 2] + " Minuten"
      elif dur < 60:
          return str(dur) + " Minuten"
      else:
          dur = int(0.5+dur / 60.0)
          if dur == 1:
              return "eine Stunde"
          elif dur <= 12:
              return lang[dur - 2] + " Stunden"
          elif dur < 24:
              return str(dur) + " Stunden"
          else:
              dur = int(dur / 24.0)
              if dur == 1:
                  return "einen Tag"
              elif dur < 7:
                  return lang[dur - 2] + " Tage"
              else:
                  dur = int(dur / 7.0)
                  if dur == 1:
                      return "eine Woche"
                  elif dur < 4:
                      return lang[dur - 2] + " Wochen"
                  else:
                      dur = int(dur / 4.0)
                      if dur == 1:
                          return "einen Monat"
                      elif dur < 12:
                          return lang[dur - 2] + " Monate"
                      else:
                          dur = int(dur / 12.0)
                          if dur == 1:
                              return "ein Jahr"
                          elif dur <= 12:
                              return lang[dur - 2] + " Jahren"
                          else:
                              return str(dur) +  " Jahren"

def duration2shorttext(dur):
    if dur < 60:
      return str(dur) + "s"
    else:
      dur = int(0.5+dur / 60.0)
      if dur < 60:
          return str(dur) + " min"
      else:
          dur = int(0.5+dur / 60.0)
          if dur < 24:
              return str(dur) + "h"
          else:
              dur = int(dur / 24.0)
              if dur < 7:
                  return str(dur) + "d"
              else:
                  dur = int(dur / 7.0)
                  if dur < 4:
                      return str(dur) + "w"
                  else:
                      dur = int(dur / 4.0)
                      if dur < 12:
                          return str(dur) + "m"
                      else:
                          dur = int(dur / 12.0)
                          return str(dur) +  "y"

def stamp2german(stamp):
    loct = t.localtime(stamp)
    date = str(loct.tm_mday).zfill(2) + "." + \
            str(loct.tm_mon).zfill(2) + "." + \
            str(loct.tm_year) + " " + \
            str(loct.tm_hour).zfill(2) + ":" + \
            str(loct.tm_min).zfill(2) + ":" + \
            str(loct.tm_sec).zfill(2)
    return date

def stamp2shortrelative(stamp, is_delta=False):
    now = int(t.time())
    relta = (stamp - now)
    if relta > 0:
        if is_delta:
            prefix = "bis in "
        else:
            prefix = "in "
    else:
        if is_delta:
            prefix = "seit "
        else:
            prefix = "vor "
    delta = abs(relta)
    if delta < 60:
        suffix = str(delta) + "s"
    else:
        delta = int(0.5+delta / 60.0)
        if delta < 60:
            suffix = str(delta) + " min"
        else:
            delta = int(0.5+delta / 60.0)
            if delta < 24:
                suffix = str(delta) + "h"
            else:
                delta = int(0.5+delta / 24.0)
                if delta < 7:
                    suffix = str(delta) + "d"
                else:
                    delta = int(0.5+delta / 7.0)
                    if delta < 4:
                        suffix = str(delta) + "w"
                    else:
                        delta = int(0.5+delta / 4.0)
                        if delta < 12:
                            suffix = str(delta) + "m"
                        else:
                            delta = int(0.5+delta / 12.0)
                            suffix = str(delta) + "y"
    return prefix + suffix

def stamp2relative(stamp, is_delta=False):
    now = t.time()
    relta = stamp - now
    if relta > 0:
        if is_delta:
            prefix = "bis in "
        else:
            prefix = "in "
    else:
        if is_delta:
            prefix = "seit "
        else:
            prefix = "vor "
    lang = ["zwei", "drei", "vier", u"fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", u"zwölf"]
    delta = abs(relta)
    if delta < 10:
        suffix = "wenigen Sekunden"
    elif delta < 40:
        suffix = "weniger als einer Minute"
    else:
        delta = int(0.5+delta / 60.0)
        if delta == 1:
            suffix = "einer Minute"
        elif delta < 12:
            suffix = lang[delta - 2] + " Minuten"
        elif delta < 15:
            suffix = "einer viertel Stunde"
        elif delta < 25:
            suffix = "zwanzig Minuten"
        elif delta < 35:
            suffix = "einer halben Stunde"
        elif delta < 40:
            suffix = "vierzig Minuten"
        elif delta < 50:
            suffix = "einer dreiviertel Stunde"
        elif delta < 55:
            suffix = u"fünfzig Minuten"
        else:
            delta = int(0.5+delta / 60.0)
            if delta == 1:
                suffix = "einer Stunde"
            elif delta < 12:
                suffix = lang[delta - 2] + " Stunden"
            elif delta < 24:
                suffix = str(delta) + " Stunden"
            else:
                delta = int(0.5+delta / 24.0)
                if delta == 1:
                    if relta < 0:
                        suffix = "gestern"
                        if not is_delta:
                            prefix = ""
                    else:
                        suffix = "morgen"
                        prefix = ""
                        if is_delta:
                            prefix = "bis "
                elif delta < 7:
                    suffix = lang[delta - 2] + " Tagen"
                else:
                    delta = int(0.5+delta / 7.0)
                    if delta == 1:
                        suffix = "einer Woche"
                    elif delta < 4:
                        suffix = lang[delta - 2] + " Wochen"
                    else:
                        delta = int(0.5+delta / 4.0)
                        if delta == 1:
                            suffix = "einem Monat"
                        elif delta < 12:
                            suffix = lang[delta - 2] + " Monaten"
                        else:
                            delta = int(0.5+delta / 12.0)
                            if delta == 1:
                                suffix = "einem Jahr"
                            elif delta <= 3:
                                suffix = lang[delta - 2] + " Jahren"
                            else:
                                if relta > 0:
                                    if is_delta:
                                        prefix = "bis zum "
                                    else:
                                        prefix = "am "
                                else:
                                    if is_delta:
                                        prefix = "seit dem "
                                    else:
                                        prefix = "am "
                                suffix = stamp2german(stamp)
    return prefix + suffix
