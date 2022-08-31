import datetime
import re
from flask import Flask, request, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'mig_absensi_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mig_absensi'
 
mysql = MySQL(app)
bcrypt = Bcrypt(app)

@app.route("/login", methods = ['POST'])
def login():
    req = request.json
    cursor = mysql.connection.cursor()
    # Get user
    cursor.execute(''' SELECT * FROM user WHERE username = '%s' ''' % (req['username']))
    user = cursor.fetchone()
    mysql.connection.commit()
    cursor.close()
    print(user)
    # Validate password
    if not user or not bcrypt.check_password_hash(user[3], req['password']):
        data = {
            "status": "Username or password wrong"
        }
        return data

    # Set session
    session['user'] = {
        "id": user[0],
        "name": user[1],
        "username": user[2]
    }

    print(session)
    data = {
        "status": "logged in"
    }
    return data

@app.route("/register", methods = ['POST'])
def register():
    req = request.json
    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO user (name, username, password) VALUES(%s,%s,%s) ''', (req['name'],req['username'],bcrypt.generate_password_hash(req['password'])))
    mysql.connection.commit()
    cursor.close()
    data = {
        "status": "Register success"
    }
    return data

@app.route("/logout", methods = ['GET','POST'])
def logout():
    session['user'] = None
    data = {
        "status": "You're logged out!"
    }
    return data

@app.route("/checkin", methods = ['GET','POST'])
def check_in():
    if session.get('user'):
        cursor = mysql.connection.cursor()
        # Get check in by user today
        cursor.execute(''' SELECT * FROM absensi WHERE id_user = '%d' AND SUBSTR(checkin_time,1,10) = '%s' ''' % (session['user']['id'], datetime.date.today()))
        absen = cursor.fetchone()
        if absen:
            data = {
                "status": "You're already checked in!"
            }
            return data
        cursor.execute(''' INSERT INTO absensi (id_user, checkin_time) VALUES(%s,%s) ''', (session['user']['id'],datetime.datetime.now()))
        mysql.connection.commit()
        cursor.close()
        data = {
            "status": "You're success check in!"
        }
        return data
    else:
        data = {
            "status": "You're not logged in!"
        }
        return data

@app.route("/checkout", methods = ['GET','POST'])
def check_out():
    if session.get('user'):
        cursor = mysql.connection.cursor()
        # Get check in by user today
        cursor.execute(''' SELECT * FROM absensi WHERE id_user = '%d' AND SUBSTR(checkin_time,1,10) = '%s' ''' % (session['user']['id'], datetime.date.today()))
        absen = cursor.fetchone()
        if not absen:
            data = {
                "status": "You're not checked in yet!"
            }
            return data

        if absen[3]:
            data = {
                "status": "You're already checked out!"
            }
            return data

        cursor.execute(''' UPDATE absensi SET checkout_time = '%s' WHERE id_user = %s AND SUBSTR(checkin_time,1,10) = '%s' ''' % (datetime.datetime.now(), session['user']['id'], datetime.date.today()))
        mysql.connection.commit()
        cursor.close()
        data = {
            "status": "You're success check out!"
        }
        return data

    else:
        data = {
            "status": "You're not logged in!"
        }
        return data

@app.route("/attendances", methods = ['GET'])
def attendances():
    if session.get('user'):
        req = request.values
        cursor = mysql.connection.cursor()
        if req.get('date'):
            cursor.execute(''' SELECT a.*, u.name FROM absensi a LEFT JOIN user u ON(a.id_user=u.id) WHERE SUBSTR(checkin_time,1,10) = '%s' ''' % (req.get('date')))
        else:
            cursor.execute(''' SELECT a.*, u.name FROM absensi a LEFT JOIN user u ON(a.id_user=u.id) ''' )

        attendances = cursor.fetchall()
        print(attendances)
        listAttendance = {
            'attendances': []
        }
        for x in attendances:
            attendance = {
                'id': x[0],
                'name': x[4],
                'check_in': x[2],
                'check_out': x[3]
            }
            listAttendance['attendances'].append(attendance)

        print(listAttendance)
        mysql.connection.commit()
        cursor.close()
        return listAttendance
        
    else:
        data = {
            "status": "You're not logged in!"
        }
        return data
        
@app.route("/activities", methods = ['GET'])
def activities():
    if session.get('user'):
        req = request.values
        cursor = mysql.connection.cursor()
        if req.get('date'):
            cursor.execute(''' SELECT a.*, u.name FROM activity a LEFT JOIN user u ON(a.id_user=u.id) WHERE SUBSTR(published_date,1,10) = '%s' ''' % (req.get('date')))
        else:
            cursor.execute(''' SELECT a.*, u.name FROM activity a LEFT JOIN user u ON(a.id_user=u.id) ''')

        activities = cursor.fetchall()
        print(activities)
        listActivity = {
            'activities': []
        }
        for x in activities:
            activity = {
                'id': x[0],
                'name': x[4],
                'activity': x[2]
            }
            listActivity['activities'].append(activity)

        print(listActivity)
        mysql.connection.commit()
        cursor.close()
        return listActivity
        
    else:
        data = {
            "status": "You're not logged in!"
        }
        return data

@app.route("/myactivity", methods = ['GET'])
def my_activity():
    if session.get('user'):
        req = request.values
        cursor = mysql.connection.cursor()
        cursor.execute(''' SELECT a.*, u.name FROM activity a LEFT JOIN user u ON(a.id_user=u.id) ''')
        activities = cursor.fetchall()
        print(activities)
        listActivity = {
            'activities': []
        }
        for x in activities:
            activity = {
                'id': x[0],
                'activity': x[2],
                'date': x[3]
            }
            listActivity['activities'].append(activity)

        print(listActivity)
        mysql.connection.commit()
        cursor.close()
        return listActivity
        
    else:
        data = {
            "status": "You're not logged in!"
        }
        return data

@app.route("/myactivity/add", methods = ['POST'])
def add_activity():
    if session.get('user'):
        cursor = mysql.connection.cursor()
        cursor.execute(''' SELECT * FROM absensi WHERE id_user = %d AND SUBSTR(checkin_time,1,10) = '%s' ''' % (session['user']['id'], datetime.date.today()))
        attendance = cursor.fetchone()
        if not attendance:
            data = {
                "status": "You're not check in yet!"
            }
            return data

        req = request.json
        if req['activity'] == '':
            data = {
                "status": "Activity cannot be empty!"
            }
            return data

        cursor.execute(''' INSERT INTO activity (id_user, activity, published_date) VALUES(%s,%s,%s) ''', (session['user']['id'], req['activity'], datetime.datetime.now()))
        mysql.connection.commit()
        cursor.close()
        data = {
            "status": "You're activity have been added!"
        }
        return data
    else:
        data = {
            "status": "You're not logged in!"
        }
        return data

@app.route("/myactivity/update", methods = ['POST'])
def update_activity():
    if session.get('user'):
        cursor = mysql.connection.cursor()
        cursor.execute(''' SELECT * FROM absensi WHERE id_user = %d AND SUBSTR(checkin_time,1,10) = '%s' ''' % (session['user']['id'], datetime.date.today()))
        attendance = cursor.fetchone()
        if not attendance:
            data = {
                "status": "You're not check in yet!"
            }
            return data

        req = request.json
        
        cursor.execute(''' SELECT * FROM activity WHERE id_user = %d AND id = %d ''' % (session['user']['id'], req['id']))
        activity = cursor.fetchone()
        if not activity:
            data = {
                "status": "Activity not found!"
            }
            return data

        try:
            if not req['id']:
                data = {
                    "status": "Activity id is required!"
                }
                return data

            if req['activity'] == '':
                data = {
                    "status": "Activity cannot be empty!"
                }
                return data

            cursor.execute(''' UPDATE activity SET activity = '%s' WHERE id_user = %d AND id = %d ''' % (req['activity'], session['user']['id'], req['id']))
        except Exception as e:
            data = {
                "status": str(e)
            }
            return data

        mysql.connection.commit()
        cursor.close()
        data = {
            "status": "You're activity have been updated!"
        }
        return data
    else:
        data = {
            "status": "You're not logged in!"
        }
        return data

@app.route("/myactivity/delete", methods = ['POST'])
def delete_activity():
    if session.get('user'):
        cursor = mysql.connection.cursor()
        cursor.execute(''' SELECT * FROM absensi WHERE id_user = %d AND SUBSTR(checkin_time,1,10) = '%s' ''' % (session['user']['id'], datetime.date.today()))
        attendance = cursor.fetchone()
        if not attendance:
            data = {
                "status": "You're not check in yet!"
            }
            return data

        req = request.json
        
        cursor.execute(''' SELECT * FROM activity WHERE id_user = %d AND id = %d ''' % (session['user']['id'], req['id']))
        activity = cursor.fetchone()
        if not activity:
            data = {
                "status": "Activity not found!"
            }
            return data

        try:
            if not req['id']:
                data = {
                    "status": "Activity id is required!"
                }
                return data

            cursor.execute(''' DELETE FROM activity WHERE id_user = %d AND id = %d ''' % (session['user']['id'], req['id']))
        except Exception as e:
            data = {
                "status": str(e)
            }
            return data

        mysql.connection.commit()
        cursor.close()
        data = {
            "status": "You're activity have been deleted!"
        }
        return data
    else:
        data = {
            "status": "You're not logged in!"
        }
        return data

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')