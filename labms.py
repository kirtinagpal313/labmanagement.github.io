from flask import Flask, redirect, request, render_template, session, url_for, flash
from flask_mysqldb import MySQL, MySQLdb
from flask_mail import Mail, Message
from itsdangerous import SignatureExpired
import bcrypt
import uuid


app = Flask(__name__)
app.config['SECRET_KEY'] = 'a really really really really long secret key'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'kirtinagpal313@gmail.com'
app.config['MAIL_DEFAULT_SENDER'] = 'kirtinagpal313@gmail.com'
app.config['MAIL_PASSWORD'] = '17071313'
mymail = Mail(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pup_lab_mgt'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forget_password():
    if request.method == 'GET':
        return render_template("forgot_password.html")
    else:
        myemail = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admin_tb where email=%s", (myemail,))
        register = cur.fetchone()
        if register:
                email = register['email']
                token = uuid.uuid4().hex.upper()
                #print("INSERT INTO admin_tb(mytoken) VALUES(%s) where email=%s", (token, email,))
                sql2 = "INSERT INTO `token_tb`(`token`, `email`) VALUES (%s,%s)"
                val2 = (token, email)
                cur.execute(sql2,val2)
                mysql.connection.commit()

                msg = Message(subject='Password Reset', sender='kirtinagpal313@gmail.com',
                              recipients=[request.form['email']])
                link = url_for('conf_email', token=token, _external=True)
                msg.body = render_template('sentmail.html', token=token, link=link)
                mymail.send(msg)

                flash('Link sent to your Email')
                # print("checking for real")
                return render_template('forgot_password.html', token=token)
        else:

            msg = Message(subject='Password Reset', sender='krowdpoint@gmail.com',
                          recipients=[request.form['email']])
            msg.body = "This email does not exist in our system, " \
                       "if you not the one who entered this mail ignore this message"
            mymail.send(msg)
            flash('Email does not exist or wrong username or password!', 'danger')
            return render_template('forgot_password.html')


@app.route('/conf_email/<token>')
def conf_email(token):
    try:
        my_token = token
        cur = mysql.connection.cursor()
        cur.execute("SELECT email FROM token_tb where token=%s", (my_token,))
        user = cur.fetchone()
        cur.close()
        if len(user) > 0:
           user_email = user['email']
           return render_template("password_reset.html", usermail=user_email)
        else:
           return render_template("index.html")
    except SignatureExpired:
       return '<h1>The token is expired!</h1>'
        # return '<h1>The token works!</h1>'
    return redirect(url_for('index.html'))


@app.route('/password_reset', methods=['GET','POST'])
def password_reset():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        conf_password = request.form["confirm_password"]
        if password == conf_password:
            new_password = request.form['password'].encode('utf-8')
            hash_password = bcrypt.hashpw(new_password, bcrypt.gensalt())
            cur = mysql.connection.cursor()
            cur.execute("UPDATE admin_tb SET password=%s WHERE email=%s", (hash_password, email))
            mysql.connection.commit()
            checkpoint = 'mission'
            return render_template("password_reset.html", checkpoint=checkpoint)
        else:
            checkpoint = 'mission_failed'
            return render_template("password_reset.html", checkpoint=checkpoint)
    return render_template("password_reset.html")


@app.route('/pass_form')
def pass_form():
    return redirect(url_for('password_confirm'))


@app.route('/')
def index():
    cur = mysql.connection.cursor()
    shownotification = 'Show'
    cur.execute("SELECT * FROM notification_tb where status=%s order by id", (shownotification,))
    notification_record = cur.fetchall()
    cur.close()
    test = 'alpha'
    return render_template('index.html', notirv=notification_record, test=test)


@app.route('/admin_panel')
def admin_panel():
    return render_template("admin_panel.html")


"""
@app.route('/register', methods=['GET', 'POST'])   #  /add_admin
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        #sql_query = "INSERT INTO admin_tb(name, email, password) VALUES(%s, %s, %s)", (name, email, hash_password,)
        #print(sql_query)
        cur.execute("INSERT INTO admin_tb(name, email, password) VALUES(%s, %s, %s)", (name, email, hash_password,))
        mysql.connection.commit()
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        return redirect(url_for('login'))    # return redirect(url_for('admin_panel'))
"""


@app.route('/add_admin', methods=['GET', 'POST'])
def add_admin():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO admin_tb(name, email, password) VALUES(%s, %s, %s)", (name, email, hash_password,))
        mysql.connection.commit()
        return redirect(url_for('view_admins'))


@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'GET':
        return render_template("add_student.html")
    else:
        try:
            first_name = request.form['fname']
            last_name = request.form['lname']
            phone_no = request.form['phoneno']
            gender = request.form['gender']
            email = request.form['email']
            password = request.form['password'].encode('utf-8')
            hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
            enrolment_no = request.form['enrolmentno']
            enrolment_date = request.form['enrolmentdate']
            registration_no = request.form['registrationno']
            registration_date = request.form['registrationdate']

            cur = mysql.connection.cursor()
            # sql_query = "INSERT INTO student_tb(fname, lname, phone_no, gender, email, student_password, enrolment_no, enrolment_date, registration_no, registration_date) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (first_name, last_name, phone_no, gender, email, hash_password, enrolment_no, enrolment_date, registration_no, registration_date,)
            # print(sql_query)
            cur.execute("INSERT INTO student_tb(fname, lname, phone_no, gender, email, student_password, "
                        "enrolment_no, enrolment_date, registration_no, registration_date) VALUES(%s, %s, %s, %s, %s, "
                        "%s, %s, %s, %s, %s)", (first_name, last_name, phone_no, gender, email, hash_password,
                                                enrolment_no, enrolment_date, registration_no, registration_date,))
            mysql.connection.commit()
            return redirect(url_for('admin_panel'))
        except AssertionError as msg:
            print(msg)


@app.route('/mark_attandance', methods=['GET', 'POST'])
def mark_attandance():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT fname, lname, email FROM student_tb order by fname")
        admin_record = cur.fetchall()
        cur.close()
        return render_template('mark_attandance.html', markrv=admin_record)
    else:
        name = request.form['name']
        email = request.form['email']
        attDate = request.form['date']
        markAttandance = request.form['attandance_mark']
        leaveType = request.form['leave_type']
        inTime = request.form['in_time']
        outTime = request.form['out_time']

        cur = mysql.connection.cursor()
        # sql_query = "INSERT INTO admin_tb(name, email, password) VALUES(%s, %s, %s)", (name, email, hash_password,)
        # print(sql_query)
        cur.execute("INSERT INTO attandance_tb(student_name, student_email, attandance_date, attandance_mark, "
                    "leave_type, in_time, out_time) VALUES(%s, %s, %s, %s, %s, %s, %s)",
                    (name, email, attDate, markAttandance, leaveType, inTime, outTime,))
        mysql.connection.commit()
        return redirect(url_for('view_attandance'))


@app.route('/mark_leave', methods=['POST'])
def mark_leave():
    name = request.form['name']
    email = request.form['email']
    leaveType = request.form['leave_type']
    remarks = request.form['remarks']
    attDate = request.form['date']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO leave_tb(name, email, leave_type, remarks, date) VALUES(%s, %s, %s, %s, %s)",
                (name, email, leaveType, remarks, attDate,))
    mysql.connection.commit()
    return redirect(url_for('index'))


