import json
from ecommerce_app.utils.tokens import get_token


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