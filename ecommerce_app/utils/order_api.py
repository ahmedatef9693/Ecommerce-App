import frappe
import json

@frappe.whitelist()
def handle_checkout_submit(product_name =None,order_data = None):
    print(f"\n\n{product_name}\n\n")
    print(f"\n\n{order_data}\n\n")


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
    
