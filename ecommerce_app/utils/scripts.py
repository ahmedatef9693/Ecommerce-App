import frappe
from frappe.integrations.utils import make_get_request,make_post_request

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
	response = make_post_request(f'{BASE_URL}/token',data={
		'email': ecommerce_setting_doc.email, 
		'password': ecommerce_setting_doc.get_password('password')})
	#store token for a year
	frappe.cache().set_value("printrove_access_token", response['access_token'],expires_in_sec= SECONDS_IN_YEAR)
	return response['access_token']

def get_products(token):
	headers.update({'Authorization':f'Bearer {token}'})
	return make_get_request(f'{BASE_URL}/products',headers=headers)

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
def initializing_data():
	token = get_token()
	products = get_products(token)
	products = products.get('products')
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
		'variants':variants
		}
		if not frappe.db.exists('Store Product',{'printrove_id':product['id']}):
			product_data.update({'name':product.get('name')})
			doc = frappe.get_doc(product_data).insert(ignore_permissions=True)
			doc.product_description = doc.name
		else:
			doc = frappe.get_doc("Store Product",{'printrove_id':product['id']})
			doc.product_description = doc.name
			doc.update(product_data)
			doc.save()
			frappe.db.set_value("Store Product",{'printrove_id':product['id']},'name',product.get('name'))



	


			


