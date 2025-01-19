# Copyright (c) 2024, Dev.AhmedAtef and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
class StoreOrder(Document):
	@frappe.whitelist()
	def payment_transacton(self,data=None):
		# data = json.loads(data)
		print(f'\n\n{data}\n\n')

		try:
			si_doc = frappe.new_doc('Sales Invoice')
			si_doc.customer = data.get('customer')
			si_doc.company = data.get('company')
			si_doc.custom_order_id = self.order_id
			si_doc.append('items',{})
			si_doc.items[0].item_code = self.product
			si_doc.items[0].qty = self.quantity
			si_doc.items[0].rate = self.retail_price
			si_doc.insert()
			si_doc.submit()
			frappe.db.set_value("Store Order",self.name,'status','Delivered')
		except Exception as e:
			frappe.log_error("Error Occured in Creating Sales Invoice!")


