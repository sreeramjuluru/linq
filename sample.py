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
class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120),unique=True)
    state = db.Column(db.String(120))
    stores = db.relationship('Store', backref='store',
                                        lazy='dynamic')
    def __repr__(self):
                return '%s' % self.name
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
    created_date =  db.Column(db.DateTime,index=True )
    return_reason_id = db.Column(db.Integer, db.ForeignKey('return_reason.id'))
    def __init__(self,linq_order_num,return_reason_id):
          self.linq_order_num = linq_order_num
          self.return_reason_id = return_reason_id
    def __repr__(self):
          return '<ReturnItem %r>' % self.linq_order_num


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
          return '<Customer %r>' % self.email


class OrderStatus(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     status = db.Column(db.String(120), unique=True)

     def __init__(self,status):
     	self.status = status

     def __repr__(self):
          return '<OrderStatus %r>' % self.status
class Orderitem(db.Model):
     linq_order_num = db.Column(db.Integer, primary_key=True)
     order_status_id = db.Column(db.Integer, db.ForeignKey('order_status.id'))
     order_id = db.Column(db.String(100))
     item_name = db.Column(db.String(120))
     item_cost = db.Column(db.Float)
     custmer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
     order_date_time = db.Column(db.DateTime)
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
        self.customer_id = customer_id
        self.order_category = order_category
        self.linq_shipping_cost = linq_shipping_cost
        self.website_shipping_cost = website_shipping_cost
        self.advance_amount = advance_amount
        self.website = website 
        self.other = other
        
     def __repr__(self):
          return '<Customer %r>' % self.email

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


db.create_all()

