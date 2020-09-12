from flask import Flask, render_template, request, session, url_for, redirect, jsonify
import pymysql
import csv
#================================

import numpy as np

from app import class_obt

app = Flask(__name__)
app.secret_key = 'random string'


#Database Connection
def dbConnection():
    connection = pymysql.connect(host="localhost", user="root", password="", database="heartdisease")
    return connection


#close DB connection
def dbClose():
    dbConnection().close()
    return



@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=["GET","POST"])
def login():
    msg = ''
    if request.method == "POST":
        # session.pop('user',None)
        mobno = request.form.get("mobno")
        password = request.form.get("pas")
        # print(mobno+password)
        con = dbConnection()
        cursor = con.cursor()
        result_count = cursor.execute('SELECT * FROM userdetails WHERE mobile = %s AND password = %s',
                                      (mobno, password))
        if result_count > 0:
            print(result_count)
            session['user'] = mobno
            #return redirect(url_for('home'))
            return jsonify(dict(redirect='home'))
        else:
            print(result_count)
            msg = 'Incorrect username/password!'
            return msg
    return render_template('login.html')



@app.route('/register', methods=["GET","POST"])
def register():
    print("register")
    if request.method == "POST":
        try:
            name = request.form.get("name")
            address = request.form.get("address")
            mailid = request.form.get("mailid")
            mobile = request.form.get("mobile")
            pass1 = request.form.get("pass1")

            con = dbConnection()
            cursor = con.cursor()
            cursor.execute('SELECT * FROM userdetails WHERE mobile = %s', (mobile))
            res = cursor.fetchone()
            if not res:
                sql = "INSERT INTO userdetails (name, address, email, mobile, password) VALUES (%s, %s, %s, %s, %s)"
                val = (name, address, mailid, mobile, pass1)
                cursor.execute(sql, val)
                con.commit()
                status= "success"
                print(status)
                #return redirect(url_for('index'))
                return jsonify(dict(redirect='login'))
            else:
                status = "Already Registered"
            return status
        except:
            print("Exception occured at user registration")
            return redirect(url_for('index'))
        finally:
            dbClose()
    return render_template('register.html')


@app.route('/home')
def home():
    if 'user' in session:
        return render_template('home.html',user=session['user'])
    return redirect(url_for('index'))


@app.route('/prediction', methods=["GET","POST"])
def prediction():
    if 'user' in session:
        if request.method == "POST":
            age = request.form.get("age")
            gender = request.form.get("gender")
            cp = request.form.get("cp")
            trestbps = request.form.get("trestbps")
            chol = request.form.get("chol")
            fbs = request.form.get("fbs")
            restecg = request.form.get("restecg")
            thalach = request.form.get("thalach")
            exang = request.form.get("exang")
            slope = request.form.get("slope")
            oldpik = request.form.get("oldpik")
            ca = request.form.get("ca")
            thal = request.form.get("thal")
            target = request.form.get("target")
            filename = 'kmeans_model.sav'
            test_list = []
            valofall = age + ',' + gender + ',' + cp + ',' + trestbps + ',' + chol + ',' + fbs + ',' + restecg + ',' + thalach + ',' + exang + ',' + slope + ',' + oldpik + ',' + ca + ',' + thal
            print(valofall)
            valofsplit = valofall.split(",")
            print(valofsplit)
            for i in range(0, len(valofsplit)):
                test_list.append(int(valofsplit[i]))
                # print(test_list)
            # X_std = scaler.fit_transform(X)
            print(test_list)
            print(np.array([test_list]))
            loaded_model = np.pickle.load(open(filename, 'rb'))
            y_gotdata = loaded_model.predict(np.array([test_list]))
            print(y_gotdata[0])
            print("predicted heart disease is " + class_obt.get(y_gotdata[0]))
            k_meansresult = class_obt.get(y_gotdata[0])
            print('kmeans')
            print(k_meansresult)
            #
            # loaded_model1 = pickle.load(open(filename1, 'rb'))
            # y_gotdata1 = loaded_model1.predict(np.array([test_list]))
            # print(y_gotdata1[0])
            #
            # #rfresult = rf.predict([test_list])
            # rfresult = class_obt.get(y_gotdata1[0])
            # print('random forest')
            # print(rfresult)
            return render_template('predictResult.html', user=session['user'])
        return render_template('prediction.html', user=session['user'],k_meansresult=session['k_meansresult'])
    return redirect(url_for('index'))


@app.route('/appointment', methods=["GET","POST"])
def appointment():
    if 'user' in session:
        con = dbConnection()
        cursor1 = con.cursor()
        cursor1.execute('SELECT * FROM doctordetails')
        dr_res = cursor1.fetchall()

        if request.method == "POST":
            patient_name = request.form.get("patient_name")
            mobile_number = request.form.get("mobile_number")
            email = request.form.get("email")
            address = request.form.get("address")
            doctorname = request.form.get("doctorname")
            gender = request.form.get("gender")
            dob = request.form.get("dob")
            time = request.form.get("time")

            #con = dbConnection()
            cursor = con.cursor()
            cursor.execute('SELECT * FROM appointment WHERE name = %s and mobile = %s and mailid = %s and doctor = %s and appt_time = %s ', (patient_name,mobile_number,email,doctorname,time))
            res = cursor.fetchone()
            if not res:
                q = "SELECT * FROM doctordetails where doctorname =  %s"
                cursor.execute(q, (doctorname))
                res1  = cursor.fetchone()
                drmailid = res1[2]
                print(drmailid)

                sql = "INSERT INTO appointment(name, gender, mobile, dob, address, mailid, appt_time, doctor) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                val = (patient_name, gender, mobile_number, dob, address, email, time, doctorname)
                cursor.execute(sql, val)
                con.commit()

                status = "success"
                print(status)
                # return redirect(url_for('index'))
                return jsonify(dict(redirect='appointment'))
            else:
                status = "Already appointed"
                return status
        return render_template('appointment.html',user=session['user'],dr_res=dr_res)
    return redirect(url_for('index'))


@app.route('/doctors')
def doctors():
    if 'user' in session:
        return render_template('doctors.html',user=session['user'])
    return redirect(url_for('index'))


@app.route('/dataset')
def dataset():
    if 'user' in session:
        con = dbConnection()
        cursor = con.cursor()
        cursor.execute('SELECT * FROM dataset')
        results = cursor.fetchall()
        return render_template('dataset.html',user=session['user'], data=results)
    return redirect(url_for('index'))


@app.route('/video')
def video():
    if 'user' in session:
        return render_template('video.html',user=session['user'])
    return redirect(url_for('index'))


#logout code
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run("0.0.0.0")
    #app.run()
