from flask import Flask,render_template,flash, request, url_for, redirect,session  
from dbconnect import connection
from wtforms import PasswordField,Form,BooleanField, TextField, validators
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart 
import gc 
from functools import wraps
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:linq12345@localhost/linq'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username


@app.route("/")
def hello():
    return render_template("main-c.html")
    #return "Its only a matter of time before LinQ makes it big"

@app.route("/dashboard/")
def dashboard():
    flash(" Navigate to orders tab to add orders")
    return render_template("dashboard.html")

@app.errorhandler(404)
def page_not_found(e):
        return ("The page doesn't exist !!")
	  

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash("You need to login first Dude!!")
            return redirect(url_for('login'))
    return wrap

@app.route("/logout/")
@login_required
def logout():
   session.clear()
   flash("You have been logged out!!")
   gc.collect()
   return redirect(url_for('dashboard'))
   



@app.route("/add-order/")
@login_required
def add_order():
   return redirect(url_for('dashboard'))


@app.route("/add-customer/")
@login_required
def add_customer():
   return redirect(url_for('dashboard'))



@app.route("/login/", methods = ["GET","POST"])
def login():
    error = ''
    try:
       c,conn = connection()
       if request.method == "POST":
             data = c.execute("SELECT * from users where user_name = (%s)" ,[thwart(request.form['username'])])
             print data
             data = c.fetchone()[2]
             print data
             if sha256_crypt.verify(request.form['password'], data):
                    session['logged_in'] = True
                    session['username'] = request.form['username']
                    flash("You are now logged in !!"+ str(request.form['username']))
                    return redirect(url_for("dashboard"))
             else: 
              	error = "Invalid Credentials. Try Again."
              	flash(error)
       return render_template("login.html", error=error)  
           
    except Exception as e:
         flash(e)
         return render_template("login.html", error = e)

class RegistrationForm(Form):
      username = TextField('Username', [validators.length(min=4, max=48)])
      email = TextField('Email Address', [validators.length(min=4, max=48)])
      password = PasswordField('Password', [validators.Required(), validators.EqualTo('confirm',message="Passwords must Match!!")])
      confirm = PasswordField('Repeat Password')
      accept_tos = BooleanField('I accept the <a href="/tos/">Terms of Service and <a href="/Privacy/">The Privacy Notice')
      


@app.route("/register/", methods = ["GET","POST"])
def register():
    try:
       form = RegistrationForm(request.form)
       if request.method == "POST" and form.validate():
           username = form.username.data
           email = form.email.data
           flash(email)
           password = sha256_crypt.encrypt(str(form.password.data))
       	   c,conn = connection()
           #x = c.execute("SELECT * from users where user_name= (%s)",[thwart(username)])
           x = User.query.filter_by(username=thwart(username)).first() 
           print x 
           if x is not None:
                 flash("The username already exists! Please choose another")
                 render_template('register.html', form=form)
           else: 
               #c.execute("INSERT into users (user_name,password,email) VALUES  (%s,%s,%s)",[thwart(username),thwart(password),thwart(email)])
               #conn.commit()
               #flash("Thanks For Registering!!")
               #c.close()
               #conn.close()
               #gc.collect()
               admin = User(username,email)
               db.session.add(admin)
               db.session.commit() 
               session['logged_in'] = True
               session['username'] = username
               return redirect(url_for('dashboard'))
       return render_template('register.html', form=form)  
    except Exception as e:
       return str(e)



if __name__ == "__main__":
    app.run()

