from flask import Flask,render_template,flash, request, url_for, redirect,session
from dbconnect import connection
from wtforms import PasswordField,Form,BooleanField, TextField, validators, IntegerField, SelectField, DecimalField
from wtforms.fields.html5 import DateField
from datetime import datetime
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from utils import *
import pygal 
import json
import redis 
import ujson
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:linq12345@localhost/linq'
db = SQLAlchemy(app)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)




class AmazonItems(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  asin        = db.Column(db.String(120))
  category    = db.Column(db.String(120))
  clicks      = db.Column(db.Integer)
  conversion  = db.Column(db.Integer)
  dqty        = db.Column(db.Integer)
  date        = db.Column(db.DateTime)
  link_type   = db.Column(db.String(120))
  nqty        = db.Column(db.Integer)
  price       = db.Column(db.Float)
  qty         = db.Column(db.Integer)
  seller      = db.Column(db.String(120))
  tag         = db.Column(db.String(120))
  title       = db.Column(db.String(120))

  def __init__(self,asin, category,clicks,conversion,dqty,date,link_type,nqty,price,qty,seller, tag , title ):
     self.asin              = asin
     self.category = category
     self.clicks = clicks
     self.conversion = conversion
     self.dqty = dqty
     self.date = date
     self.link_type = link_type
     self.nqty = nqty
     self.price =  price
     self.qty = qty
     self.seller =  seller
     self.tag  =  tag
     self.title =  title

  def __repr__(self):
                return '%s' % self.asin



class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120),unique=True)
    state = db.Column(db.String(120))
    stores = db.relationship('Store', backref='store',
		                        lazy='dynamic')
    def __repr__(self):
		return '%s' % self.name


class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120),unique=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    address = db.Column(db.Text)
    pincode = db.Column(db.Integer)
    users = db.relationship('User', backref='user',
                    lazy='dynamic')
    def __repr__(self):
            return '%s' % (self.name)

