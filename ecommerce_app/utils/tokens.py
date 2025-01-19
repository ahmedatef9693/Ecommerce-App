import frappe
import json
import requests
from ecommerce_app.utils.constants import *


def get_token(token_name,payment_data = None):
	token = ''
	if token_name == "paymob_access_token":
		token = frappe.safe_decode(frappe.cache().get('paymob_access_token'))
		if token:
			return token
		paymob_setting_doc = frappe.get_cached_doc('PayMob Settings')
		payload = json.dumps({'api_key':paymob_setting_doc.api_key})
		response = json.loads(requests.request("POST", f"{BASE_URL}auth/tokens", headers=PAYMOB_HEADERS, data=payload).text)
		#store token for a 50 minutes at server it expires after 60 minutes 
		frappe.cache().setex("paymob_access_token",TOKEN_EXIPRY_TIME ,response['token'])
		return response['token']
	elif token_name == "payment_access_token":
		if payment_data:
			response = requests.request("POST",f"{BASE_URL}acceptance/payment_keys",headers=PAYMOB_HEADERS,data=payment_data).text
			response = json.loads(response)
			return response.get('token')