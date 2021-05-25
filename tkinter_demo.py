import tkinter
from tkinter import *

import PIL.Image
import PIL.ImageTk
import cv2
from PIL import ImageTk, Image

import os
import sqlite3
import numpy as np
from tkinter import messagebox
from tkinter import ttk

window = Tk()
window.title("Nhan Dang Khuon Mat")
window.geometry("920x650+300+50")
window.config(bg="#2B2B2B")
# load = Image.open("nhandien3.jpg")
# render = ImageTk.PhotoImage(load)
# img =  Label(window, image=render)
# img.place(x=0,y=0)
# Tiêu Đề
lbltitle = Label(window, text="NHẬN DẠNG KHUÔN MẶT GIỐNG NHAU", fg="cyan", font=("Calibri Bold", 30), bg="#2B2B2B")
lbltitle.place(x=140, y=5)
# Nhập Tên
blbten = Label(window, text="Nhập Tên")
blbten.place(x=10, y=100)
txtTen = Entry(window, width=27)
txtTen.place(x=78, y=98, height=25)

# Nhập ID
blbID = Label(window, text="  Nhập ID ")
blbID.place(x=10, y=150)
txtID = Entry(window, width=27)
txtID.place(x=78, y=148, height=25)
# Thông Báo
boxthongbao = LabelFrame(window, text="            Thông Báo            ", width=230, height=219, bd=5,
                         bg="LIGHTBLUE", font=("Calibri Bold", 15), fg="black").place(x=10, y=410)
lblthongbao1 = Label(boxthongbao, font=("Calibri Bold", 20), bg="lightblue", fg="red")
lblthongbao2 = Label(boxthongbao, font=("Calibri Bold", 20), bg="lightblue", fg="red")
lblthongbao3 = Label(boxthongbao, font=("Calibri Bold", 20), bg="lightblue", fg="red")
lblthongbao4 = Label(boxthongbao, font=("Calibri Bold", 20), bg="lightblue", fg="blue")

# Giao Diện Camera
video = cv2.VideoCapture(0)
# load thu vien
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
bw = 0
canvas = Canvas(window, width=638, height=474)
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
# biến count chạy lần đầu khi lấy ảnh
count = 1
# số lượng ảnh hiện có
numberImage = None


########### Sự Kiên $$$$$$$$$$
def update_frame():
    global canvas, photo, bw, check, sampleNum, numberReadTrain, recognizer, userID, count, numberImage
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
            # số ảnh của id hiện có trong dataSet
            if count == 1:
                numberImage = getMaxNumberImage('dataSet', userID)
                count = 2
            if numberImage is None:
                cv2.imwrite('dataSet/User.' + str(userID) + '.' + str(sampleNum) + '.' + '0' + '.jpg',
                            gray[y: y + h, x: x + w])
            # lưu khuôn mặt
            # User.1.1.0.jpg chưa train
            # User.1.1.1.jpg đã train
            else:
                cv2.imwrite('dataSet/User.' + str(userID) + '.' + str(sampleNum + numberImage) + '.' + '0' + '.jpg',
                            gray[y: y + h, x: x + w])
            break
        if sampleNum > 99:
            sampleNum = 0
            check = 0
            count = 1
            numberImage = None
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
            # recognizer.read('E:\\ChuyenDe\\NhanDienKhuonMat\\recoginzer\\trainingData.yml')
            recognizer.read('recoginzer/trainingData.yml')
        for (x, y, w, h) in faces:
            # vẽ ô vuông
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 225, 0), 2)

            # cắt khuôn mặt trên webcam
            roi_gray = gray[y:y + h, x:x + w]

            # nhận diện người này là ai, trả về tham số id và độ chính xác
            ID, confidence = recognizer.predict(roi_gray)
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
    color = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Convert hanh image TK
    photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(color))
    # Show
    canvas.create_image(0, 0, image=photo, anchor=tkinter.NW)
    window.after(15, update_frame)


update_frame()


def thoat():
    exit()


def LayAnh():
    global bw, check, userID
    btbnhandien["state"] = "normal"
    if txtID.get() == "" and userID is None:
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
    bw = 1 - bw
    lblthongbao1.place(x=25, y=430)
    lblthongbao1.configure(text="")
    res2 = ""
    lblthongbao2.place(x=25, y=470)
    lblthongbao2.configure(text=res2)
    res3 = "Đang Lấy Ảnh"
    lblthongbao3.place(x=40, y=510)
    lblthongbao3.configure(text=res3)
    res4 = ""
    lblthongbao4.place(x=45, y=550)
    lblthongbao4.configure(text=res4)


def DocAnh():
    global numberReadTrain, recognizer

    lblthongbao1.place(x=25, y=430)
    lblthongbao1.configure(text="")
    res2 = ""
    lblthongbao2.place(x=25, y=470)
    lblthongbao2.configure(text=res2)
    res3 = "Đang Đọc Ảnh"
    lblthongbao3.place(x=40, y=510)
    lblthongbao3.configure(text=res3)
    res4 = ""
    lblthongbao4.place(x=45, y=550)
    lblthongbao4.configure(text=res4)

    btbnhandien["state"] = "normal"
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
    # xuất thông báo Train thành công
    top = Toplevel()
    my_label = Label(top, text="Train Ảnh Thành Công").pack()
    numberReadTrain = 1


def NhanDien():
    global check
    check = 2
    btbnhandien["state"] = "disable"

    txtID.delete(0, END)
    txtTen.delete(0, END)
    lblthongbao1.place(x=25, y=430)
    lblthongbao1.configure(text="")
    res2 = ""
    lblthongbao2.place(x=25, y=470)
    lblthongbao2.configure(text=res2)
    res3 = "Đang Nhận Diện"
    lblthongbao3.place(x=30, y=510)
    lblthongbao3.configure(text=res3)
    res4 = ""
    lblthongbao4.place(x=45, y=550)
    lblthongbao4.configure(text=res4)


