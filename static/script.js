window.onload = function () {
  let password = document.querySelector("#password");
  let confirmation = document.querySelector("#confirmation");
  let confirm = document.querySelector("#confirm");
  let form = document.querySelector("form");

  function type() {
    if (password.value !== confirmation.value) {
      confirm.innerHTML = "Passwords Don't Match";
      confirm.style.color = "red";
    } else {
      confirm.innerHTML = "Passwords Match";
      confirm.style.color = "green";
    }
  }
  password.addEventListener("input", type);
  confirmation.addEventListener("input", type);
  form.addEventListener("submit", (event) => {
    if (password.value !== confirmation.value) {
      event.preventDefault();
    }
  });
};

let removes = document.querySelectorAll(".remove");
for (let remove of removes) {
  remove.addEventListener("click", () => {
    fetch(`/cart?r=${remove.getAttribute("title")}`)
      .then((response) => {
        response = response.json();
        return response;
      });
    document
      .querySelector(
        `div.product-card[title='${remove.getAttribute("title")}']`
      )
      .remove();
  });
}
