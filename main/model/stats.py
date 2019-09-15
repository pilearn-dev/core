import sqlite3 as lite
class NumericDistribution:

    def __init__(self, filename, table, column, filter="1=1"):
        self.__data = []
        self.filename = filename
        self.table = table
        self.column = column
        self.filter = filter
        self.init()

    def init(self):
        con = None
        try:
            con = lite.connect('databases/'+self.filename)
            cur = con.cursor()
            cur.execute("SELECT "+self.column+" FROM "+self.table+" WHERE "+self.filter)
            self.__data = sorted(list(map(lambda x: x[0], cur.fetchall())))
            return self.__data
        except lite.Error as e:
            print(e)
            return self.__data
        finally:
            if con:
                con.close()

    def getMedian(self, perc):
        perc = int(0.5+len(self.__data) * (perc / 100.0))
        return self.__data[perc]

    def get10(self): return self.getMedian(10)
    def get25(self): return self.getMedian(25)
    def get50(self): return self.getMedian(50)
    def get75(self): return self.getMedian(75)
    def get90(self): return self.getMedian(90)

    def getArMed(self):
        return sum([(float(i)/len(self.__data)) for i in self.__data])
ReputationDistribution = NumericDistribution("pilearn.db", "user", "reputation", "deleted=0 AND banned=0")
