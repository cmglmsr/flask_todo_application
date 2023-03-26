from datetime import datetime
import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__) 

app.secret_key = 'abcdefgh'
  
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'cs353hw4db'
  
mysql = MySQL(app)  

@app.route('/')

@app.route('/login', methods =['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = % s AND password = % s', (username, password, ))
        user = cursor.fetchone()
        if user:              
            session['loggedin'] = True
            session['userid'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            message = 'Logged in successfully!'
            return redirect(url_for('tasks'))
        else:
            message = 'Please enter correct email / password !'
    return render_template('login.html', message = message)


@app.route('/register', methods =['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            message = 'Choose a different username!'
        elif not username or not password or not email:
            message = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO User (id, username, email, password) VALUES (NULL, % s, % s, % s)', (username, email, password,))
            mysql.connection.commit()
            message = 'User successfully created!'

    elif request.method == 'POST':
        message = 'Please fill all the fields!'
    return render_template('register.html', message = message)

@app.route('/tasks', methods =['GET'])
def tasks():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Task ORDER BY deadline ASC')
    tasks_list = cursor.fetchall()
    return render_template('tasks.html', tasks_list=tasks_list)

@app.route('/tasks', methods=['POST'])
def add_task():
    # add form checks
    # change null values of tasks
    task_title = request.form.get("name")
    task_description = request.form.get("description")
    task_status = "Todo"
    task_deadline = request.form.get("deadline")
    task_creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    task_done_time = None
    task_user_id = int(session['userid'])
    task_type = request.form.get("tasktypes")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO Task (title, description, status, deadline, creation_time, done_time, user_id, task_type) VALUES ('{}', '{}','{}', '{}', '{}', NULL, {}, '{}')".format(task_title, task_description, task_status, task_deadline, task_creation_time, task_user_id, task_type))
    mysql.connection.commit()
    cursor.execute('SELECT * FROM Task ORDER BY deadline ASC')
    tasks_list = cursor.fetchall()
    return render_template('tasks.html', tasks_list=tasks_list)

@app.route('/tasks/delete', methods=['POST'])
def del_task():
    task_id  = request.form.get("task_id")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM Task WHERE id={}".format(task_id))
    mysql.connection.commit()
    cursor.execute('SELECT * FROM Task ORDER BY deadline ASC')
    tasks_list = cursor.fetchall()
    return redirect(url_for('tasks'))

@app.route('/tasks/edit', methods=['POST'])
def edit_task():
    task_id  = request.form.get("task_id")
    task_title = request.form.get("name")
    task_description = request.form.get("description")
    task_deadline = request.form.get("deadline")
    task_type = request.form.get("tasktypes")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if task_title:
        cursor.execute("UPDATE Task SET title = '{}' WHERE id={}".format(task_title,task_id))
    if task_description:
        cursor.execute("UPDATE Task SET description = '{}' WHERE id={}".format(task_description,task_id))
    if task_deadline:
        cursor.execute("UPDATE Task SET deadline = '{}' WHERE id={}".format(task_deadline,task_id))
    if task_type:
        cursor.execute("UPDATE Task SET task_type = '{}' WHERE id={}".format(task_type,task_id))
    mysql.connection.commit()
    return redirect(url_for('tasks'))

@app.route('/tasks/edit', methods=['GET'])
def edit_task_get():
    task_id  = request.args.get("task_id")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT title FROM Task WHERE id={}".format(task_id))
    name = cursor.fetchone()["title"]
    return render_template('edittask.html', task_name=name, task_id=task_id)

@app.route('/tasks/done', methods=['POST'])
def done_task():
    task_id  = request.form.get("task_id")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT status FROM Task WHERE id={}".format(task_id))
    is_done = cursor.fetchone()["status"]
    if is_done == "Done":
        cursor.execute("UPDATE Task SET status = 'Todo' WHERE id={}".format(task_id))
        cursor.execute("UPDATE Task SET done_time = NULL WHERE id={}".format(task_id))
    else:
        cursor.execute("UPDATE Task SET status = 'Done' WHERE id={}".format(task_id))
        cursor.execute("UPDATE Task SET done_time = '{}' WHERE id={}".format(datetime.now(),task_id))
    mysql.connection.commit()
    return redirect(url_for('tasks'))

@app.route('/analysis', methods =['GET', 'POST'])
def analysis():
    return "Analysis page"


"""
TODO
1 - show the completed tasks separately in main page, sorted by their completion time
2 - make tasks special to users
3 - analysis page
"""

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
