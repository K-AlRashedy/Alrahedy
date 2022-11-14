
from datetime import datetime
from io import BytesIO
from tempfile import TemporaryFile
from threading import Lock
from PIL import Image
from flask import Flask, render_template,redirect,session, request, send_file
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from validate_email import validate_email
from helpers import SQL, login_required, apology, cart_saving, is_not_phone,admin_login_required, list_return
from flask_mail import Mail, Message
from random import randint

import json
#config app
app = Flask(__name__)
#config session
app.config["SESSION_TYPE"] = 'filesystem'
#mail configration
app.config['MAIL_PORT'] = 587
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PASSWORD'] = 'cpuixcogpnqwhoad'
app.config['MAIL_DEFAULT_SENDER'] = 'kamela49652@gmail.com'
app.config['MAIL_USERNAME'] = 'kamela49652@gmail.com'
app.config['MAIL_USE_TLS'] = True
mail = Mail(app)
Session(app)
#connect to db
db = SQL('database.db')
# Set lock for data base
lock = Lock()



@app.route('/')
def index():
    products = db.description(r"select * from products")
    for product in products:
        images = db.execute("select image_id from images where product_id = ?", product['id'])
        imgs = []
        for img in images:
            imgs.append(img[0])
        product['images'] = imgs
    return render_template("index.html", products=products)


@app.route("/login" ,methods=["POST","GET"])
def login():
    if request.method == 'POST':
        if not request.form.get("email") or not request.form.get("password"):
            return apology('Invalid email Or Password')
        if id:= db.execute(r"SELECT id, fname,passwrd,cart FROM customers WHERE email = ?", request.form.get('email')):
            session['email'] = request.form.get('email')
            if check_password_hash(id[0][2], request.form.get("password")):
                session['user_id'] = id[0][0]
                if (cart_saving(id[0][3])):
                    session['cart'] = cart_saving(id[0][3])
                elif session.get('cart'):
                    db.execute(r"update customers set cart = ? WHERE id = ?", str(session['cart']), session['user_id'])
                else:
                    session['cart'] = {}
                session['fname'] = id[0][1]
                return redirect("/")
            else:
                return render_template("login.html",error="wrong Password")
        else:
            return render_template("login.html",error="Email Not Exist!")  
    return render_template('login.html')


@app.route("/changepassword", methods=['POST','GET']) #Done
def changepassword():
    if request.method == 'POST':
        if request.form.get("validationcode"):
            if request.form.get("validationcode") == session['security-number']:
                session['security-number'] = True
                return render_template("ch_pw.html")
        if  session['security-number'] == True:
            if request.form.get('password') and request.form.get('confirmation') and request.form.get('password') == request.form.get('confirmation'):
                db.execute(r"UPDATE customers SET passwrd = ? WHERE email = ? ", generate_password_hash(request.form.get('password')), session['email'])
                return redirect("/login")
            else:
                return render_template("ch_pw.html")
        else:
            return render_template("validate.html",action="/changepassword")

    session['security-number'] = str(randint(1,999999)).zfill(6)
    msg = Message("hello",sender=app.config['MAIL_DEFAULT_SENDER'],recipients=[session['email']])
    msg.body = f"""hello your verification code is {session['security-number']}"""
    mail.send(msg)
    return render_template("validate.html",action="/changepassword")




@app.route("/logout") # Done
def logout():
    session.clear()
    return redirect("/")

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        if not validate_email(request.form.get("email")):
            return apology("INvalid Email")
        if db.execute(r"SELECT id FROM customers WHERE email = ?", request.form.get("email")):
            session['email'] = request.form.get('email')
            return redirect("/login")
        if not (request.form.get("fname") or request.form.get("lname") or request.form.get("phone")):
            return apology("Requried Data Missing")
        if not request.form.get("password") == request.form.get("confirmation"):
            return apology('passwords dont match')
        #Saving user date in session
        for key in request.form:
            session[key] = request.form.get(key)
        session['security-number'] = str(randint(1,999999)).zfill(6)
        # print(session)
        msg = Message("hello",sender=app.config['MAIL_DEFAULT_SENDER'],recipients=[session['email']])
        msg.body = f"""hello your verification code is {session['security-number']}"""
        mail.send(msg)
        return render_template("validate.html", action="/signup")
    if request.method == 'GET' and request.args.get("validationcode"):
        if request.args.get("validationcode") == session['security-number']:
            db.execute(r"INSERT INTO customers (fname,lname,phone,phone_op,email,passwrd) Values (?,?,?,?,?,?)", session['fname'],session['lname'],session['phone'],session['phone_op'],session['email'],generate_password_hash(session['password']))
            id = db.execute(r"SELECT id FROM customers WHERE email = ?", session['email'])
            session['user_id'] = id[0][0]
            return redirect("/")
        else:
            return render_template("validate.html", error="wrong validation code")


    return render_template("signup.html")