def ThemNhanDien():
    global userID, error
    btbnhandien["state"] = "normal"
    if txtID.get() == "" or txtTen.get() == "":
        messagebox.showerror("Lỗi:", "Bạn chưa nhập ID hoặc Tên!!!")
    else:
        try:
            # bắt lỗi nhập chữ vào ID
            ID = int(txtID.get().strip())
            insertPeople(ID, txtTen.get().strip())
            # bắt lỗi nhập trùng ID đã lưu
            if error != "":
                messagebox.showerror("Lỗi:", error)
            else:
                res = "Thêm Nhận Diện"
                lblthongbao1.place(x=25, y=430)
                lblthongbao1.configure(text=res)
                res2 = "Tên: " + txtTen.get()
                lblthongbao2.place(x=20, y=470)
                lblthongbao2.configure(text=res2)
                res3 = "ID: " + txtID.get()
                lblthongbao3.place(x=20, y=510)
                lblthongbao3.configure(text=res3)
                res4 = "Mời Lấy Ảnh "
                lblthongbao4.place(x=45, y=550)
                lblthongbao4.configure(text=res4)
                userID = txtID.get()

        except ValueError:
            messagebox.showerror("Lỗi:", "ID phải nhập số!")


def BoSungAnh():
    lblthongbao1.place(x=25, y=430)
    lblthongbao1.configure(text="")
    res2 = ""
    lblthongbao2.place(x=25, y=470)
    lblthongbao2.configure(text=res2)
    res3 = "Bổ Sung Ảnh"
    lblthongbao3.place(x=40, y=510)
    lblthongbao3.configure(text=res3)
    res4 = ""
    lblthongbao4.place(x=45, y=550)
    lblthongbao4.configure(text=res4)


def XemDuLieu():
    scrollbar = Scrollbar(window)
    scrollbar.place(x=15, y=440, width=219, height=182)

    # mylist = Listbox(window, yscrollcommand=scrollbar.set, bg="lightblue")
    # Tree View
    tv = ttk.Treeview(window)
    tv['columns'] = ('ID', 'Name')
    tv.column('#0', width=0, stretch=NO)
    tv.column('ID', anchor=CENTER, width=80)
    tv.column('Name', anchor=CENTER, width=80)

    tv.heading('#0', text='', anchor=CENTER)
    tv.heading('ID', text='ID', anchor=CENTER)
    tv.heading('Name', text='Name', anchor=CENTER)
    conn = sqlite3.connect('facebase.db')
    query = "SELECT * FROM people ORDER BY id DESC"
    cursor = conn.execute(query)
    for people in cursor:
        print(people[0], people[1])
        tv.insert(parent='', index=0, text='', values=(people[0], people[1]))
    conn.close()

    tv.place(x=15, y=440, width=219, height=182)
    scrollbar.config(command=tv.yview())
    # mylist.place(x=15, y=440, width=219, height=182)
    # scrollbar.config(command=mylist.yview)


def insertPeople(ID, name):
    global error
    # kết nối sqlite
    conn = sqlite3.connect('facebase.db')
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
    # conn = sqlite3.connect('E:\\ChuyenDe\\NhanDienKhuonMat\\facebase.db')
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


def getMaxNumberImage(path, ID):
    # lấy tất cả đường dẫn ảnh trong "dataSet"
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]

    imageNumber = []

    for imagePath in imagePaths:

        # cắt id
        imageID = int(imagePath.split('\\')[1].split('.')[1])
        if imageID == ID:
            imageNumber.append(int(imagePath.split('\\')[1].split('.')[2]))

    # imageNumber == []
    if not imageNumber:
        return None
    return max(imageNumber)


# Nút Lấy Ảnh
btblayanh = Button(window, text="LẤY ẢNH", bg="orange", fg="black", font=("Calibri Bold", 13), bd=10, command=LayAnh)
btblayanh.place(x=270, y=560, width=110, height=70)
# Nút Bổ Sung Ảnh
btbnhandien = Button(window, text="BỔ SUNG ẢNH", bg="BLue", fg="white", font=("Calibri Bold", 13), bd=10,
                     command=BoSungAnh)
btbnhandien.place(x=50, y=262, width=160, height=60)
# Nút Đọc Ảnh
btbtriananh = Button(window, text="ĐỌC ẢNH", bg="Pink", fg="black", font=("Calibri Bold", 13), bd=10, command=DocAnh)
btbtriananh.place(x=440, y=560, width=115, height=70)
# Nút Nhận Diện
btbnhandien = Button(window, text="NHẬN DIỆN", bg="Yellow", fg="black", font=("Calibri Bold", 13), bd=10,
                     command=NhanDien)
btbnhandien.place(x=620, y=560, width=120, height=70)
# Nút Thêm Nhận Diện
btbnhandien = Button(window, text="THÊM NHÂN DIỆN", bg="BLue", fg="white", font=("Calibri Bold", 13), bd=10,
                     command=ThemNhanDien)
btbnhandien.place(x=50, y=190, height=60)
# Nút Xem Duữ liệu
btbnhandien = Button(window, text="XEM DỮ lIỆU", bg="BLue", fg="white", font=("Calibri Bold", 13), bd=10,
                     command=XemDuLieu)
btbnhandien.place(x=50, y=335, height=60, width=160)
# Nút Thoát
btbthoat = Button(window, text="THOÁT", bg="RED", fg="black", font=("Calibri Bold", 13), bd=10, command=thoat)
btbthoat.place(x=800, y=560, width=90, height=70)

window.mainloop()