class OrderStatus(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     status = db.Column(db.String(120), unique=True)

     def __init__(self,status):
        self.status = status

     def __repr__(self):
          return '<OrderStatus %r>' % self.status

class ReturnStatus(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     status = db.Column(db.String(120), unique=True)

     def __init__(self,status):
        self.status = status

     def __repr__(self):
          return '<ReturnStatus %r>' % self.status



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    name = db.Column(db.String(120))
    mobile_num = db.Column(db.String(13), unique=True)
    password = db.Column(db.String(150))
    is_active = db.Column(db.Boolean)
    affliate_id = db.Column(db.String(120))
    is_admin = db.Column(db.Boolean)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'))


    def __init__(self, email, name, mobile_num, password, store_id, affliate_id):
        self.email = email
        self.name = name
        self.mobile_num = mobile_num
        self.password = password
        self.store_id = store_id
        self.is_active = True
        self.affliate_id = affliate_id
        self.is_admin = False

        def __repr__(self):
                return '<User %r>' % self.email

class Customer(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     email = db.Column(db.String(120), unique=True)
     mobile_num = db.Column(db.String(13), unique=True)
     name = db.Column(db.String(120))
     marketing_source = db.Column(db.String(120))
     date_of_birth = db.Column(db.DateTime)
     gender = db.Column(db.String(13))
     store_id = db.Column(db.Integer, db.ForeignKey('store.id'))

     def __init__(self,email,mobile_num,name,marketing_source,date_of_birth, gender,store_id):
         self.email = email
         self.mobile_num = mobile_num
         self.name = name
         self.marketing_source = marketing_source
         self.date_of_birth = date_of_birth
         self.gender = gender
         self.store_id = store_id
     def __repr__(self):
          return '%r, %s ' % (self.name.encode('utf-8'), self.mobile_num)

class Orderitem(db.Model):
     linq_order_num = db.Column(db.Integer, primary_key=True)
     order_status_id = db.Column(db.Integer, db.ForeignKey('order_status.id'))
     order_id = db.Column(db.String(100))
     item_name = db.Column(db.String(120))
     item_cost = db.Column(db.Float)
     custmer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
     order_date_time = db.Column(db.DateTime, default=datetime.now())
     order_category = db.Column(db.String(120))
     ordered_by = db.Column(db.Integer, db.ForeignKey('user.id'))
     linq_shipping_cost = db.Column(db.Float)
     website_shipping_cost = db.Column(db.Float)
     total_cost = db.Column(db.Float)
     advance_amount = db.Column(db.Float)
     website = db.Column(db.String(120))
     other = db.Column(db.String(120))
     rvn = db.Column(db.Integer)
     received_date = db.Column(db.DateTime)
     delivered_date = db.Column(db.DateTime)
     store_id = db.Column(db.Integer, db.ForeignKey('store.id'))

     def __init__(self,order_id,item_name,item_cost,customer_id,order_category, linq_shipping_cost,website_shipping_cost,advance_amount,website,other):
        self.order_id = order_id
        self.item_name = item_name
        self.item_cost = item_cost
        self.custmer_id = customer_id
        self.order_category = order_category
        self.linq_shipping_cost = linq_shipping_cost
        self.website_shipping_cost = website_shipping_cost
        self.advance_amount = advance_amount
        self.website = website 
        self.other = other
        self.store_id = session['store_id']
        self.ordered_by = session['user_id']
         
        self.total_cost = item_cost + linq_shipping_cost + website_shipping_cost 
        self.order_status_id = 1 
        
     def __repr__(self):
          return '<Orderitem %r>' % self.item_name



class ReturnReason(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     reason = db.Column(db.String(120), unique=True)

     def __init__(self,status):
        self.reason = reason

     def __repr__(self):
          return '<ReturnReason %r>' % self.reason


class ReturnItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    linq_order_num = db.Column(db.Integer, db.ForeignKey('orderitem.linq_order_num'),index=True)
    return_status_id = db.Column(db.Integer, db.ForeignKey('return_status.id'),index=True)
    amount_returnable = db.Column(db.Float)
    courier_tracking_num = db.Column(db.String(120),index=True)
    is_return_shippingcharge_refunded =  db.Column(db.Boolean)
    created_date =  db.Column(db.DateTime,index=True ,default=datetime.now())
    return_reason_id = db.Column(db.Integer, db.ForeignKey('return_reason.id'))  
    def __init__(self,linq_order_num,return_reason_id, returnable_amount=0, return_reason=''):
          self.linq_order_num = linq_order_num
          self.return_reason_id = return_reason_id
          self.amount_returnable = returnable_amount
          self.return_reason = return_reason
          self.return_status_id = 1
    def __repr__(self):
          return '<ReturnItem %r>' % self.id

class AddOrderForm(Form):
    order_id  = TextField('Website Order Id', [validators.length(min=4, max=120)])
    item_name = TextField('Item Name', [validators.length(min=4, max=120)])
    item_cost = DecimalField('Item Cost' , [validators.Required()])
    custmer_id = SelectField('Customer',coerce=int)
    order_category = SelectField('Order Category',coerce=int,choices=[(1,'Mobiles'), (2,'Clothing')]) 
    linq_shipping_cost =  DecimalField('Linq Shipping Cost' , [validators.Required()])
    website_shipping_cost = DecimalField('Website Shipping Cost' , [validators.Required()])
    advance_amount = DecimalField('Advance Amount' , [validators.Required()])
    website = SelectField('Website', coerce=int,choices=[(1,'Amazon'), (2,'Flipkart')] )
    other = TextField('Any Other Information')
    def __init__(self, *args, **kwargs):
        super(AddOrderForm, self).__init__(*args, **kwargs)
        self.custmer_id.choices = convert_list_wtforms_choices(Customer.query.all())


class SendSMSForm(Form):
      message = TextField('Message to be sent', [validators.length(min=4, max=240)])
class SendSMSFormSingle(Form):
      message = TextField('Message to be sent', [validators.length(min=4, max=240)])
      mobile_number = TextField('Mobile Number', [validators.Required()])


class RegistrationForm(Form):
    email = TextField('Email Address', [validators.length(min=4, max=120)])
    name = TextField('Name', [validators.length(min=4, max=120)])
    password = PasswordField('Password', [validators.Required(), validators.EqualTo('confirm',message="Passwords must Match!!")])
    confirm = PasswordField('Repeat Password')
    mobile_num = TextField('Telephone', [validators.Required()])
    affliate_id = TextField('Affliate Id', [validators.length(min=5, max=120)])
    stores = Store.query.all()
    store = SelectField('Store',coerce=int,choices= convert_list_wtforms_choices(stores))
    accept_tos = BooleanField('I accept the <a href="/tos/">Terms of Service and <a href="/Privacy/">The Privacy Notice', [validators.Required()])

class CustomerForm(Form):
    email = TextField('Email Address', [validators.length(min=4, max=120)])
    name = TextField('Name', [validators.length(min=4, max=120)])
    mobile_num = TextField('Mobile Number', [validators.Required()])
    marketing_source = SelectField('Marketing Source' ,coerce=int, choices = [(1,'Flyer Marketing'),(2, 'Tv Ad'),(3, 'Word Of Mouth'),(4,'Other')])
    date_of_birth = DateField('Date Of Birth', [validators.Required()])
    gender = SelectField('Gender' ,coerce=int, choices =[(1,'Male'),(2,'Female')])

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash("You need to login first Dude!!")
            return redirect(url_for('login'))
    return wrap

@app.route("/add-customer/", methods = ["GET","POST"])
@login_required
def add_customer():
    try:
        print request
        form = CustomerForm(request.form)
        print form
        print request.method
        print form.email
        print form.email.data
        print form.name.data
        print form.date_of_birth.data
        if request.method == "POST" and form.validate():
            print "posty"
            email = form.email.data
            name = form.name.data
            mobile_num = form.mobile_num.data
            marketing_source = form.marketing_source.data
            date_of_birth = form.date_of_birth.data
            gender = form.gender.data
            store_id = session['store_id']
            customer = Customer(email,mobile_num,name,marketing_source,date_of_birth,gender,store_id)
            db.session.add(customer)
            db.session.commit()
            flash("Customer Added successfully")
            return redirect(url_for('dashboard'))
        return render_template('add-customer.html', form=form)
    except Exception as e:
        return str(e)



@app.route("/add-order/", methods = ["GET","POST"])
@login_required
def add_order():
    try:
        print "sratb get orderr"
        print request
        print "after request"
        print request.form
        form = AddOrderForm(request.form)
        print "before cust id"
        print form.custmer_id.data
        if request.method == "POST" and form.validate():
            print 'postyy'
            order_id = form.order_id.data
            item_name = form.item_name.data
            item_cost = form.item_cost.data
            order_category = form.order_category.data
            custmer_id = form.custmer_id.data
            linq_shipping_cost = form.linq_shipping_cost.data
            website_shipping_cost = form.website_shipping_cost.data
            total_cost = item_cost + linq_shipping_cost + website_shipping_cost 
            advance_amount = form.advance_amount.data
            other = form.other.data
            website = form.website.data
            print 'here'
            print custmer_id
            print session['user_id']
            store_id = session['store_id']
            order_item = Orderitem(order_id,item_name,item_cost,custmer_id,order_category, linq_shipping_cost,website_shipping_cost,advance_amount,website,other) 
            db.session.add(order_item)
            db.session.commit()
            print 'after commit'
            flash("Order Added successfully")
            return redirect(url_for('dashboard'))
        return render_template('add-order.html', form=form)
    except Exception as e:
        return str(e)


@app.route("/add-return/", methods = ["GET","POST"])
@login_required
def add_return():
        if request.method == "POST":
           print "post"
           order= Orderitem.query.filter_by(linq_order_num = request.json['linq_order_num']).first()
           print order
           order.order_status_id = 4
           returnable_amount = 0
           if order.order_status_id == 2 or order.order_status_id == 1:
               returnable_amount = order.advance_amount
           else:
              returnable_amount = order.item_cost + order.website_shipping_cost
           return_reason = request.json['return_reason']
           print return_reason
           return_item = ReturnItem(request.json['linq_order_num'],1, returnable_amount, return_reason)
           db.session.add(return_item)
           db.session.commit()
           print "sucessfully commited"
           return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
 
        orders  = Orderitem.query.join(Customer, Orderitem.custmer_id == Customer.id).add_columns(Orderitem.order_date_time,Orderitem.order_id, Orderitem.item_name, Orderitem.item_cost, Orderitem.website_shipping_cost, Orderitem.order_status_id , Customer.mobile_num, Customer.name, Orderitem.linq_shipping_cost, Orderitem.advance_amount,Orderitem.linq_order_num)
        return render_template('add-return.html',orders=orders)



@app.route("/returns-all/", methods = ["GET"])
@login_required
def all_return():
   print 'zingdi'
   returns  = ReturnItem.query.join(Orderitem,Orderitem.linq_order_num == ReturnItem.linq_order_num ).join(Customer, Orderitem.custmer_id == Customer.id).add_columns(Orderitem.order_date_time,Orderitem.order_id, Orderitem.item_name, Orderitem.item_cost, Orderitem.website_shipping_cost, Orderitem.order_status_id , Customer.mobile_num, Customer.name, Orderitem.linq_shipping_cost, Orderitem.advance_amount,Orderitem.linq_order_num)
   returns  = ReturnItem.query.join(Orderitem ).join(Customer).add_columns(Orderitem.order_date_time,Orderitem.order_id, Orderitem.item_name, Orderitem.item_cost, Orderitem.website_shipping_cost, Orderitem.order_status_id , Customer.mobile_num, Customer.name, Orderitem.linq_shipping_cost, Orderitem.advance_amount,Orderitem.linq_order_num, ReturnItem.id, ReturnItem.return_status_id).all()
   print '---------'
   print returns
   print '----------'
   return render_template('returns-ab.html', returns=returns)


@app.route("/")
def hello():
    return render_template("header.html")
    #return "Its only a matter of time before LinQ makes it big"

@app.route("/dashboard/")
def dashboard():
    print "tehmpydash:"
    return render_template("dashboard.html")

@app.errorhandler(404)
def page_not_found(e):
        return ("The page doesn't exist !!")

@app.route("/pap/")
def hello1():
    returns  = ReturnItem.query.join(Orderitem ).join(Customer).add_columns(Orderitem.order_date_time,Orderitem.order_id, Orderitem.item_name, Orderitem.item_cost, Orderitem.website_shipping_cost, Orderitem.order_status_id , Customer.mobile_num, Customer.name, Orderitem.linq_shipping_cost, Orderitem.advance_amount,Orderitem.linq_order_num, ReturnItem.id, ReturnItem.return_status_id).all()

    return render_template("returns-ab.html", returns=returns)
    #return "Its only a matter of time before LinQ makes it big"


@app.route("/logout/")
@login_required
def logout():
   session.clear()
   flash("You have been logged out!!")
   gc.collect()
   return redirect(url_for('dashboard'))

@app.route("/customers/")
@login_required
def customers():
   users= Customer.query.filter_by(store_id = session['store_id']).all()
   for user in users:
       print user.name
       print user.email
   return render_template('customers.html', users=users)
   return User.query.filter_by(store_id = session['store_id']).all()

@app.route("/orders/")
@login_required
def orders_all():
   orders  = Orderitem.query.join(Customer, Orderitem.custmer_id == Customer.id).add_columns(Orderitem.order_date_time,Orderitem.order_id, Orderitem.item_name, Orderitem.item_cost, Orderitem.website_shipping_cost, Orderitem.order_status_id , Customer.mobile_num, Customer.name, Orderitem.linq_shipping_cost, Orderitem.advance_amount,Orderitem.linq_order_num)
   #orders= Orderitem.query.filter_by(store_id = session['store_id']).all()
   print orders 
   return render_template('orders.html', orders=orders)

@app.route("/orders-tracked/")
@login_required
def orders_all_tracked():
   tracked_items = AmazonItems.query.filter_by(tag = session['affliate_id']).all()
   return render_template('orders-tracked.html', items =tracked_items)


@app.route("/receive-order/", methods = ["POST"])
@login_required
def orders_receive():
   print request
   print request.json
   order= Orderitem.query.filter_by(linq_order_num = request.json['linq_order_num']).first()
   order.order_status_id = 2
   db.session.commit()
   return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route("/deliver-order/", methods = ["POST"])
@login_required
def orders_deliver():
   print request
   print request.json
   order= Orderitem.query.filter_by(linq_order_num = request.json['linq_order_num']).first()
   order.order_status_id = 3
   db.session.commit()
   return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
   


@app.route("/dispatch-return/", methods = ["POST"])
@login_required
def return_dispatch():
   print "return_dispatch"
   print request
   print request.json
   returnitem = ReturnItem.query.filter_by(id = request.json['return_id']).first()
   returnitem.return_status_id = 2
   returnitem.courier_tracking_num = request.json['courier_details']
   db.session.commit()
   return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route("/return-destination/", methods = ["POST"])
@login_required
def return_destination():
   print "return_dispatch"
   print request
   print request.json
   returnitem = ReturnItem.query.filter_by(id = request.json['return_id']).first()
   returnitem.return_status_id = 3
   db.session.commit()
   return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route("/refund-received/", methods = ["POST"])
@login_required
def refund_received():
   print "return_dispatch"
   print request
   print request.json
   returnitem = ReturnItem.query.filter_by(id = request.json['return_id']).first()
   returnitem.return_status_id = 4
   db.session.commit()
   return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


@app.route("/display-orders/", methods = ["GET"])
@login_required
def display_order():
    return render_template('orders-display.html')



@app.route("/returns/", methods = ["GET"])
@login_required
def display_returns():
    return render_template('returns.html')


@app.route("/login/", methods = ["GET","POST"])
def login():
    error = ''
    try:
       c,conn = connection()
       if request.method == "POST":
             print request
             print request.form['username']
             print request.form['password']
             data = c.execute("SELECT * from user where email  = (%s)" ,[thwart(request.form['username'])])
             print data
             data = c.fetchone()
             print data
             if data and sha256_crypt.verify(request.form['password'], data[4]):
                    print 'matchy'
                    session['logged_in'] = True
                    session['username'] = request.form['username']
                    session['store_id'] = data[8]
                    session['user_id'] = data[0]
                    session['affliate_id'] = data[6]
                    flash("You are now logged in !!"+ str(request.form['username']))
                    return redirect(url_for("dashboard"))
             else:
                print "Invalid"
                error = "Invalid Credentials. Try Again."
                flash(error)
       return render_template("login.html", error=error)

    except Exception as e:
         flash(e)
         return render_template("login.html", error = e)


@app.route("/register/", methods = ["GET","POST"])
def register():
    try:
       form = RegistrationForm(request.form)
       if request.method == "POST" and form.validate():
           email = form.email.data
           name = form.name.data
           mobile_num = form.mobile_num.data
           affliate_id = form.affliate_id.data
           print 'storeeeees'
           print form.store.data
           print 'kayees'
           store_id = form.store.data
           password = sha256_crypt.encrypt(str(form.password.data))
           c,conn = connection()
           #x = c.execute("SELECT * from users where user_name= (%s)",[thwart(username)])
           x = User.query.filter_by(email=thwart(email)).first()
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
               admin = User(email,name,mobile_num, password,store_id,affliate_id)
               db.session.add(admin)
               db.session.commit()
               session['logged_in'] = True
               session['name'] = name
               session['store_id'] = store_id
               session['user_id']=User.query.filter_by(mobile_num=mobile_num).first().id 
               return redirect(url_for('dashboard'))
       return render_template('register.html', form=form)
    except Exception as e:
       return str(e)

@app.route('/pygalexample/')
def pygalexample():
	try:
		graph = pygal.Bar()
		graph.title = 'No of orders on daily basis'
		graph.x_labels = ['2011','2012','2013','2014','2015','2016']
		graph.add('Tiruvuru',  [15, 31, 89, 200, 356, 900])
		graph.add('Khammam',    [15, 45, 76, 80,  91,  95])
		graph.add('Vissannapeta',     [5,  51, 54, 102, 150, 201])
		graph.add('Siddipet',  [5, 15, 21, 55, 92, 105])
		graph_data = graph.render_data_uri()
		return render_template("graphing.html", graph_data = graph_data)
	except Exception, e:
		return(str(e))
@app.route('/send-sms/', methods = ["GET","POST"])
@login_required
def send_sms():
        try:
           form = SendSMSForm(request.form)
           if request.method == "POST":
              c,conn = connection()
              print "hello"
              data = form.message.data 
              print data
              redis_client.sadd('sms-queue',  data)
              return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

           return render_template('send-sms.html', form=form)

	    

        except Exception,e :
               return(str(e))

              
@app.route('/send-sms-single/', methods = ["GET","POST"])
@login_required
def send_sms_single():
        try:
           form = SendSMSFormSingle(request.form)
           if request.method == "POST":
              c,conn = connection()
              print "hello ckwhjqwbh"
              data = request.json['message']
              mobile_number = request.json['mobile_number']
              print data
              redis_client.sadd('sms-queue-single', ujson.dumps({'data': data, 'mobile_number': mobile_number }))
              print "sfksjb"
              return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

           return render_template('send-sms-single.html', form=form)


        except Exception,e :
               return(str(e))
             



if __name__ == "__main__":
    app.run()

