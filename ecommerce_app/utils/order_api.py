import frappe
import requests
import json
# from frappe.integrations.utils import make_get_request,make_post_request

BASE_URL =  "https://accept.paymob.com/api/"
HEADERS = {
  'Content-Type': 'application/json'
}
TOKEN_EXIPRY_TIME = 55 * 60

@frappe.whitelist()
def handle_checkout_submit(product_name =None,order_data = None):
	order_data = json.loads(order_data)
	token = paymob_token()
	make_order_pay(token,product_name,order_data)




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
	store_order_doc = frappe.get_cached_doc("Store Product",product_name)
	ecommerce_setting_doc = frappe.get_cached_doc('Ecommerce Settings')
	paymob_setting_doc = frappe.get_cached_doc('PayMob Settings')
	sku = frappe.db.get_value('Store Product Variant', filters={'parent': product_name,'color':order_data['color']}, fieldname='sku')
	order = {
	"auth_token": token,
  	"delivery_needed": "true",
	"amount_cents": store_order_doc.retail_price * 100,
	"currency": "EGP",
	"items": [
		{
			"name": sku,
			"amount_cents": store_order_doc.retail_price * 100,
			"description": store_order_doc.product_description,
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
	
	print(f'\n\n\n{order_id}\n\n\n')
	print(f'\n\n\n{integration_id}\n\n\n')


	payment_data={
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
	response = requests.request("POST",f"{BASE_URL}ecommerce/orders",headers=HEADERS,data=payment_data).text
	response = json.loads(response)
	print('\n\n\npayment token\n\n\n\n')
	print(response.get('token'))

	
	  
	 


def paymob_token():
	token = frappe.cache().get_value('paymob_access_token')
	if token:
		return token
	paymob_setting_doc = frappe.get_cached_doc('PayMob Settings')
	payload = json.dumps({'api_key':paymob_setting_doc.api_key})
	response = json.loads(requests.request("POST", f"{BASE_URL}auth/tokens", headers=HEADERS, data=payload).text)
	#store token for a 55 minutes at server it expires after 60 minutes 
	frappe.cache().set_value("paymob_access_token", response['token'],expires_in_sec= TOKEN_EXIPRY_TIME)
	return response['token']
	