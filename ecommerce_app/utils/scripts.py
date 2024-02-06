import frappe
from frappe.integrations.utils import make_get_request,make_post_request

BASE_URL = 'https://api.printrove.com/api/external'
headers = {
  'Authorization':'',
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}









def get_token():
	ecommerce_setting_doc = frappe.get_doc('Ecommerce Settings')
	response = make_post_request(f'{BASE_URL}/token',data={
		'email': ecommerce_setting_doc.email, 
		'password': ecommerce_setting_doc.get_password('password')})
	return response['access_token']

def get_products(token):
	headers.update({'Authorization':f'Bearer {token}'})
	return make_get_request(f'{BASE_URL}/products',headers=headers)


def initializing_data():
	token = get_token()
	products = get_products(token)
	products = products.get('products')

	for product in products:
		doc = None
		values = {
			'doctype':'Store Product',
			'name':product.get('name'),
			'printrove_id':product['id'],
			'front_mockup':product['mockup']['front_mockup'],
			'back_mockup':product['mockup']['back_mockup']
			}
		if not frappe.db.exists('Store Product',{'name':product['name']}):
			doc = frappe.get_doc(values).insert(ignore_permissions=True)
		else:
			doc = frappe.db.set_value('Store Product', product['name'], {
				'printrove_id':product['id'],
				'front_mockup':product['mockup']['front_mockup'],
				'back_mockup':product['mockup']['back_mockup']
				})

			


