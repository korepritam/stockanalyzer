from flask import Flask,render_template, redirect, url_for, request, json, make_response, jsonify
from flask_mysqldb import MySQL
import os,requests,hashlib,datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app=Flask(__name__)  #creating instance of class flask
CORS(app)

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

@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/company1')
def company1():
    return render_template('company1.html')


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
        print(type(session['is_Author']))
        is_Author = session['is_Author']
        return render_template('company.html',data=t,length=length,is_Author=is_Author)
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
        passwor=generate_password_hash(password)
        cur=mysql.connection.cursor()
        #cur.execute("insert into users(name,is_Author,username,email,password) values('"+name+"','"+is_Author+"','"+username+"','"+email+"','"+password+"')")
        sql_query="""insert into users (name,is_Author,username,email,password) values (%s,%s,%s,%s,%s)"""
        recordTuple=(name,is_Author,username,email,passwor)
        cur.execute(sql_query,recordTuple)
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
    #cur.execute("select * from users where username= '"+username+"' and password= '"+password+"'")
    sql_query="""select * from users where username = %s """
    recordTuple = (username,)
    cur.execute(sql_query,recordTuple)
    account=cur.fetchall()
    mysql.connection.commit()
    print(type(account))

    if not account:
        msg=0
        return render_template('home.html',session=session,msg=msg)

    for account in account:
        if check_password_hash(account[5], password):           # checking password with hash of passwords in db
            print('logged in')
            session['logged_in']=True
            session['id']=account[0]
            session['name']=account[1]
            session['is_Author']=account[2]
            session['username']=account[3]
            session['email']=account[4]
            msg=1
            return render_template('home.html',session=session,msg=msg)
    return render_template('home.html',session=session,msg=0)

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
    print(session)
    if 'logged_in' in session :
        cur=mysql.connection.cursor()
        sql_query="""select * from news where news.uid = %s"""
        recordTuple=(session['id'],)
        cur.execute(sql_query,recordTuple)
        news=cur.fetchall()
        length=len(news)
        mysql.connection.commit()
        #print(news)
        return render_template('blog.html',news=news,length=length)
    else :
        msg=2
        return render_template('home.html',session=session,msg=msg)

@app.route('/read_blog',methods=['POST'])
def read_blog():
    if request.method == "POST":
        data=request.form.to_dict()
        company=data['company']
        print(company)
        cur=mysql.connection.cursor()
        sql_query = """ select * from news where company=%s """
        recordTuple=(company,)
        cur.execute(sql_query,recordTuple)
        rec=cur.fetchall()
        mysql.connection.commit()
        #print(rec)
        news={}
        for i in rec:
            news.update({i[2]:i[3]})     
        print(news)   
    return jsonify(news)

@app.route('/render_blog')
def render_blog():
    if 'logged_in' in session :
        return render_template('read.html')

@app.route('/postnews',methods=['POST'])
def postnews():
    if request.method == "POST":
        #print(request.form.to_dict())
        data=request.form.to_dict()
        print(data)
        company=data['company']
        title=data['title']
        content=data['content']
        cur=mysql.connection.cursor()
        #cur.execute("insert into news(id,title,content) values('"+nid+"','"+title+"','"+content+"')")
        sql_query=""" insert into news (company,title,content,uid,date) values (%s,%s,%s,%s,%s) """
        recordTuple=(company,title,content,session['id'],datetime.datetime.now())
        cur.execute(sql_query,recordTuple)
        mysql.connection.commit()
    return redirect(url_for('blog'))

@app.route('/getBlogById',methods=['POST'])
def getBlogById():
    if request.method == "POST":
        data=request.form.to_dict()
        #print(data)
        nid=data['id']
        print(type(nid))
        cur=mysql.connection.cursor()
        #cur.execute("select * from news where id = '"+nid+"' ")
        sql_query=""" select * from news where id = %s """
        recordTuple=(nid,)
        cur.execute(sql_query,recordTuple)
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
        #cur.execute(" update news set title = '"+title+"' , content = '"+content+"' where id = '"+nid+"' ")
        sql_query=""" update news set title = %s, content= %s where id= %s """
        recordTuple=(title,content,nid)
        cur.execute(sql_query,recordTuple)
        mysql.connection.commit()
        return '' 

@app.route('/deleteBlog',methods=['POST'])
def deleteBlog():
    if request.method == 'POST':
        nid=request.form['id']
        print(nid)
        cur = mysql.connection.cursor()
        #cur.execute("delete from news where id ='"+nid+"'")
        sql_query= """ delete from news where id =%s """
        recordTuple=(nid,) 
        cur.execute(sql_query,recordTuple)
        mysql.connection.commit()
        return ''


######   CREATING API FOR EXPERT'S BLOG    #####

@app.route('/api/v1/resources/books/all',methods=['GET'])
def api_all():
    cur=mysql.connection.cursor()
    cur.execute("select company,title,content,date,uid from news")
    all_records=cur.fetchall()
    mysql.connection.commit()
    return jsonify(all_records)

@app.route('/api/v1/resources/books', methods=['GET'])
def api_fetch():
    query_parameters = request.args
    company = query_parameters.get('company')
    uid = query_parameters.get('uid')

    query = "SELECT company,title,content,date,uid FROM news WHERE"
    to_filter = []
    recordTuple=[]

    if company:
        recordTuple.append(company)
        query += ' company=%s AND'
        to_filter.append(company)
    if uid:
        recordTuple.append(uid)
        query += ' uid=%s AND'
        to_filter.append(uid)
    if not (company or uid):
        return 'page_not_found(404)'

    query = query[:-4] + ';'

    cur=mysql.connection.cursor()
    cur.execute(query,tuple(recordTuple))
    records=cur.fetchall()
    mysql.connection.commit()
    return jsonify(records)

@app.route('/api')
def api():
    return render_template('api.html')

if __name__ == "__main__":
    app.run(debug=True)