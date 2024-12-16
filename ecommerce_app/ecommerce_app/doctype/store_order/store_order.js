// Copyright (c) 2024, Dev.AhmedAtef and contributors
// For license information, please see license.txt

frappe.ui.form.on("Store Order", {
  refresh: function (frm) {
    if (frm.doc.status == "Pending") {
      frm.add_custom_button(__("Pay Order"), function () {
        frappe.call({
          method: "ecommerce_app.utils.payment_api.payment_transacton",
          args: { order_name: frm.doc.name },
          callback: (r) => {
            frappe.show_alert({
              message: "Order Paied Successfully!",
              indicator: "green",
            });
            frm.reload_doc();
          },
          error: (r) => {
            // on error
          },
        });
      });
    } else {
      frm.remove_custom_button("Pay Order");
    }
  },
});
