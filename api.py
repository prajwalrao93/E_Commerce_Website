from flask import Flask, request,render_template,redirect,url_for,session,flash,logging
from wtforms import Form,StringField,PasswordField,TextAreaField,RadioField,validators
from wtforms.fields.html5 import EmailField
from passlib.hash import sha256_crypt
from models.user_model import remove_from_cart,product_deletion,user_signup,search_user_by_username,Product_addition,check_user,seller_products,buyer_products,cart_details,update_cart_details,search_products_in_page,buy_product

app = Flask(__name__)

app.config['SECRET_KEY']='hello'
app.config['SERVER_PORT']=5000


@app.route("/")
@app.route("/home")

def home():

	return render_template("home.html")


@app.route("/dashboard")
@app.route("/welcome")
def dashboard():


	if ("user_id" in session.keys()):
		
		
		return render_template('dashboard.html')

		
	else :

		return render_template('login.html')


@app.route("/about")

def about():

	return render_template("about.html")

@app.route("/contact")

def contact():

	return render_template("contact.html")


#follow the below format in wtforms, 1st create a class for every form needed

class RegistrationForm(Form):

	
	name = StringField('Name',[validators.Length(min=4,max=25)])
	username = StringField('Username',[validators.Length(min=4,max=25)])
	email =EmailField('Email address', [validators.DataRequired(), validators.Email()])
	password = PasswordField('Password',[
		validators.Length(min=4,max=25),
		validators.DataRequired(),
		validators.EqualTo('confirm',message="Passwords don't match!")
		])
	confirm = PasswordField('Confirm Password')
	account_type = RadioField('Account Type',choices=[('buyer','Buyer'),('seller','Seller')])
	#message has been initialized in _messages.

@app.route("/register",methods=['GET','POST'])

def register():

	form = RegistrationForm(request.form)
	if request.method == 'POST' and form.validate():
		user_info={}

		user_info["name"] = form.name.data
		user_info["username"] = form.username.data
		user_info["email"] = form.email.data
		user_info["account_type"]=form.account_type.data
		user_info["password"] = sha256_crypt.encrypt(str(form.password.data))

		session["username"]=user_info["name"]
		session["account_type"]=user_info["account_type"]

		if user_info["account_type"]=="buyer":

			user_info["cart"]=[]

		if check_user(user_info["username"]) is None:

			results=user_signup(user_info)
			if(results[0] is True):

				session['user_id'] = str(results[1])
				app.logger.info("SIGNUP SUCCESSFUL")
				flash('signup Sucessful!','success')
			return redirect(url_for('dashboard'))
		
		else:	

			flash('the username already exists.please go back and enter another username','danger')
			return(redirect(url_for('register')))
	else:

		return render_template("register.html",form=form)



@app.route("/login", methods=['GET','POST'])

def login():
	
	#wtforms not needed here

	if request.method == 'POST':

		inbound_username = request.form['username']
		existing_user = search_user_by_username(inbound_username)
		if (existing_user is None):
			app.logger.info("NO USER")
			error="Username or Password is incorrect! Username is case sensitive"
			return render_template('login.html',error=error)

		elif(sha256_crypt.verify(request.form['password'],existing_user['password'])):
			app.logger.info("PASSWORD MATCHED,LOGGING IN")
		
			session['user_id'] = str(existing_user['_id'])
			session['account_type']=existing_user['account_type']
			session['username']=existing_user['username']
		
			flash('Login Sucessful!','success')
			return redirect(url_for('dashboard'))


		else: 
			app.logger.info("WRONG PASSWORD")
			error="Username or Password is incorrect!"
			return render_template('login.html',error=error)

	

	if ("user_id" in session.keys()):
		
		
		return render_template('dashboard.html')

	
	return render_template('login.html')


@app.route("/addproductspage",methods=["POST"])

def addproductspage():
	return render_template('addproducts.html')


@app.route('/addproducts', methods=["POST"])
def addproducts():
	product_info={}
	product_info["product name"] = request.form["name"]
	price = request.form["price"].replace(',','')
	product_info["price"] = int(price)
	product_info["description"] =  request.form["product_description"]
	product_info["user_id"]=session['user_id']
	product_info["username"] =session["username"]
	results =Product_addition(product_info)

	flash('product added!','success')
	return(redirect(url_for('products')))

@app.route('/remove',methods =['GET','POST'])

def removeproducts():
	product_id = request.form["product_id"]
	product_deletion(product_id)
	return redirect((url_for('products')))

@app.route("/products", methods=['POST','GET'])

def products():
	if request.method=='GET' or request.method=='POST':

		if session["account_type"] =="seller":
			result = seller_products(session["user_id"])
		else:
			result = buyer_products()
		return render_template("products.html" ,result=result[0],isproducts=result[1])


@app.route("/searchproducts", methods=["POST"])

def search_products():

	word = request.form["search"]
	search = search_products_in_page(word)
	if search.count()==0:
		isSearch = None
	return render_template("searchproducts.html",search=search,isSearch=isSearch)

	



@app.route('/logout',methods=['GET','POST'])
def logout():
   # remove the username from the session if it is there
   #session.pop('user_id', None)
	if session:
		session.clear()
		flash('You have logged out','success')
		return redirect(url_for('home'))

	else:
		flash('You have not logged in yet','success')
		return redirect(url_for('home'))	

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
	
	product_id =request.form["product_id"]
	quantity=int(request.form["quantity"])
	price=int(request.form["price"])
	session["order_total"]=update_cart_details(session["user_id"],product_id,quantity,price)
	flash('Product has been added to cart','success')
	return redirect(url_for("cart_page"))

@app.route("/remove_from_cart",methods=['POST'])

def remove_cart():

	product_id =request.form["product_id"]
	quantity=int(request.form["quantity"])
	price=int(request.form["price"])
	total =remove_from_cart(session["user_id"],product_id,quantity,price)
	session['order_total'] = total[0]
	if total[1] is True:
		cart= cart_details(session["user_id"])
		cart_value=cart[0] 
		quantity=cart[1]
		return render_template("cart_page.html",cart=zip(cart_value,quantity),order_total=session["order_total"],msg='product has been removed from cart')
	else:
		return render_template("cart_page.html",cart='None',order_total=session["order_total"],msg='No products in your cart.')

@app.route('/cart_page',methods=['GET','POST'])
def cart_page():
	cart= cart_details(session["user_id"])
	if cart[0]=='None':
		session['order_total']=cart[2]
		return render_template("cart_page.html",cart=cart[0],order_total=session["order_total"])	
	else:

		cart_value=cart[0] 
		quantity=cart[1]
		session['order_total']=cart[2]
		return render_template("cart_page.html",cart=zip(cart_value,quantity),order_total=session["order_total"])

@app.route('/buy',methods=['POST'])

def buy():

	cart= cart_details(session["user_id"])
	buy_product(session["user_id"])
	mess='Congratulations,your product will be delivered, free, to your house!(not really)'
	return render_template('purchase.html',cart=zip(cart[0],cart[1]),msg=mess)


if(__name__ == "__main__"):
	app.run(debug=True)