// Copyright (c) 2024, Dev.AhmedAtef and contributors
// For license information, please see license.txt

frappe.ui.form.on("Store Order", {
  refresh: function (frm) {
    if (frm.doc.status == "Pending") {
      frm.add_custom_button(__("Pay Order"), function () {
        get_data_from_user(frm);
      });
    } else {
      frm.remove_custom_button("Pay Order");
    }
  },
});

function get_data_from_user(frm) {
  let d = new frappe.ui.Dialog({
    title: "Enter details",
    fields: [
      {
        label: "Customer Name",
        fieldname: "customer",
        fieldtype: "Link",
        options: "Customer",
      },
      {
        label: "Company Name",
        fieldname: "company",
        fieldtype: "Link",
        options: "Company",
      },
    ],
    size: "small",
    primary_action_label: "Submit",
    primary_action(values) {
      create_sales_invoice(frm, values);
      d.hide();
    },
  });

  d.show();
  return d;
}

function create_sales_invoice(frm, values) {
  frm.call({
    doc: frm.doc,
    method: "payment_transacton",
    args: { data: values },
    callback: function (r) {
      if (r) {
        frappe.show_alert({
          message: "Order Paied Successfully!",
          indicator: "green",
        });
        frm.reload_doc();
        frm.remove_custom_button("Pay Order");
      } else {
        frappe.throw("error occured");
      }
    },
  });
}
