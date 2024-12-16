import json
from ecommerce_app.utils.tokens import get_token
import frappe

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

@frappe.whitelist()
def payment_transacton(order_name):
	store_order = frappe.get_cached_doc('Store Order',order_name)
	try:
		si_doc = frappe.new_doc('Sales Invoice')
		si_doc.customer = 'ahmed'
		si_doc.company = 'A&A'
		si_doc.custom_order_id = store_order.order_id
		si_doc.append('items',{})
		si_doc.items[0].item_code = store_order.product
		si_doc.items[0].qty = store_order.quantity
		si_doc.items[0].rate = store_order.retail_price
		si_doc.insert()
		si_doc.submit()
		frappe.db.set_value("Store Order",store_order.name,'status','Delivered') 
	except Exception as e:
		frappe.log_error("Error Occured in Creating Sales Invoice!")