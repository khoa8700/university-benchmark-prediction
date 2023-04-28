import socket
import threading
import json

from database import database
import numpy as np
from sklearn import linear_model
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

IP = "localhost"
PORT = 5566
ADDR = (IP, PORT)

db = database()


def predict(maNganh, maTruong, group):
    sbj1, sbj2, sbj3 = db.getSubjectInGroup(group)
    score1 = np.array(db.getSubjectScore(sbj1, maNganh, maTruong))
    score2 = np.array(db.getSubjectScore(sbj2, maNganh, maTruong))
    score3 = np.array(db.getSubjectScore(sbj3, maNganh, maTruong))
    if len(score1) != len(score2) or len(score1) != len(score3):
        print("thieu du lieu diem thi")
        return 0
    score = score1 + score2 + score3
    finalScore = np.array(db.getFinalScore(maNganh, maTruong)[:-1])
    if len(finalScore) != len(score) - 1:
        return 0
    one = np.ones((score[:-1].shape[0], 1))
    Score = np.concatenate((one, score[:-1]), axis=1)
    regr = linear_model.LinearRegression(fit_intercept=False)
    regr.fit(Score, finalScore)
    w0 = regr.coef_[0][0]
    w1 = regr.coef_[0][1]
    return round(float(w1 * score[-1] + w0), 2)


def getGroupList():
    rows = db.getGroup()
    res = {}
    for row in rows:
        res[row[0]] = row[1:]
    return res


def getScoreList(group, score, year):
    uniList = db.getUniCourse(group, year)
    res = []
    for maTruong, maNganh, diem in uniList:
        if diem == 0.0:
            diem = predict(maNganh, maTruong, group)
            db.updateScore(maNganh, maTruong, group, year, diem)
        if score >= diem and diem != 0.0:
            tenTruong = db.getUni(maTruong)
            if tenTruong == None:
                print("thieu ten truong", maTruong)
                tenTruong = maTruong
            tenNganh = db.getCourse(maNganh)
            if tenNganh == None:
                print("thieu ten nganh", maNganh)
                tenNganh = maNganh
            res.append((tenTruong, tenNganh, diem))
    return res


def handle_client(conn, addr):
    print(f"{addr} connected.")
    key = os.urandom(16)
    iv = os.urandom(16)
    connected = True
    while connected:
        recv = json.loads(conn.recv(1024).decode())

        if recv["command"] == "getGroupList":
            conn.send(json.dumps(getGroupList()).encode())
            continue
        if recv["command"] == "getYearList":
            conn.send(json.dumps(db.getYear(recv["group"])).encode())
            continue
        if recv["command"] == "getScoreList":
            conn.send(
                json.dumps(
                    getScoreList(recv["group"], recv["score"], recv["year"])
                ).encode()
            )
            continue
        if recv["command"] == "login":
            if db.checkLogin(recv["id"], recv["pwd"]):
                cipher = AES.new(key, AES.MODE_CBC, iv)
                conn.send(
                    json.dumps(
                        {
                            "status": "Login success!",
                            "auth": cipher.encrypt(pad(b"ADMIN", 16)).hex(),
                        }
                    ).encode()
                )
            else:
                conn.send(json.dumps({"status": "Login fail!"}).encode())
            continue
        cipher = AES.new(key, AES.MODE_CBC, iv)
        if unpad(cipher.decrypt(bytes.fromhex(recv["auth"])), 16) == b"ADMIN":
            try:
                if recv["command"] == "addUni":
                    conn.send(db.addUni(*recv["arg"]).encode())
                    continue
                if recv["command"] == "addCourse":
                    conn.send(db.addCourse(*recv["arg"]).encode())
                    continue
                if recv["command"] == "addGroup":
                    conn.send(db.addGroup(*recv["arg"]).encode())
                    continue
                if recv["command"] == "addUniCourse":
                    conn.send(db.addUniCourse(*recv["arg"]).encode())
                    continue
                if recv["command"] == "addSubjectScore":
                    conn.send(db.addSubjectScore(*recv["arg"]).encode())
                    continue
                if recv["command"] == "updateScore":
                    conn.send(db.updateScore(*recv["arg"]).encode())
                    continue
            except:
                conn.send("wrong json format".encode())
    conn.close()


def main():
    print("Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"Server is listening on {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    main()
