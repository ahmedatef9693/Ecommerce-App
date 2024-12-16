import frappe
from frappe.integrations.utils import make_get_request,make_post_request
import random
import requests
import json
BASE_URL = 'https://api.printrove.com/api/external'
SECONDS_IN_YEAR =	365	* 24 * 60 * 60	
headers = {
  'Authorization':'',
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}


def get_token():
	token = frappe.cache().get_value('printrove_access_token')
	if token:
		return token
	ecommerce_setting_doc = frappe.get_cached_doc('Ecommerce Settings')
	response = requests.request('POST',f'{BASE_URL}/token',data={
		'email': ecommerce_setting_doc.email, 
		'password': ecommerce_setting_doc.get_password('password')})
	
	if validate_response(response=response):
		response = json.loads(response.text)
		#store token for a year
		frappe.cache().set_value("printrove_access_token", response['access_token'],expires_in_sec= SECONDS_IN_YEAR)
		return response['access_token']
	else:
		frappe.throw("Error Occured While Getting Access Token")

def get_products(token):
	headers.update({'Authorization':f'Bearer {token}'})
	response = requests.request('GET',f'{BASE_URL}/products',headers=headers)
	
	if validate_response(response=response):
		return json.loads(response.text)
	else:
		frappe.throw("Error In Getting Products")

def get_varaints(printrove_id):
	response = make_get_request(f'{BASE_URL}/products/{printrove_id}',headers=headers)
	variants_list = []
	for variant in response['product']['variants']:
		variants_list.append({
			'variant_id': variant['id'],
			'sku': variant['sku'],
			'color':variant['product']['color'],
			'size':variant['product']['size'],
			'variant_name':variant['product']['name'],
		})
	return variants_list



@frappe.whitelist()
def initializing_data(button = None):
	ecommerce_settings_doc = frappe.get_cached_doc('Ecommerce Settings')
	if button or ecommerce_settings_doc.get_products_data:
		token = get_token()
		products = get_products(token)
		create_store_products(products.get('products'))

def create_store_products(products):
	product_names = []
	for product in products:
		doc = None
		variants = get_varaints(product['id'])
		product_data = {
		'doctype':'Store Product',
		'printrove_id':product['id'],
		'category_id':product.get('product').get('id'),
		'category':product.get('product').get('name'),
		'front_mockup':product['mockup']['front_mockup'],
		'back_mockup':product['mockup']['back_mockup'],
		'is_published':1,
		'retail_price':random.randint(100, 500),
		'variants':variants
		}
		if not frappe.db.exists('Store Product',{'printrove_id':product['id']}):
			product_data.update({'name':product.get('name')})
			product_names.append(product.get('name'))
			doc = frappe.get_doc(product_data).insert(ignore_permissions=True)
			doc.product_description = doc.name
		else:
			doc = frappe.get_doc("Store Product",{'printrove_id':product['id']})
			doc.product_description = doc.name
			product_names.append(doc.name)
			doc.update(product_data)
			doc.save()
			frappe.db.set_value("Store Product",{'printrove_id':product['id']},'name',product.get('name'))
		create_items(product_names)
	return product_names



def create_items(product_names):
	for product in product_names:
		if not frappe.db.exists('Item',product):
			item_data = {'doctype':'Item','item_code':product,'item_group':'Products','stock_uom':'Nos'}
			frappe.get_doc(item_data).insert()



			


def validate_response(response):
	if response.status_code >= 200 and response.status_code <=299:
		return True
	else:
		return False