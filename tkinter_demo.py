import os
import sqlite3
import tkinter
from tkinter import *
import tkinter.messagebox
from tkinter import messagebox

import PIL
import cv2
import numpy as np
from PIL import ImageTk, Image

window = Tk()
window.title("Nhan Dang Khuon Mat")
window.geometry("920x650")
load = Image.open("nhandien3.jpg")
render = ImageTk.PhotoImage(load)
img = Label(window, image=render)
img.place(x=0, y=0)
# Tiêu Đề
lbltitle = Label(window, text="NHẬN DẠNG KHUÔN MẶT GIỐNG NHAU", fg="cyan", font=("Calibri Bold", 30), bg="#131313")
lbltitle.place(x=140, y=5)
# Nhập Tên
blbten = Label(window, text="Nhập Tên", fon=10)
blbten.place(x=10, y=100)
txtTen = Entry(window, width=25)
txtTen.place(x=90, y=100, height=25)
# Nhập ID
blbID = Label(window, text="  Nhập ID ", fon=10).place(x=10, y=150)
txtID = Entry(window, width=25)
txtID.place(x=90, y=150, height=25)
# Thông Báo
boxthongbao = LabelFrame(window, width=230, height=100, bd=5, bg="LIGHTBLUE")
boxthongbao.place(x=10, y=410)
lblthongbao = Label(boxthongbao, font=("Calibri Bold", 20), bg="lightblue", fg="red")

# Giao Diện Camera
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
video = cv2.VideoCapture(0)
# lấy hình ảnh từ webcam frame:hình ret:true
canvas = Canvas(window, width=640, height=480)
canvas.place(x=253, y=57)
photo = None
# số hình đã lấy
sampleNum = 0
# font chữ
fontface = cv2.FONT_HERSHEY_PLAIN
# Biến check: 1 là lấy ảnh, 2 nhận dạng ảnh, default là 0
check = 0
# số lần đọc file train
numberReadTrain = 1
recognizer = cv2.face.LBPHFaceRecognizer_create()
# ID trong lấy ảnh
userID = None
# error trong insertPeople
error = ""


########### Sự Kiên $$$$$$$$$$
def update_frame():
    global canvas, photo, check, sampleNum, numberReadTrain, recognizer, userID
    ret, frame = video.read()
    # lấy ảnh
    if check == 1:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 7)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # tạo thư mục dataSet
            if not os.path.exists('dataSet'):
                os.makedirs('dataSet')
            sampleNum += 1
            # nếu tồn tại ảnh thứ 101 thì file bắt đầu: user.id.201.0
            if os.path.exists('dataSet/User.' + str(userID) + '.200.0.jpg') is True or os.path.exists(
                    'dataSet/User.' + str(userID) + '.200.1.jpg') is True:
                cv2.imwrite('dataSet/User.' + str(userID) + '.' + str(sampleNum + 200) + '.' + '0' + '.jpg',
                            gray[y: y + h, x: x + w])
            # nếu tồn tại ảnh thứ 1 thì file bắt đầu: user.id.101.0
            elif os.path.exists('dataSet/User.' + str(userID) + '.100.0.jpg') is True or os.path.exists(
                    'dataSet/User.' + str(userID) + '.100.1.jpg') is True:
                cv2.imwrite('dataSet/User.' + str(userID) + '.' + str(sampleNum + 100) + '.' + '0' + '.jpg',
                            gray[y: y + h, x: x + w])
            else:
                # lưu khuôn mặt
                # User.1.1.0.jpg chưa train
                # User.1.1.1.jpg đã train
                cv2.imwrite('dataSet/User.' + str(userID) + '.' + str(sampleNum) + '.' + '0' + '.jpg',
                            gray[y: y + h, x: x + w])
            break
        if sampleNum > 99:
            sampleNum = 0
            check = 0
            top = Toplevel()
            my_label = Label(top, text="LẤY ẢNH HOÀN THÀNH").pack()
            userID = None
            btblayanh["state"] = "normal"
    # nhận diện hình ảnh
    elif check == 2:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 7)
        if numberReadTrain == 1:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            numberReadTrain = numberReadTrain + 1
            #recognizer.read('E:\\ChuyenDe\\NhanDienKhuonMat\\recoginzer\\trainingData.yml')
            recognizer.read('recoginzer/trainingData.yml')
        for (x, y, w, h) in faces:
            # vẽ ô vuông
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 225, 0), 2)

            # cắt khuôn mặt trên webcam
            roi_gray = gray[y:y + h, x:x + w]

            # nhận diện người này là ai, trả về tham số id và độ chính xác
            ID, confidence = recognizer.predict(roi_gray)
            name = ""
            if confidence < 100:
                profile = getProfile(ID)
                if profile is not None:
                    confidence = "{0}%".format(round(100 - confidence))
                    cv2.putText(frame, str(profile[1]), (x + 10, y + h + 30), fontface, 1, (0, 255, 0), 2)
                    cv2.putText(frame, str(confidence), (x + 100, y + h + 30), fontface, 1, (0, 255, 255), 2)
                else:
                    cv2.putText(frame, str("Unknow"), (x + 10, y + h + 30), fontface, 1, (0, 0, 255), 2)
            break
    # Chuyen he mau
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Convert hanh image TK
    photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
    # Show
    canvas.create_image(0, 0, image=photo, anchor=tkinter.NW)
    window.after(15, update_frame)


