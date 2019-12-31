# coding: utf-8
WORD_CHAR = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-+äöüÄÖÜß"

def buildSFTextQuery(fieldName, s):
    FLAG_DIRECT = False
    FLAG_OR = False
    ADD_DATA = []
    SEARCH_DATA = []

    if s.startswith("="):
        FLAG_DIRECT = True
        s = s[1:]
    elif s.startswith("*"):
        FLAG_OR = True
        s = s[1:]

    if FLAG_DIRECT:
        return [fieldName+"=?", (s,)]

    s = s.strip().split(" ")
    for word in s:
        flag_not = False
        if word.startswith("!"):
            flag_not = True
            word = word[1:]
        new_word = ""
        for char in word:
            if char in WORD_CHAR:
                new_word += char
        if not new_word:
            continue
        new_word = new_word.replace("+", " ").strip()
        if flag_not:
            SEARCH_DATA.append(fieldName+" NOT LIKE ?")
        else:
            SEARCH_DATA.append(fieldName+" LIKE ?")
        ADD_DATA.append("%"+new_word+"%")

    if FLAG_OR:
        SEARCH_DATA = " OR ".join(SEARCH_DATA)
    else:
        SEARCH_DATA = " AND ".join(SEARCH_DATA)

    return [SEARCH_DATA, ADD_DATA]