#Search route
@app.route("/search")
def search():
    if request.args.get("q"):
        return json.dumps(db.description(r"select name from products where name like ? or description like ? or catagory like ?", "%"+request.args.get("q")+"%","%"+request.args.get("q")+"%","%"+request.args.get("q")+"%"))
    if request.args.get("Q"):
        products = db.description(r"select * from products where name like ? or description like ? or catagory like ?", "%"+request.args.get("Q")+"%","%"+request.args.get("Q")+"%","%"+request.args.get("Q")+"%")
        for product in products:
            images = db.execute("select image_id from images where product_id = ?", product['id'])
            imgs = []
            for img in images:
                imgs.append(img[0])
            product['images'] = imgs
        return render_template("search.html", products=products)

@app.route("/adminslogin" ,methods=['GET','POST']) # Done
def adminslogin():
    if request.method == 'POST':
        #Check for Errors
        if not (request.form.get("username") and request.form.get("password")):
            return apology("username and password required")
        #validate Log In
        if id := db.execute("select id,passwrd FROM users WHERE username = ?", request.form.get("username")):
            session['admin_name'] = request.form.get("username")
            if check_password_hash(id[0][1], request.form.get("password")):
                session['admin_id'] = id[0][0]
                return redirect("/admin")
            else:
                return render_template("adminslogin.html", error="Wong Password")
        else:
            return render_template("adminslogin.html", error="Wong UserName")

    return render_template("adminslogin.html")


@app.route("/createAdmin" , methods=['POST', 'GET']) # Done
@admin_login_required
def createadmin():
    if request.method == 'POST':
        if not (request.form.get("username") and request.form.get("password") and request.form.get("confirmation")):
            return apology("username, password and confirmation required")
        if db.execute("select id,passwrd FROM users WHERE username = ?", request.form.get("username")):
            return apology("username exist")
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords DOESn't MATCH")
        db.execute(r"INSERT INTO users (username,passwrd) VALUES (?,?)",request.form.get("username"), generate_password_hash(request.form.get("password")))
        return redirect("/admin")
    return render_template("createadmin.html")

@app.route("/admin" ,methods=['GET','POST'])
@admin_login_required
def admin():
    try:
        if not session['admin_id']:
            return redirect("/adminslogin")
    except KeyError:
        return redirect("/adminslogin")
    return render_template("admin.html",orders=db.get_orders(),orders_data=db.get_orders_details())

@app.route("/addproduct", methods=["POST", "GET"]) # TODO
@admin_login_required
def addproduct():
    if request.method == "POST":
        db.execute(r"INSERT INTO products (name,description,price,catagory,sub_catagory) VALUES (?,?,?,?,?)", request.form.get("name"), request.form.get("description"), request.form.get("price"), request.form.get("catagory"), request.form.get("sub_catagory"))
        id = db.execute(r"SELECT id FROM products ORDER BY id DESC LIMIT 1")
        images = request.files
        for img in images:
            image = images.get(img)
            image = Image.open(image)
            image = image.resize((200,200))
            fp = TemporaryFile()
            image.save(fp,'PNG')
            fp.seek(0)
            db.execute(r"INSERT INTO images (product_id,image) VALUES (?,?)", id[0][0],fp.read())
        return redirect("/addproduct")
    return render_template("newproduct.html",font=10,catagories=[c[0] for c in db.execute(r"Select catagory From catagory")])    

@app.route("/editproduct/<int:id>", methods=["POST", "GET"]) 
@admin_login_required
def editproduct(id):
    product = db.product(id)
    if request.method == 'GET':
        if request.args.get('r'):
            db.execute(r"DELETE FROM products WHERE id = ?", id)
            db.execute(r"DELETE FROM images WHERE product_id = ?", id)
            return "ok"
        return render_template("editproduct.html",product=product,font=10,catagories=[c[0] for c in db.execute(r"Select catagory From catagory")])
    else:
        db.execute(r"UPDATE products SET name = ?, description = ?, price = ?, catagory = ?, sub_catagory = ? WHERE id = ?", request.form.get("name"), request.form.get("description"), request.form.get("price"), request.form.get("catagory"), request.form.get("sub_catagory"), id)
        for i in range(4):
            if image := request.files.get(f"image{i}"):
                print(i)
                image = Image.open(image)
                image = image.resize((200,200))
                fp = TemporaryFile()
                image.save(fp,'PNG')
                fp.seek(0)
                db.execute(r"UPDATE images SET image = ? WHERE image_id = ?",fp.read(), product['images'][i])
        return redirect(f'/editproduct/{id}')
@app.route("/products") # TODO
@admin_login_required
def products():
    products = db.description(r"select * from products")
    for product in products:
        images = db.execute("select image_id from images where product_id = ?", product['id'])
        imgs = []
        for img in images:
            imgs.append(img[0])
        product['images'] = imgs
    return render_template("products.html", products=products,font=10)
