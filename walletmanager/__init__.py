from flask import Flask , render_template , request ,redirect ,url_for,session,jsonify
from flaskext.mysql import MySQL
import datetime
import json
from passlib.hash import sha256_crypt
 
# connecting to sql
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'ahmed'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'walletmanage'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.secret_key="qwerty"
mysql = MySQL(app)


@app.route('/login' ,methods=['GET', 'POST'])
def login():
    conn=mysql.connect()
    cur=conn.cursor()
    error = None
    if request.method == 'POST':
            password=request.form['pass']
            username=request.form['user']
            en_password = sha256_crypt.encrypt(password)
            cur.execute('''SELECT * FROM login WHERE username=%s''',(username))
            data=cur.fetchone()
            check=sha256_crypt.verify(password,data[1])
            if data is None or check is False:
                error="invalid username or password"
                return render_template('login.html',error=error)
            else:
                session['user']=username
                session['pass']=password
                return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/home' , methods=['GET' , 'POST'])
def home():
    balance=0
    conn=mysql.connect()
    cur=conn.cursor()
    cur.execute('''SELECT * FROM balance WHERE username=%s''',(session['user']))
    data=cur.fetchone()
    if data is None:
        if request.method=="POST":
            balance=request.form.get('bal')
            cur.execute('''INSERT INTO balance VALUES(%s,%s )''',
                          (session['user'],balance))
            conn.commit()
            session['bal']=balance
    else:
        balance=data[1]
        session['bal']=balance
    cur.execute('''SELECT splituser,splitamount FROM splits WHERE user=%s''',(session['user']))
    data1=cur.fetchall()
    return render_template('home.html',balance=balance,data=data1)

@app.route('/addexp', methods=['GET','POST'])
def addexp():
    conn=mysql.connect()
    cur=conn.cursor()
    splituser=request.form.get('splituser')
    if request.method=="POST" and splituser is None:    
        expense=request.form.get('amount')
        title=request.form.get('title')
        des=request.form.get('des')
        if expense is None:
            expense=0
        curr_bal=int(session['bal'])-int(expense)
        if title:
            cur.execute('''INSERT INTO exp_details VALUES(%s,%s,%s,%s)''',(session['user'],title,des,expense))
            conn.commit()
        cur.execute('''UPDATE balance SET balance=%s WHERE username=%s''',(curr_bal,session['user']))
        conn.commit()
    if request.method=="POST":
        splituser=request.form.get('splituser')
        amt=request.form.get('splitamt')
        if splituser:
            cur.execute('''INSERT INTO splits VALUES(%s,%s,%s)''' , (session['user'],splituser,amt))
            conn.commit()    
    return render_template('addexp.html')

@app.route('/delexp',methods=['GET','POST'])
def delexp():
    conn=mysql.connect()
    cur=conn.cursor()
    title=request.form.get('title')
    cur.execute('''DELETE FROM exp_details WHERE username=%s AND title=%s''',(session['user'],title))
    conn.commit()
    cur.execute('''SELECT * FROM exp_details WHERE username=%s''',(session['user']))
    data=cur.fetchall()
    if data is None:
        data="no expenses yet!!"
    return render_template('delexp.html' , data=data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/viewexp')
def viewexp():
    conn=mysql.connect()
    cur=conn.cursor()
    cur.execute('''SELECT * FROM exp_details WHERE username=%s''',(session['user']))
    data=cur.fetchall()
    return render_template('viewexp.html',data=data)

@app.route('/register' , methods=['GET','POST'])
def register():
    conn=mysql.connect()
    cur=conn.cursor()
    error = None
    

    if request.method=="POST":
        if request.form['pass'] != request.form['passc']:
            error="passwords doesn't match"
        else:
            password=request.form['pass']
            username=request.form['user']
            en_password = sha256_crypt.encrypt(password)
            cur.execute('''INSERT INTO login VALUES (%s,%s)''',(username,en_password))
            conn.commit()
            
            msg="user created succefully.Please login to use.."
            return render_template("register.html",msg=msg)

    return render_template("register.html",error=error)    


@app.route('/settle' , methods=['GET','POST'])
def settle():
    msg=""
    conn=mysql.connect()
    cur=conn.cursor()
    cur.execute('''SELECT user,splitamount FROM splits WHERE splituser=%s''',(session['user']))
    data=cur.fetchall()
    if request.method=="POST":
        setuser=request.form.get('setuser')
        amount=request.form.get('amount')
        cur.execute('''SELECT balance FROM balance WHERE username=%s''',(setuser))
        bal_data=cur.fetchone()
        oldbal=bal_data[0]
        newbal=oldbal+int(amount)
        cur.execute('''SELECT balance FROM balance WHERE username=%s''',(session['user']))
        usr_bal=cur.fetchone()
        usrbal=usr_bal[0]-int(amount)
        msg="amount settled"
        cur.execute('''UPDATE balance SET balance=%s WHERE username=%s''',(newbal,setuser))
        conn.commit()
        cur.execute('''DELETE FROM splits WHERE user=%s AND splituser=%s AND splitamount=%s''',
                       (setuser,session['user'],amount))
        conn.commit()
        cur.execute('''UPDATE balance SET balance=%s WHERE username=%s''',(usrbal,session['user']))
        conn.commit()
    return render_template('settle.html',data=data,msg=msg)

@app.route('/temp',methods=['GET','POST'])
def temp():
    if request.method=="POST":
        return request.get_json('mydata')
   

if __name__=="__main__":
    app.run()