@app.route('/add_notification', methods=['GET', 'POST'])
def add_notificiation():
    if request.method == 'GET':
        return render_template("add_notifications.html")
    else:
        notfication_title = request.form['title']
        notification_details = request.form['details']
        notification_status = request.form['notification_status']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO notification_tb(title, details, status) VALUES(%s, %s, %s)",
                    (notfication_title, notification_details, notification_status,))
        mysql.connection.commit()
        return redirect(url_for('view_notifications'))


@app.route('/add_purchase', methods=['GET', 'POST'])
def add_purchase():
    if request.method == 'GET':
        return render_template("add_purchase.html")
    else:
        item_name = request.form['item_name']
        vendor_name = request.form['vendor_name']
        invoice_no = request.form['invoice_no']
        amount = request.form['amount']
        purchase_date = request.form['purchase_date']
        diary_number = request.form['diary_number']
        paid_to = request.form['paid_to']
        payment_mode = request.form['payment_mode']
        # f = request.files['file']
        # user_filename = f.filename
        # ext = user_filename.split('.')[-1]
        # filename = secure_filename('{}.{}'.format(diary_number, ext))
        # pathname = os.path.join(app.config['UPLOADS'], filename)
        # f.save(pathname)
        # f.save(secure_filename(f.filename))
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO purchase_tb(item_name, vendor_name, invoice_no, amount, purchase_date, diary_number, "
                    "paid_to, payment_mode) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
                    (item_name, vendor_name, invoice_no, amount, purchase_date, diary_number, paid_to, payment_mode,))

        mysql.connection.commit()
        return redirect(url_for('view_purchase'))


