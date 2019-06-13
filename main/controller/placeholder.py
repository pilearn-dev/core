def parseGeneral(text):
    return text

def parseForForum(text, forum):
    if forum.id == 0:
        text = text.replace("${forum_name}", "globale Forum")
        text = text.replace("${forum_title}", forum.getTitle())
        text = text.replace("${forum_url}", "/f/0")
        text = text.replace("${forum_link}", "<a href='/f/0'>" + forum.getTitle() + "</a>")
    else:
        text = text.replace("${forum_name}", "Kursforum zu " + forum.getTitle())
        text = text.replace("${forum_title}", forum.getTitle())
        text = text.replace("${forum_url}", "/f/%i" % forum.id)
        text = text.replace("${forum_link}", ("<a href='/f/%i'>" + forum.getTitle() + "</a>") % forum.id)
    return parseGeneral(text)

def parseForCourse(text, course):
    return parseGeneral(text)