update_frame()


def thoat():
    exit()


def LayAnh():
    global check, userID
    btbnhandien["state"] = "normal"
    res = ""
    if txtID.get() == "":
        res = "Bạn chưa nhập ID"
        messagebox.showerror("Lỗi:", "Bạn chưa nhập ID!!!.")
    else:
        try:
            userID = int(txtID.get().strip())
            if checkID(userID):
                check = 1
                btblayanh["state"] = "disable"
            else:
                messagebox.showerror("Lỗi:", "ID không tồn tại!!!")
        except ValueError:
            messagebox.showerror("Lỗi:", "ID phải nhập số!")
    res = "Đang Lấy Ảnh"
    lblthongbao.place(x=45, y=435)
    lblthongbao.configure(text=res)


def DocAnh():
    global numberReadTrain, recognizer
    btbnhandien["state"] = "normal"
    res = "Đang Đọc Ảnh"
    lblthongbao.pack()
    lblthongbao.configure(text=res)

    path = "dataSet"
    faces, Ids = getImageWithId(path)

    # train
    # faces != []
    if faces:
        recognizer.train(faces, np.array(Ids))
    else:
        top = Toplevel()
        my_label = Label(top, text="Không Có Ảnh Cần Train").pack()
        numberReadTrain = 1
        return
    if not os.path.exists('recoginzer'):
        os.makedirs('recoginzer')

    # lưu file train
    recognizer.save('recoginzer/trainingData.yml')
    top = Toplevel()
    my_label = Label(top, text="Train Ảnh Thành Công").pack()
    numberReadTrain = 1


def NhanDien():
    global check
    check = 2
    btbnhandien["state"] = "disable"
    res = "Đang Nhận Diện"
    lblthongbao.place(x=30, y=435)
    lblthongbao.configure(text=res)


def ThemNhanDien():
    btbnhandien["state"] = "normal"
    res = "Thêm Nhận Diện"
    lblthongbao.place(x=25, y=435)
    lblthongbao.configure(text=res)


def BoSungAnh():
    btbnhandien["state"] = "normal"
    res = "Bổ Sung Ảnh"
    lblthongbao.place(x=45, y=435)
    lblthongbao.configure(text=res)


def DangKy():
    global userID
    btbnhandien["state"] = "normal"
    res = ""
    if txtID.get() == "" or txtTen.get() == "":
        res = "Bạn chưa nhập ID hoặc tên"
    else:
        try:
            # bắt lỗi nhập chữ vào ID
            ID = int(txtID.get().strip())
            insertPeople(ID, txtTen.get().strip())
            # bắt lỗi nhập trùng ID đã lưu
            if error != "":
                messagebox.showerror("Lỗi:", error)
            else:
                if messagebox.askquestion("Hỏi:", "Bạn có muốn lấy ảnh luôn không?.") == "yes":
                    userID = txtID.get()
                    LayAnh()
                res = "Đăng ký thành công"
        except ValueError:
            messagebox.showerror("Lỗi:", "ID phải nhập số!")
    lblthongbao.pack()
    lblthongbao.configure(text=res)


