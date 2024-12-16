import frappe
import json
import requests
from ecommerce_app.utils.constants import *


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
			response = requests.request("POST",f"{BASE_URL}acceptance/payment_keys",headers=HEADERS,data=payment_data).text
			response = json.loads(response)
			frappe.cache().set_value("payment_access_token", response.get('token'),expires_in_sec= TOKEN_EXIPRY_TIME)
			return response.get('token')