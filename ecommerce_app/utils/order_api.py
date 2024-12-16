from ecommerce_app.utils.constants import *
import frappe
import requests
import json
from ecommerce_app.utils.tokens import get_token
from ecommerce_app.utils.payment_api import get_payments_data

@frappe.whitelist()
def handle_checkout_submit(product_name =None,order_data = None):
	order_data = json.loads(order_data)
	paymob_token = get_token("paymob_access_token")
	url = make_order_pay(paymob_token,product_name,order_data)
	return url

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
		try:
			response = requests.request("POST",f"{BASE_URL}ecommerce/orders",headers=HEADERS,data=order)
			response = json.loads(response.text)
			order_id = response.get('id')
			create_order(response)
		except Exception as e:
			frappe.throw("An Error Occured While Processing Order {0}".format(e))
		integration_id = paymob_setting_doc.integration_id
		payments_access_token = get_payments_data(token,order_id,integration_id,order_data,store_product_doc,ecommerce_setting_doc)	
		external_url = f"https://accept.paymob.com/api/acceptance/iframes/824545?payment_token={payments_access_token}"
		return external_url
	else:
		frappe.throw("Check Price Of Current Product")



def create_order(order_response):
	print("Order Response")
	print(f"\n\n{order_response}\n\n")
	store_order_doc = frappe.new_doc('Store Order')
	store_order_doc.order_id = order_response.get('id')
	store_order_doc.status = 'Pending'
	shipping_data = order_response.get('shipping_data')
	if shipping_data:
		store_order_doc.phone_number = shipping_data.get('phone_number')
		if user_exist(shipping_data.get('email')):
			store_order_doc.user = shipping_data.get('email')
		store_order_doc.customer_name = shipping_data.get('last_name')
		store_order_doc.country = shipping_data.get('country')
		store_order_doc.state = shipping_data.get('city')
		store_order_doc.address_line_1 = shipping_data.get('building') + ',' + shipping_data.get('street') + ' st.'+ shipping_data.get('floor') + ' fl.' +','+shipping_data.get('apartment')
		store_order_doc.address_line_2 = shipping_data.get('building') + ',' + shipping_data.get('street') + ' st.'+ shipping_data.get('floor') + ' fl.' +','+shipping_data.get('apartment')
		if shipping_data.get('postal_code'):
			store_order_doc.pincode = shipping_data.get('postal_code')
		else:
			store_order_doc.pincode = '0123'
	store_order_doc.currency_type = order_response.get('currency')
	if len(order_response.get('items')) > 0:
		print(f'\n\n{order_response.get("items")}\n\n')
		for item in order_response.get('items'):
			store_order_doc.paid_amount = item.get('amount_cents')
			store_order_doc.quantity = item.get('quantity')
			store_order_doc.product = get_product_by_sku(item.get('name'))
	try:
		store_order_doc.docstatus = 1
		store_order_doc.insert()
	except Exception as e:
		frappe.throw(f"Error While inserting order {e}")
	frappe.msgprint(f'Order Created <a href="../store-order/{store_order_doc.name}" target="_blank"><strong>{store_order_doc.name}</strong></a>')


def validate_retal_price(retail_price):
	if retail_price <= 0 or not retail_price:
		return False
	else:
		return True
	

def get_product_by_sku(sku):
	return frappe.db.get_value('Store Product Variant',{'sku':sku},'parent')


def user_exist(email):
	return frappe.db.exists('User',{'email':email})