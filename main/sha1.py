import hashlib
def sha1(string):
    string = string.encode("utf-8")
    m = hashlib.sha256()
    m.update(string)
    return m.hexdigest()

def md5(string):
    string = string.encode("utf-8")
    m = hashlib.md5()
    m.update(string)
    return m.hexdigest()
