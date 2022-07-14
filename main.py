from crypt import methods
from flask import Flask, request
from flask_mysqldb import MySQL
import json, datetime

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mig_absensi'
 
mysql = MySQL(app)


@app.route("/login", methods = ['POST'])
def login():
    req = request.json
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT * FROM user WHERE username = %s ''', (req['username']))
    user = cursor.fetch()
    mysql.connection.commit()

    cursor.close()
    data = {
        "status": "logged in"
    }
    
    return data

@app.route("/register", methods = ['POST'])
def register():
    req = request.json
    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO user (name, username, password) VALUES(%s,%s,%s) ''', (req['name'],req['username'],req['password']))
    mysql.connection.commit()
    cursor.close()
    data = {
        "status": "Regiter success"
    }
    return data

@app.route("/logout", methods = ['GET'])
def logout():
    data = {
        "status": "logged in"
    }
    return data

@app.route("/checkin", methods = ['POST'])
def check_in():
    data = {
        "status": "logged in"
    }
    return data

@app.route("/checkout", methods = ['POST'])
def check_out():
    data = {
        "status": "logged in"
    }
    return data

@app.route("/activities", methods = ['GET'])
def activities():
    data = {
        "status": "logged in"
    }
    return data

@app.route("/myactivity", methods = ['GET'])
def my_activity():
    data = {
        "status": "logged in"
    }
    return data

@app.route("/myactivity/add", methods = ['POST'])
def add_activity():
    data = {
        "status": "logged in"
    }
    return data

@app.route("/myactivity/update", methods = ['POST'])
def update_activity():
    data = {
        "status": "logged in"
    }
    return data

@app.route("/myactivity/delete", methods = ['POST'])
def delete_activity():
    data = {
        "status": "logged in"
    }
    return data

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')