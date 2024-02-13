document.querySelector("#payment_form").addEventListener("submit", (event) => {
  event.preventDefault();
  const form_data = new FormData(event.target);
  let form_data_object = Object.fromEntries(form_data);
  frappe.call({
    method: "ecommerce_app.utils.order_api.handle_checkout_submit",
    args: {
      product_name:document.querySelector("#product_name").textContent.split(":")[1],
      order_data: form_data_object,
    },
    callback: (r) => {
      frappe.show_alert({
        message: "Order Successfully!",
        indicator: "green",
      });
    },
    error: (r) => {
      // on error
    },
  });
  console.log("hello submision of form");
});
