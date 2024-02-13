import frappe


@frappe.whitelist()
def handle_checkout_submit(product_name =None,order_data = None):
    print(f"\n\n{product_name}\n\n")
    print(f"\n\n{order_data}\n\n")