import frappe
import requests
import json
# from flask import redirect

# from frappe.integrations.utils import make_get_request,make_post_request

BASE_URL =  "https://accept.paymob.com/api/"
HEADERS = {
  'Content-Type': 'application/json'
}
TOKEN_EXIPRY_TIME = 55 * 60

@frappe.whitelist()
def handle_checkout_submit(product_name =None,order_data = None):
	order_data = json.loads(order_data)
	paymob_token = get_token("paymob_access_token")
	url = make_order_pay(paymob_token,product_name,order_data)
	return url




@frappe.whitelist()
def get_colors_of_size(product_size,product_name):
	colors = [
	   current_color.color for current_color in frappe.db.sql("""
												   select 
													   color 
												   from 
													   `tabStore Product Variant` 
												   where 
													   size = %(size)s 
												   and 
													   parent = %(parent)s
												   """,values={
													   'size':product_size,
													   'parent':product_name
													   },
													as_dict=True)]
	return colors
	


def make_order_pay(token,product_name,order_data):
	store_product_doc = frappe.get_cached_doc("Store Product",product_name)
	ecommerce_setting_doc = frappe.get_cached_doc('Ecommerce Settings')
	paymob_setting_doc = frappe.get_cached_doc('PayMob Settings')
	sku = frappe.db.get_value('Store Product Variant', filters={'parent': product_name,'color':order_data['color']}, fieldname='sku')
	order = ''
	if validate_retal_price(store_product_doc.retail_price):
		order = {
		"auth_token": token,
		"delivery_needed": "true",
		"amount_cents": store_product_doc.retail_price * 100,
		"currency": "EGP",
		"items": [
			{
				"name": sku,
				"amount_cents": store_product_doc.retail_price * 100,
				"description": store_product_doc.product_description,
				"quantity": "1"
			},
		],
		"shipping_data": {
			"apartment": "1", 
			"email": ecommerce_setting_doc.email, 
			"floor": "2", 
			"first_name": "Mr", 
			"street": order_data.get("address_line_1"), 
			"building": order_data.get("address_line_2"), 
			"phone_number": order_data.get("phone_number"), 
			"postal_code": order_data.get("pincode"), 
			"extra_description": order_data.get("address_line_3"),
			"city": order_data.get("city"), 
			"country": order_data.get("country"), 
			"last_name": order_data.get("customer_name"), 
			"state": order_data.get("state")
		},
		"shipping_details": {
			"notes" : "s",
			"number_of_packages": 1,
			"weight" : 1,
			"weight_unit" : "",
			"length" : 1,
			"width" :1,
			"height" :1,
			"contents" : "product of some sorts"
		}
		}
		order = json.dumps(order)
		response = requests.request("POST",f"{BASE_URL}ecommerce/orders",headers=HEADERS,data=order).text
		response = json.loads(response)
		order_id = response.get('id')
		integration_id = paymob_setting_doc.integration_id
		payments_access_token = get_payments_data(token,order_id,integration_id,order_data,store_product_doc,ecommerce_setting_doc)	
		print(f'\n\n\npayment access token\n\n\n')
		print(f'\n\n\n{payments_access_token}\n\n\n')
		external_url = f"https://accept.paymob.com/api/acceptance/iframes/824545?payment_token={payments_access_token}"
		return external_url
	else:
		frappe.throw("Check Price Of Current Product")




def get_token(token_name,payment_data = None):
	token = ''
	if token_name == "paymob_access_token":
		token = frappe.cache().get_value('paymob_access_token')
		if token:
			return token
		paymob_setting_doc = frappe.get_cached_doc('PayMob Settings')
		payload = json.dumps({'api_key':paymob_setting_doc.api_key})
		response = json.loads(requests.request("POST", f"{BASE_URL}auth/tokens", headers=HEADERS, data=payload).text)
		#store token for a 55 minutes at server it expires after 60 minutes 
		frappe.cache().set_value("paymob_access_token", response['token'],expires_in_sec= TOKEN_EXIPRY_TIME)
		return response['token']
	elif token_name == "payment_access_token":
		token = frappe.cache().get_value("payment_access_token")
		if token:
			return token
		if payment_data:
			print('\n\nEnter again\n\n\n')
			print(f'\n\n{payment_data}\n\n\n')
			response = requests.request("POST",f"{BASE_URL}acceptance/payment_keys",headers=HEADERS,data=payment_data).text
			response = json.loads(response)
			print(f'\n\n{response}\n\n\n')
			frappe.cache().set_value("payment_access_token", response.get('token'),expires_in_sec= TOKEN_EXIPRY_TIME)
			return response.get('token')





def get_payments_data(token,order_id,integration_id,order_data,store_order_doc,ecommerce_setting_doc):
	payment_data = {
		"auth_token": token,
		"amount_cents": store_order_doc.retail_price * 100, 
		"expiration": 3600, 
		"order_id": str(order_id),
		"billing_data": {
			"apartment": "1", 
			"email": ecommerce_setting_doc.email, 
			"floor": "2", 
			"first_name": "Mr", 
			"street": order_data.get("address_line_1"), 
			"building": order_data.get("address_line_2"), 
			"phone_number": order_data.get("phone_number"), 
			"shipping_method": "PKG", 
			"postal_code": order_data.get("pincode"), 
			"city": order_data.get("city"), 
			"country": order_data.get("country"), 
			"last_name": order_data.get("customer_name"), 
			"state": order_data.get("state")
		}, 
		"currency": "EGP", 
		"integration_id": integration_id,
		"lock_order_when_paid": "false"
		}
	payment_data = json.dumps(payment_data)
	payment_access_token = get_token("payment_access_token",payment_data = payment_data)
	return payment_access_token



def validate_retal_price(retail_price):
	if retail_price <= 0 or not retail_price:
		return False
	else:
		return True