@app.route('/view_admins')
def view_admins():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM admin_tb order by id")
    admin_record = cur.fetchall()
    cur.close()
    return render_template('view_admins.html', rv=admin_record)


@app.route('/search_admin', methods=['GET', 'POST'])
def search_admin():
    if request.method == 'POST':
        name = request.form['search']
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name, email FROM admin_tb where name LIKE %s OR email LIKE %s", (name, name))
        result = cur.fetchall()
        if len(result) == 0 and (name == 'all'):
            cur.execute("SELECT id, name, email from admin_tb order by id")
            result = cur.fetchall()
        cur.close()
        return render_template('search_admin.html', myrv=result)
    return render_template("search_admin.html")


@app.route('/view_students')
def view_students():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM student_tb order by id")
    student_record = cur.fetchall()
    cur.close()
    return render_template('view_students.html', myrv=student_record)


@app.route('/student_search', methods=['GET', 'POST'])
def student_search():
    if request.method == 'POST':
        name = request.form['search']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM student_tb where fname LIKE %s OR email LIKE %s", (name, name))
        result = cur.fetchall()
        if len(result) == 0 and (name == 'all'):
            cur.execute("SELECT * from student_tb order by id")
            result = cur.fetchall()
        cur.close()
        return render_template('student_search.html', myrv=result)
    return render_template("student_search.html")


@app.route('/view_attandance')
def view_attandance():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM attandance_tb order by id")
    attandance_record = cur.fetchall()
    cur.close()
    return render_template('view_attandance.html', attandancerv=attandance_record)


@app.route('/leave_applications')
def leave_applications():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM leave_tb order by id")
    leave_record = cur.fetchall()
    cur.close()
    return render_template('leave_applications.html', attandancerv=leave_record)


@app.route('/view_notifications')
def view_notifications():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM notification_tb order by id")
    notification_record = cur.fetchall()
    cur.close()
    return render_template('view_notifications.html', notirv=notification_record)


@app.route('/view_purchase')
def view_purchase():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM purchase_tb order by id")
    purchase_record = cur.fetchall()
    cur.close()
    return render_template('view_purchase.html', purchaserv=purchase_record)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM admin_tb WHERE email=%s", (email,))
        user = curl.fetchone()
        curl.close()

        if len(user) > 0:
            if bcrypt.hashpw(password, user['password'].encode('utf-8')) == user["password"].encode('utf-8'):
                session['name'] = user['name']
                session['email'] = user['email']
                return render_template("admin_panel.html")
            else:
                return render_template("index.html")
        else:
            return "Error user not found!!!"
    else:
        return render_template("login.html")


# Update Admin Records with Query String
@app.route('/update_admin/<string:id_data>', methods=['GET', 'POST'])
def update(id_data):
    if request.method == "GET" and id_data != 'ram':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admin_tb where id=%s", (id_data,))
        admin_record = cur.fetchall()
        cur.close()
        return render_template('update_admin.html', adminrv=admin_record)
    else:
        my_id = request.form['id']
        name = request.form['name']
        email = request.form['email']
        cur = mysql.connection.cursor()
        new_id = int(my_id)
        cur.execute("UPDATE admin_tb SET name=%s, email=%s WHERE id=%s", (name, email, new_id))
        mysql.connection.commit()
        return redirect(url_for('view_admins'))


@app.route('/delete_admin/<string:id_data>', methods=['GET', 'POST'])
def delete_admin(id_data):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("delete from admin_tb where id=%s", (id_data,))
        mysql.connection.commit()
        return render_template("admin_panel.html")
    else:
        return render_template("view_admins.html")


@app.route('/update_student/<string:id_data>', methods=['GET', 'POST'])
def update_student(id_data):
    if request.method == "GET" and id_data != 'ram':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM student_tb where id=%s", (id_data,))
        student_record = cur.fetchall()
        cur.close()
        val = 'king'
        return render_template('update_student.html', studentrv=student_record, val=val)
    else:
        student_id = request.form['id']
        first_name = request.form['fname']
        last_name = request.form['lname']
        phone_no = request.form['phoneno']
        gender = request.form['gender']
        email = request.form['email']
        enrolment_no = request.form['enrolmentno']
        enrolment_date = request.form['enrolmentdate']
        registration_no = request.form['registrationno']
        registration_date = request.form['registrationdate']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE student_tb SET fname=%s, lname=%s, phone_no=%s, gender=%s, email=%s, enrolment_no=%s, "
                    "enrolment_date=%s, registration_no=%s, registration_date=%s WHERE id=%s", (first_name, last_name,
                                                                                                phone_no, gender, email,
                                                                                                enrolment_no,
                                                                                                enrolment_date,
                                                                                                registration_no,
                                                                                                registration_date,
                                                                                                student_id))
        mysql.connection.commit()
        return redirect(url_for('admin_panel'))


