import sqlite3
from flask import redirect, session, render_template
from functools import wraps
import re
from PIL import Image
from tempfile import TemporaryFile
class SQL:
    def __init__(self, filename):
        self.db = sqlite3.connect(filename, check_same_thread=False)
        self.cr = self.db.cursor()
    def execute(self,q,*args):
        l = self.cr.execute(q,args).fetchall()
        self.db.commit()
        return l
    def description(self,q,*args):
        json_data = []
        l = self.cr.execute(q,args)
        des = self.cr.description
        for row in l:
            d = {}
            for i, value in enumerate(row):
                d[des[i][0]] = value
            json_data.append(d)
        return json_data
    def product(self,id):
        if  product := self.description(r"select * from products where id = ?", id):
            images = self.execute(r"select image_id from images where product_id = ?", id)
            imgs = []
            for img in images:
                imgs.append(img[0])
            product[0]['images'] = imgs
            product[0]['range'] = range(0,len(imgs))
            return product[0]
        else:
            return None
    def cart(self,id):
        cart = self.execute(r"SELECT cart FROM customers WHERE id = ?",id)
        return cart[0][0]
    def products(self,cart: dict) -> list:
        if not cart:
            return None, 0
        if len(cart) > 1:
            products = self.description(f"select * from products where id in {tuple(cart)}")
        else:
            products = self.description(f"select * from products where id = ?", *cart)
        total = 0
        for product in products:
            images = self.execute("select image_id from images where product_id = ?", product['id'])
            imgs = []
            total += product['price'] * cart[str(product['id'])]
            for img in images:
                imgs.append(img[0])
            product['images'] = imgs
            product['range'] = range(0,len(imgs))
            product['number'] = cart[str(product['id'])]
        return [products, total]
    def get_adresses(self,id):
        return self.description(r"SELECT adress_id,adress,phone FROM Adresses WHERE customer_id = ?", id)
    def get_orders(self,status=None,paid=None,limit=10):
        if (not (status or paid)) or (status not in ['pending','return','inprogress', 'indelivery','delivered','all']) or (paid not in ['paid','due','all']) or (status == 'all' and paid == 'all'):
            return self.description(r"SELECT order_id,orders.cart,orders.total,adress,Adresses.phone,status,paid,fname FROM orders JOIN customers ON orders.customer_id = id JOIN Adresses ON orders.adress_id = Adresses.adress_id ORDER BY order_id DESC LIMIT ?",limit)
        status = status if status != "all" else None
        paid = paid if paid != "all" else None
        if status and paid:
            return self.description(r"SELECT order_id,orders.cart,orders.total,adress,Adresses.phone,status,paid,fname FROM orders JOIN customers ON orders.customer_id = id JOIN Adresses ON orders.adress_id = Adresses.adress_id WHERE status = ? AND paid = ? ORDER BY order_id DESC LIMIT ?",status,paid,limit)
        if status:
            return self.description(r"SELECT order_id,orders.cart,orders.total,adress,Adresses.phone,status,paid,fname FROM orders JOIN customers ON orders.customer_id = id JOIN Adresses ON orders.adress_id = Adresses.adress_id WHERE status = ? ORDER BY order_id DESC LIMIT ?",status,limit)
        if paid:
            return self.description(r"SELECT order_id,orders.cart,orders.total,adress,Adresses.phone,status,paid,fname FROM orders JOIN customers ON orders.customer_id = id JOIN Adresses ON orders.adress_id = Adresses.adress_id WHERE paid = ? ORDER BY order_id DESC LIMIT ?",paid,limit)
    def get_order(self,id):
        if id is int:
            return None
        order = self.description(r"SELECT order_id,date,orders.cart,orders.total,adress,Adresses.phone,status,paid,fname,lname FROM orders JOIN customers ON orders.customer_id = id JOIN Adresses ON orders.adress_id = Adresses.adress_id WHERE order_id = ? ",id)
        if order:
            order[0]['cart'] = self.products(cart_saving(order[0]['cart'])).pop(0)
            order[0]['phone'] = str(order[0]['phone']).zfill(11)
            return order[0]
        return None
    def get_orders_details(self):
        data = {}
        for _ in self.execute(r"SELECT status,COUNT(total) FROM orders GROUP BY status"):
            data[_[0]] = _[1]
        for _ in self.execute(r"SELECT paid,COUNT(total) FROM orders GROUP BY paid"):
            data[_[0]] = _[1]
        data['total_due'], = self.execute(r"SELECT SUM(total) FROM orders WHERE paid = 'due'").pop(0)
        data['orders_count'], = self.execute(r"SELECT COUNT(total) FROM orders WHERE NOT (paid,status) = ('paid','delivered')").pop(0)
        return data




def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
def admin_login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin_id") is None:
            return redirect("/adminslogin")
        return f(*args, **kwargs)
    return decorated_function
def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code
def cart_saving(cart:str)-> dict:
    """taking a string represents a dict of a cart {'1': 2, '3': 4}"""
    cart = cart.replace("{","").replace("}","").split(", ")
    dict = {}
    for item in cart:
        try:
            d = re.search("'(\d+)': *(\d+)",item)
            dict[d.group(1)] = int(d.group(2))
        except:
            pass
    return dict
def is_not_phone(phone: str) -> bool:
    """Take a string of a phone number and check if it's valid or not"""
    if re.search("^01\d{9}$",phone):
        return False
    return True
def list_return(s:str) -> list:
    """take a string reprisents list and return it as list"""
    s = s[1:-1].split(", ")
    l = []
    for i in s:
        l.append(i.strip("'"))
    return l

# db = SQL("database.db")
# img = Image.open(r"E:\CS50\CS50x\finalProject\static\productimages\1.png")
# img = img.resize((200,200))
# fp = TemporaryFile()
# img.save(fp,'PNG')
# fp.seek(0)
# db.execute(r"INSERT INTO images (product_id,image) VALUES (?,?)", 5,fp)
# with open("son.png", 'wb') as img:
#     print(img)
#     imge, = db.execute(r"SELECT image FROM images WHERE image_id = '17'").pop(0)
#     img.write(imge)

