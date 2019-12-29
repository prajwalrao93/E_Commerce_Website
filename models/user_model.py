from pymongo import MongoClient
from bson.objectid import ObjectId


client = MongoClient()
db = client['dummy_amazon']


def user_signup(user_info):
	#save user info dictionary inside mongo
	results = db['users'].insert_one(user_info)
	filter_query = {'username' :user_info['username']}
	results= db['users'].find_one(filter_query)
	
	return (True,results['_id']) 

def check_user(username):
	
	filter_query = {'username' :username}
	results= db['users'].find(filter_query)

	if(results.count()>0):
		return results.next()

	else:
		return None

def Product_addition(product_info):
	#saves the products inside mongoDB
	results = db['products'].insert_one(product_info)

	return True

def product_deletion(product_id):
	
	filter_query = {"_id" : ObjectId(product_id)}
	db['products'].remove(filter_query)


def search_user_by_username(username):
	filter_query = {'username' :username}
	results = db['users'].find(filter_query)

	if(results.count()>0):
		return results.next()

	else:
		return None 



def products_by_username(username):
    filter_query = {'username' : username}
    results = db['products'].find(filter_query)
    results['product name']


def seller_products(user_id):
	ans =[]
	filter_query = {'user_id': user_id}
	results = db["products"].find(filter_query)
	for post in results:
		ans.append(post)
	if not ans:
		return (ans,'no')

	else:

		return(ans, 'yes')

def buyer_products():
	ans =[]
	result = db["products"].find({})	
	for post in result:
		ans.append(post)

	if not ans:
		return (ans,'no')

	else:

		return(ans, 'yes')

	
def cart_details(user_id):
	results =[]
	quantity=[]
	filter_query1 = {"_id":ObjectId(user_id)}
	result = db["users"].find_one(filter_query1)
	cart_list=result["cart"]
	total=0

	if not cart_list:

		return('None','There is nothing in your cart',total)

	else:

		for item in cart_list:
			filter_query2 = {"_id":ObjectId(item["product_id"])}
			results.append(db["products"].find_one(filter_query2))
			quantity.append(item['quantity'])
		
		user_info = db["users"].find_one({"_id":ObjectId(user_id)})	
		cart_dict = user_info.get("cart")

		for dict1 in cart_dict:
			total+=dict1["price"]*dict1["quantity"]
		return (results,quantity,total)


def update_cart_details(user_id,product_id,quantity,price):

	user_info = db["users"].find_one({"_id":ObjectId(user_id)})
	cart_dict = user_info.get("cart")
	product_index = None
	total = 0
	
		
	for dict1 in cart_dict:

		if dict1["product_id"]==product_id:

			product_index=cart_dict.index(dict1) + 1

	if bool(product_index) == True:


		db["users"].update({"_id" : ObjectId(user_id),"cart.product_id":product_id},{ '$inc':{ 'cart.$.quantity':quantity}})
		

	else:

		db["users"].update({"_id":ObjectId(user_id)},{"$addToSet":{"cart":{"$each":[{"product_id":product_id,"quantity":quantity,"price":price }]}}})
	
	user_info = db["users"].find_one({"_id":ObjectId(user_id)})	
	cart_dict = user_info.get("cart")

	for dict1 in cart_dict:

		total+=dict1["price"]*dict1["quantity"]

	return total

def remove_from_cart(user_id,product_id,quantity,price):


	user_info = db["users"].find_one({"_id":ObjectId(user_id)})
	cart_dict = user_info.get("cart")
	total =0 

	for dict1 in cart_dict:

		if dict1["product_id"]==product_id:


			if dict1["quantity"]==quantity:
				db["users"].update({"_id":ObjectId(user_id)},{"$pull":{"cart":{"product_id":product_id,"quantity":quantity,"price":price }}})

				user_info = db["users"].find_one({"_id":ObjectId(user_id)})	
				cart_dict = user_info.get("cart")
				
				if not cart_dict:
						return (total,False)
				else:

					for dict1 in cart_dict:
						if (dict1["price"] is None) or (dict1["quantity"] is None):
							total=0
						else: 
							total+=dict1["price"]*dict1["quantity"]

					return (total,True)
				
			else:
				db["users"].update({"_id" : ObjectId(user_id),"cart.product_id":product_id},{ '$inc':{ 'cart.$.quantity':-quantity}})
				user_info = db["users"].find_one({"_id":ObjectId(user_id)})	
				cart_dict = user_info.get("cart")

				for dict1 in cart_dict:

					total+=dict1["price"]*dict1["quantity"]

				return (total,True)
			
	


def search_products_in_page(search):

	result=[]
	filter_query = {"product name" : search}
	result = db['products'].find(filter_query)
	return result

def buy_product(user_id):

	db["users"].update({"_id":ObjectId(user_id)},{"$unset":{ "cart":1}})
	db["users"].update({"_id":ObjectId(user_id)},{"$set":{ "cart":[]}})

	return True