@app.route("/cart") # Done
def cart():
    if session.get('user_id'):
        session['cart'] = cart_saving(db.cart(session['user_id']))
    if not session.get('cart'):
        session['cart'] = {}
    if request.args.get("i"):
        if request.args.get("i") in session['cart']:
            session['cart'][request.args.get("i")] += 1
        else:
            session['cart'][request.args.get("i")] = 1
    if request.args.get("r"):
        try:
            session['cart'].pop(request.args.get("r"))
        except (KeyError, ValueError):
            pass
    if request.args.get("n") and request.args.get("id"):
        if int(request.args.get("n")) == 0:
            session['cart'].pop(request.args.get("id"))
        else:
            session['cart'][request.args.get("id")] = int(request.args.get("n"))
    products, total = db.products(session['cart'])
    if session.get('user_id'):
        db.execute(r"update customers set cart = ? WHERE id = ?", str(session['cart']), session['user_id'])
    if request.args.get("n") and request.args.get("id") or request.args.get("r"):
        return {'total': total}
    return render_template("cart.html",products=products, total=total, classs="cart-container")


@app.route("/product")
def product():
    if request.args.get("i"):
        return render_template("product.html", product=db.product(request.args.get('i')))
    else:
        return redirect("/")


@app.route("/buy",methods=['POST','GET'])
@login_required
def buy():
    cart,total = db.products(session['cart'])
    if request.method == 'GET':
        if not session.get('cart'):
            return redirect("/cart")
        if  adress:= db.get_adresses(session['user_id']):
            return render_template('buy.html',adresses=adress, products=cart,total=total,classs='buy-container')
        else:
            return redirect("/adress")
    else:
        if not request.form.get("adress") and request.form.get("adress").isdecimal():
            return redirect("/buy")
        db.execute(r"INSERT INTO orders (cart,total,customer_id,adress_id,status,paid,date) VALUES (?,?,?,?,'pending','due',?)",str(session['cart']),total,session['user_id'],request.form.get("adress"),datetime.date(datetime.now()))
        session['cart'].clear()
        db.execute(r"update customers set cart = ? WHERE id = ?", str(session['cart']), session['user_id'])
        return redirect("/")


@app.route("/adress",methods=['POST','GET'])
@login_required
def adress():
    if request.method == 'POST':
        if not request.form.get("adress") and request.form.get("phone") and is_not_phone(request.form.get("phone").strip()):
            return apology("missing phone or adress")
        db.execute(r"INSERT INTO Adresses (customer_id,adress,phone) VALUES (?,?,?)",session['user_id'],request.form.get("adress"), request.form.get('phone'))
        return redirect("/buy")
    return render_template("adress.html")

@app.route("/orders",methods=["POST","GET"])
@admin_login_required
def orders():
    if request.method == 'GET':
        return render_template("orders.html", orders=db.get_orders(40),limit=40)
    else:
        return render_template("orders.html", orders=db.get_orders(request.form.get('status'),request.form.get('paid'),int(request.form.get('limit'))),limit=request.form.get('limit'),status=request.form.get('status'),paid=request.form.get('paid'))

@app.route("/order",methods=["POST","GET"])
@admin_login_required
def order():
    if request.method == 'POST':
        db.execute(r"UPDATE orders SET paid = ?, status = ? WHERE order_id = ?",request.form.get("paid"),request.form.get("status"),request.form.get("id"))
        return redirect("/orders")
    if not request.args.get("id") or not (order:=db.get_order(request.args.get("id"))):
        return redirect('/orders')
    return render_template("order.html", order=order)
    
@app.route("/i/<int:idint>")
def images(idint):
    try:
        lock.acquire(True)
        result, = db.execute(r"SELECT image FROM images WHERE image_id = ?", idint).pop(0)
    except:
        result, = db.execute(r"SELECT image FROM images WHERE image_id = ?", idint).pop(0)
    finally:
        lock.release()
        image = BytesIO(result)
    return send_file(image,mimetype='image/PNG')

@app.route("/addcatagory", methods=['GET','POST'])
@admin_login_required
def addcatagory():
    if request.method == 'POST':
        if id := db.description(r"SELECT catagory_id FROM catagory WHERE catagory = ?",request.form.get("catagory")):
            return apology("catagory Exsit")
        db.execute(r"INSERT INTO catagory (catagory,sub_catagories) Values (?,?)",request.form.get("catagory"), str(request.form.getlist('sub')))
        return redirect("/addcatagory")
    if request.args.get("c"):
        print(request.args.get("c"))
        c, = db.execute(r"SELECT sub_catagories FROM catagory WHERE catagory = ?", request.args.get("c")).pop(0)
        print(json.dumps(list_return(c)))
        return json.dumps(list_return(c))
    return render_template("addcatagory.html")

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
