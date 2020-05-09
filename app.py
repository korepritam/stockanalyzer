from flask import Flask,render_template, redirect, url_for, request, json
from flask_mysqldb import MySQL
import os
import requests

app=Flask(__name__)  #creating instance of class flask

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='stockdb'

mysql=MySQL(app)
session={}

url = "https://yahoo-finance15.p.rapidapi.com/api/yahoo/ne/news/AAPL"

headers = {
    'x-rapidapi-host': "yahoo-finance15.p.rapidapi.com",
    'x-rapidapi-key': "4deb0e01a0msh43e8c813ecadc63p1031ecjsn6f107073d104"
    }

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/company')
def company():
    if 'logged_in' in session :
        #response = requests.request("GET", url, headers=headers)
        #print(response.text)
        json_url = os.path.join(SITE_ROOT, "static/data", "company.json")
        data = json.load(open(json_url))
        t=data['item']
        #print(t[0])
        length=len(t)
        return render_template('company.html',data=t,length=length)
    else :
        msg=2
        return render_template('home.html',session=session,msg=msg)

@app.route('/jquery')
def jquery():
    return render_template('jquery.html')

@app.route('/bootstrap')
def bootstrap():
    return render_template('bootstrap.html')

@app.route('/register')
def register():
    return render_template('register.html',message="")

@app.route('/validate', methods=['POST'])
def validate():
        #print(request.form.to_dict())
        name=request.form['name']
        username=request.form['username']
        is_Author=request.form['radio']
        email=request.form['email']
        password=request.form['password']
        cur=mysql.connection.cursor()
        cur.execute("insert into users(name,is_Author,username,email,password) values('"+name+"','"+is_Author+"','"+username+"','"+email+"','"+password+"')")
        #print(q)
        mysql.connection.commit()
        return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/checkAccount',methods=['POST'])
def checkAccount():
    account=['0']*4
    username=request.form['username']
    password=request.form['password']
    cur=mysql.connection.cursor()
    cur.execute("select * from users where username= '"+username+"' and password= '"+password+"'")
    account=cur.fetchone()
    mysql.connection.commit()
    print(account)
    if account is None:
        msg=0
        return render_template('home.html',session=session,msg=msg)
    elif(account[3]=='root' and account[5]=='1234'):
        print('welcome admin')
        return redirect(url_for('admin'))
    elif account:
        session['logged_in']=True
        session['id']=account[0]
        session['name']=account[1]
        session['is_Author']=account[2]
        session['username']=account[3]
        session['email']=account[4]
        msg=1
        print(type(session['is_Author']))
        return render_template('home.html',session=session,msg=msg)
    else:
        msg='Incorrect credentials'
        print(msg)
    return render_template('home.html',session=session)

@app.route('/')
def home():
    print(session)
    return render_template('home.html',session=session)

@app.route('/logout')
def logout():
    session.clear()
    return render_template('home.html',session=session)

#### Admin section ####
@app.route('/admin')
def admin():
    return render_template('admin.html')

#### Blog section ####

@app.route('/blog')
def blog():
    if 'logged_in' in session :
        cur=mysql.connection.cursor()
        cur.execute("select * from news")
        news=cur.fetchall()
        length=len(news)
        mysql.connection.commit()
        #print(news)
        return render_template('blog.html',news=news,length=length)
    else :
        msg=2
        return render_template('home.html',session=session,msg=msg)

@app.route('/postnews',methods=['POST'])
def postnews():
    if request.method == "POST":
        #print(request.form.to_dict())
        data=request.form.to_dict()
        print(data['id'])
        nid=data['id']
        title=data['title']
        content=data['content']
        cur=mysql.connection.cursor()
        cur.execute("insert into news(id,title,content) values('"+nid+"','"+title+"','"+content+"')")
        mysql.connection.commit()
    return redirect(url_for('blog'))

@app.route('/getBlogById',methods=['POST'])
def getBlogById():
    if request.method == "POST":
        data=request.form.to_dict()
        #print(data)
        nid=data['id']
        #print(nid)
        cur=mysql.connection.cursor()
        cur.execute("select * from news where id = '"+nid+"' ")
        rec=cur.fetchone()
        #print(rec[0])
        mysql.connection.commit()
        news = []
        news.append({'Id':rec[0],'Title':rec[1],'Content':rec[2]})
        #print(news)
        return json.dumps(news)

@app.route('/updateBlog',methods=['POST'])
def updateBlog():
    if request.method == "POST":
        #print(request.form.to_dict())
        title = request.form['title']
        content = request.form['content']
        nid = request.form['id']
        cur=mysql.connection.cursor()
        cur.execute(" update news set title = '"+title+"' , content = '"+content+"' where id = '"+nid+"' ")
        mysql.connection.commit()
        return '' 

@app.route('/deleteBlog',methods=['POST'])
def deleteBlog():
    if request.method == 'POST':
        nid=request.form['id']
        print(nid)
        cur = mysql.connection.cursor()
        cur.execute("delete from news where id ='"+nid+"'")
        mysql.connection.commit()
        return ''

if __name__ == "__main__":
    app.run(debug=True)