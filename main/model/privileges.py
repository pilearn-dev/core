import json

# Returns a list with all privileges.
def getAll():
    f = open("privileges.json", "r")
    PRIV_DATA = json.loads(f.read())
    f.close()
    return PRIV_DATA

# Returns a list with all privileges information
def getInformations():
    f = open("privilege_data.json", "r")
    PRIV_INFO = json.loads(f.read())
    f.close()
    return PRIV_INFO

def getSingleInformation(priv):
    for data in getInformations():
        if data["id"] == priv:
            return data
    raise ValueError("Privilege not found: " + priv)

# Returns one privilege
def getOne(p):
    return getAll()[p]
