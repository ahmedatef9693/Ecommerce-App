import frappe

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