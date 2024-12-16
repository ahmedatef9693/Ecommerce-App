// Copyright (c) 2024, Dev.AhmedAtef and contributors
// For license information, please see license.txt

frappe.ui.form.on("Ecommerce Settings", {
  refresh: function (frm) {
    frm.add_custom_button(__("Sync Products Now"), () => {
      frappe.call({
        method: "ecommerce_app.utils.scripts.initializing_data",
        args: { button: true },
        callback: (r) => {
          frappe.show_alert({
            message: "Products Updated Successfully!",
            indicator: "green",
          });
        },
        error: (r) => {
          // on error
        },
      });
    });
  },
});
