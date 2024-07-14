document.querySelector("#payment_form").addEventListener("submit", (event) => {
  event.preventDefault();
  const form_data = new FormData(event.target);
  let form_data_object = Object.fromEntries(form_data);
  frappe.call({
    method: "ecommerce_app.utils.order_api.handle_checkout_submit",
    args: {
      product_name: get_product_name(),
      order_data: form_data_object,
    },
    callback: (r) => {
      frappe.show_alert({
        message: "Order Successfully!",
        indicator: "green",
      });
      window.location.href = r.message;
    },
    error: (r) => {
      // on error
    },
  });
  console.log("hello submision of form");
});

document
  .getElementById("product_size")
  .addEventListener("change", function (event) {
    let product_name = get_product_name();
    let product_size = this.value;

    frappe.call({
      method: "ecommerce_app.utils.order_api.get_colors_of_size",
      args: {
        product_size: product_size,
        product_name: product_name,
      },
      callback: (r) => {
        let select_element = document.querySelector("#product_color");
        select_element.innerHTML = "";
        let option_element = ``;
        r.message.forEach((current_color) => {
          option_element += `<option value="${current_color}">${current_color}</option>`;
          select_element.innerHTML = option_element;
        });
      },
      error: (r) => {
        frappe.throw("Failed to get colors");
      },
    });
  });

function get_product_name() {
  return document
    .querySelector("#product_name")
    .textContent.split(":")[1]
    .trim();
}