@app.route('/delete_student/<string:id_data>', methods=['GET', 'POST'])
def delete_student(id_data):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("delete from student_tb where id=%s", (id_data,))
        mysql.connection.commit()
        return redirect("../view_students")
    else:
        return render_template("view_students.html")


@app.route('/update_notification/<string:id_data>', methods=['GET', 'POST'])
def update_notification(id_data):
    if request.method == "GET" and id_data != 'ram':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM notification_tb where id=%s", (id_data,))
        notification_record = cur.fetchall()
        cur.close()
        val = 'king'
        return render_template('update_notification.html', notificationrv=notification_record, val=val)
    else:
        notification_id = request.form["id"]
        notfication_title = request.form['title']
        notification_details = request.form['details']
        notification_status = request.form['notification_status']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE notification_tb SET title=%s, details=%s, status=%s WHERE id=%s",
                    (notfication_title, notification_details, notification_status, notification_id))
        mysql.connection.commit()
        return redirect(url_for('view_notifications'))


@app.route('/delete_notification/<string:id_data>', methods=['GET', 'POST'])
def delete_notification(id_data):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("delete from notification_tb where id=%s", (id_data,))
        mysql.connection.commit()
        return redirect("../view_notifications")
    else:
        return render_template("view_notifications.html")


@app.route('/update_purchase/<string:id_data>', methods=['GET', 'POST'])
def update_purchase(id_data):
    if request.method == "GET" and id_data != 'ram':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM purchase_tb where id=%s", (id_data,))
        purchase_record = cur.fetchall()
        cur.close()
        val = 'king'
        return render_template('update_purchase.html', purchaserv=purchase_record, val=val)
    else:
        id = request.form['id']
        item_name = request.form['item_name']
        vendor_name = request.form['vendor_name']
        invoice_no = request.form['invoice_no']
        amount = request.form['amount']
        purchase_date = request.form['purchase_date']
        diary_number = request.form['diary_number']
        paid_to = request.form['paid_to']
        payment_mode = request.form['payment_mode']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE purchase_tb SET item_name=%s, vendor_name=%s, invoice_no=%s, amount=%s, purchase_date=%s, "
                    "diary_number=%s, paid_to=%s, payment_mode=%s WHERE id=%s", (item_name, vendor_name, invoice_no,
                                                                                 amount, purchase_date,
                                                                                 diary_number, paid_to,
                                                                                 payment_mode, id))
        mysql.connection.commit()
        return redirect(url_for('view_purchase'))


@app.route('/delete_purchase/<string:id_data>', methods=['GET', 'POST'])
def delete_purchase(id_data):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("delete from purchase_tb where id=%s", (id_data,))
        mysql.connection.commit()
        return redirect("../view_purchase")
    else:
        return render_template("view_purchase.html")


@app.route('/update_attandance/<string:id_data>', methods=['GET', 'POST'])
def update_attandance(id_data):
    if request.method == "GET" and id_data != 'ram':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM attandance_tb where id=%s", (id_data,))
        attandance_record = cur.fetchall()
        cur.close()
        val1 = 'king'
        return render_template('update_attandance.html', attandancerv=attandance_record, val=val1)
    else:
        attandance_id = request.form['id']
        name = request.form['name']
        email = request.form['email']
        attDate = request.form['date']
        markAttandance = request.form['attandance_mark']
        leaveType = request.form['leave_type']
        inTime = request.form['in_time']
        outTime = request.form['out_time']

        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE attandance_tb SET student_name=%s, student_email=%s, attandance_date=%s, attandance_mark=%s, leave_type=%s, in_time=%s, out_time=%s WHERE id=%s",
            (name, email, attDate, markAttandance, leaveType, inTime, outTime, attandance_id))
        mysql.connection.commit()
        return redirect(url_for('view_attandance'))


@app.route('/delete_attandance/<string:id_data>', methods=['GET', 'POST'])
def delete_attandance(id_data):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("delete from attandance_tb where id=%s", (id_data,))
        mysql.connection.commit()
        return redirect("../view_attandance")
    else:
        return render_template("view_attandance.html")


@app.route('/logout')
def logout():
    session.clear()
    return render_template("index.html")


if __name__ == '__main__':
    app.secret_key = '^A%DJAJU^JJ123'
    app.run(debug=True)
