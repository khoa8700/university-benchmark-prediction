import pymysql


class database:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "tuvan"

    def connect(self):
        conn = pymysql.connect(
            host=self.host, user=self.user, passwd=self.password, database=self.database
        )
        cursor = conn.cursor()
        return conn, cursor

    def close(self, conn, cursor):
        cursor.close()
        conn.close()

    def getUniCourse(self, group, year):
        conn, cursor = self.connect()
        query = f"SELECT maTruong, maNganh, diem FROM diemxettuyen WHERE (toHop='{group}' AND nam='{year}');"
        cursor.execute(query)
        result = cursor.fetchall()
        self.close(conn, cursor)
        return result

    def getSubjectScore(self, subject, idCourse, idUni):
        conn, cursor = self.connect()
        query = f"SELECT diem FROM diemmon WHERE (mon='{subject}' AND nam IN (SELECT nam from diemxettuyen WHERE (maNganh='{idCourse}' AND maTruong='{idUni}'))) ORDER BY nam ASC"
        # query = f"SELECT diem FROM diemmon WHERE mon='{subject}' ORDER BY nam ASC;"
        cursor.execute(query)
        result = cursor.fetchall()
        self.close(conn, cursor)
        return result

    def getGroup(self):
        conn, cursor = self.connect()
        query = f"SELECT * FROM tohop;"
        cursor.execute(query)
        result = cursor.fetchall()
        self.close(conn, cursor)
        return result

    def getYear(self, group):
        conn, cursor = self.connect()
        query = f"SELECT DISTINCT nam FROM diemxettuyen WHERE tohop='{group}' ORDER BY nam DESC;"
        cursor.execute(query)
        result = cursor.fetchall()
        self.close(conn, cursor)
        return result

    def getSubjectInGroup(self, group):
        conn, cursor = self.connect()
        query = f"SELECT mon1, mon2, mon3 FROM tohop WHERE toHop='{group}';"
        cursor.execute(query)
        result = cursor.fetchone()
        self.close(conn, cursor)
        return result

    def getFinalScore(self, idCourse, idUni):
        conn, cursor = self.connect()
        query = f"SELECT diem FROM diemxettuyen WHERE (maNganh='{idCourse}' AND maTruong='{idUni}') ORDER BY nam ASC;"
        cursor.execute(query)
        result = cursor.fetchall()
        self.close(conn, cursor)
        return result

    def getUni(self, idUni):
        conn, cursor = self.connect()
        query = f"SELECT tenTruong FROM truong WHERE maTruong='{idUni}';"
        cursor.execute(query)
        result = cursor.fetchone()
        self.close(conn, cursor)
        if result != None:
            result = result[0]
        return result

    def getCourse(self, idCourse):
        conn, cursor = self.connect()
        query = f"SELECT tenNganh FROM nganh WHERE maNganh='{idCourse}';"
        cursor.execute(query)
        result = cursor.fetchone()
        self.close(conn, cursor)
        if result != None:
            result = result[0]
        return result

    def checkLogin(self, id, pwd):
        conn, cursor = self.connect()
        query = (
            f"SELECT * FROM account WHERE (id='{id}' AND pass=OLD_PASSWORD('{pwd}'));"
        )
        cursor.execute(query)
        result = cursor.fetchone()
        self.close(conn, cursor)
        if result != None:
            return True
        return False

    def updateScore(self, idCourse, idUni, group, year, score):
        conn, cursor = self.connect()
        query = f"UPDATE diemxettuyen SET diem='{score}' WHERE (maNganh='{idCourse}' AND maTruong='{idUni}' AND toHop='{group}' AND nam='{year}');"
        try:
            cursor.execute(query)
            conn.commit()
            self.close(conn, cursor)
            return "ok"
        except:
            return "SQL error"

    def addCourse(self, idCourse, nameCourse):
        conn, cursor = self.connect()
        query = f"INSERT INTO nganh (maNganh, tenNganh) VALUES ('{idCourse}', '{nameCourse}');"
        try:
            cursor.execute(query)
            conn.commit()
            self.close(conn, cursor)
            return "ok"
        except:
            return "SQL error"

    def addUni(self, idUni, nameUni):
        conn, cursor = self.connect()
        query = (
            f"INSERT INTO truong (maTruong, tenTruong) VALUES ('{idUni}', '{nameUni}');"
        )
        try:
            cursor.execute(query)
            conn.commit()
            self.close(conn, cursor)
            return "ok"
        except:
            return "SQL error"

    def addUniCourse(self, idCourse, idUni, group, year, score=0.0):
        conn, cursor = self.connect()
        query = f"INSERT INTO diemxettuyen (maNganh, maTruong, toHop, diem, nam) VALUES ('{idCourse}', '{idUni}', '{group}', '{score}', '{year}');"
        try:
            cursor.execute(query)
            conn.commit()
            self.close(conn, cursor)
            return "ok"
        except:
            return "SQL error"

    def addGroup(self, group, subject1, subject2, subject3):
        conn, cursor = self.connect()
        query = f"INSERT INTO tohop (toHop, mon1, mon2, mon3) VALUES ('{group}', '{subject1}', '{subject2}', '{subject3}');"
        try:
            cursor.execute(query)
            conn.commit()
            self.close(conn, cursor)
            return "ok"
        except:
            return "SQL error"

    def addSubjectScore(self, subject, score, year):
        conn, cursor = self.connect()
        query = f"INSERT INTO diemmon (mon,diem,nam) VALUES ('{subject}', '{score}', '{year}');"
        try:
            cursor.execute(query)
            conn.commit()
            self.close(conn, cursor)
            return "ok"
        except:
            return "SQL error"
