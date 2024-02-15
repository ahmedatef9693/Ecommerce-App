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
    print(f"\n\n{product_name}\n\n")
    print(f"\n\n{order_data}\n\n")
    token = paymob_token()
    make_order_pay(token)




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
    


def make_order_pay(token):
	print(f"\n\n{token}\n\n")
      
     


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
	