def insertPeople(ID, name):
    global error
    # kết nối sqlite
    conn = sqlite3.connect('facebase.db')
    print(conn)
    # tìm id
    query = "SELECT * FROM people WHERE id=" + str(ID)
    cursor = conn.execute(query)

    isRecordExist = 0

    for row in cursor:
        isRecordExist = 1
    # nếu có update không insert
    if isRecordExist == 0:
        query = "INSERT INTO people(id, name) VALUES(" + str(ID) + ",'" + str(name) + "')"
    else:
        error = "ID đã tồn tại!!! Vui lòng nhập ID khác"

    conn.execute(query)
    conn.commit()
    conn.close()


def checkID(ID):
    #conn = sqlite3.connect('E:\\ChuyenDe\\NhanDienKhuonMat\\facebase.db')
    conn = sqlite3.connect('facebase.db')
    # tìm id
    query = "SELECT * FROM people WHERE id=" + str(ID)
    cursor = conn.execute(query)
    for people in cursor:
        if people is not None:
            return True
    return False


def getImageWithId(path):
    # lấy tất cả đường dẫn ảnh trong "dataSet"
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]

    # print(imagePaths)

    faces = []
    IDs = []

    for imagePath in imagePaths:
        # chuyển hình thành dạng mảng
        faceImg = Image.open(imagePath).convert('L')
        faceNp = np.array(faceImg, 'uint8')

        # print(faceNp)

        # cắt id
        checkTrain = int(imagePath.split('\\')[1].split('.')[3])
        if checkTrain == 0:
            # user.1.1.0
            Id = int(imagePath.split('\\')[1].split('.')[2])
            nameImage = imagePath.split('\\')[1]
            array = imagePath.split('\\')[1].split('.')

            faces.append(faceNp)

            IDs.append(Id)

            os.rename(imagePath, 'dataSet\\' + array[0] + '.' + array[1] + '.' + array[2] + '.' + '1' + '.' + array[4])

    return faces, IDs


def getProfile(ID):
    # kết nối database
    conn = sqlite3.connect('facebase.db')
    query = "SELECT * FROM people WHERE id=" + str(ID)
    cursor = conn.execute(query)

    profile = None

    # lưu các dòng trong db
    for row in cursor:
        profile = row

    conn.close()
    return profile


# Nút Lấy Ảnh
btblayanh = Button(window, text="LẤY ẢNH", bg="orange", fg="black", font=("Calibri Bold", 13), bd=10, command=LayAnh)
btblayanh.place(x=270, y=560, width=110, height=70)
# Nút Thêm Ảnh
btbthemanh = Button(window, text="BỔ SUNG ẢNH", bg="Yellow", fg="Black", font=("Calibri Bold", 13), bd=10,
                     command=BoSungAnh)
btbthemanh.place(x=40, y=330, width=160, height=70)
# Nút Đọc Ảnh
btbtrainanh = Button(window, text="ĐỌC ẢNH", bg="orange", fg="black", font=("Calibri Bold", 13), bd=10, command=DocAnh)
btbtrainanh.place(x=440, y=560, width=115, height=70)
# Nút Nhận Diện
btbnhandien = Button(window, text="NHẬN DIỆN", bg="orange", fg="black", font=("Calibri Bold", 13), bd=10,
                     command=NhanDien)
btbnhandien.place(x=620, y=560, width=120, height=70)
# Nút Thêm Người
btbthemnguoi = Button(window, text="THÊM NHÂN DIỆN", bg="Yellow", fg="Black", font=("Calibri Bold", 13), bd=10,
                     command=ThemNhanDien)
btbthemnguoi.place(x=40, y=230, height=70)
# Nút Đăng Ký
btbdangky = Button(window, text="Đăng Ký", bg="pink", fg="black", font=("Calibri Bold", 10), bd=7, command=DangKy)
btbdangky.place(x=175, y=185, width=70)
# Nút Thoát
btbthoat = Button(window, text="THOÁT", bg="RED", fg="black", font=("Calibri Bold", 13), bd=10, command=thoat)
btbthoat.place(x=800, y=560, width=80, height=70)

window.mainloop()
