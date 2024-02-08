# Copyright (c) 2024, Dev.AhmedAtef and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator

class StoreProduct(WebsiteGenerator):
	

	def get_context(self,context):
		context.add_breadcrumbs = 1
		context.parents = [
			{"label":"Store","route":"/products"},
			{"label":self.category,"route":f"/products"}
		]
		settings = frappe.get_cached_doc('Ecommerce Settings')
		if settings.use_custom_product_view_template:
			rendered_html_template = frappe.render_template(settings.custom_product_view_template,{"doc":self})
			context.rendered_html_template = rendered_html_template



