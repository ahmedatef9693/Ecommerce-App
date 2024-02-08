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

@frappe.whitelist()
def initializing_data():
	token = get_token()
	products = get_products(token)
	products = products.get('products')
	for product in products:
		doc = None
		product_data = {
		'name':product.get('name'),
		'category_id':product.get('product').get('id'),
		'category':product.get('product').get('name'),
		'front_mockup':product['mockup']['front_mockup'],
		'back_mockup':product['mockup']['back_mockup']
		}
		values = {
			'doctype':'Store Product',
			'printrove_id':product['id'],
			**product_data
			}
		if not frappe.db.exists('Store Product',{'printrove_id':product['id']}):
			doc = frappe.get_doc(values).insert(ignore_permissions=True)
		else:
			doc_name = frappe.db.sql(f"""select name from `tabStore Product` where printrove_id = {product['id']}""",as_dict=True)[0].name
			doc = frappe.db.set_value('Store Product', doc_name, {
				**product_data
				})

			


