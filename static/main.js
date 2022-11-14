// search bar CODE -----------------------------
let search = document.querySelector("#search");
function search_li_q() {
  let search_li = document.querySelectorAll(".sl");
  for (let li of search_li) {
    li.addEventListener("click", () => {
      search.value = li.innerHTML;
    });
  }
}

search.addEventListener("input", () => {
  if (search.value) {
    fetch(`/search?q=${search.value}`)
      .then((response) => {
        response = response.json();
        return response;
      })
      .then((res) => {
        let auto_copm = document.querySelector(".auto-comp");
        let searchQ = "";
        for (i of res) {
          searchQ += `<li onclick='set(this)'>${i.name}</li>`;
        }
        auto_copm.innerHTML = searchQ;
      });
  }
});
function set(element) {
  search.value = element.innerHTML;
}

document.querySelector(".search").addEventListener("submit", (event) => {
  if (!search.value) {
    event.preventDefault();
  }
});
// SEARCH BAR END ----------------------------------
// cart start     ----------------------------------
let carts = document.querySelectorAll(".cart-btn");
let buynows = document.querySelectorAll(".buy-btn");
let massage = document.querySelector(".massage");
let msg_btn = document.querySelector(".massage button");
for (let cart of carts) {
  cart.addEventListener("click", (event) => {
    event.preventDefault();
    fetch(`/cart?i=${cart.getAttribute("title")}`);
    massage.style.display = "block";
  });
}
for (let buy of buynows) {
  buy.addEventListener("click", () => {
    fetch(`/cart?i=${buy.getAttribute("title")}`);
    setTimeout(() => {
      window.location.href = "/cart";
    }, 500);
  });
}
// cart remove btn
let removes = document.querySelectorAll(".remove");
for (let remove of removes) {
  remove.addEventListener("click", (event) => {
    event.preventDefault();
    fetch(`/cart?r=${remove.getAttribute("title")}`)
      .then((response) => {
        response = response.json();
        return response;
      })
      .then((res) => {
        [...document.querySelectorAll(".cart-total")].forEach((tot) => {
          tot.innerHTML = res.total;
        });
      });
    document
      .querySelector(`div.cart-card[title='${remove.getAttribute("title")}']`)
      .remove();
  });
}
// cart countity number
let numbers = document.querySelectorAll(".number");
let change = new Event("change");
for (let number of numbers) {
  let input = number.querySelector("input");
  input.addEventListener("change", () => {
    if (input.value === "0") {
      document
        .querySelector(`div.cart-card[title='${input.getAttribute("title")}']`)
        .remove();
    }
    fetch(`/cart?n=${input.value}` + `&id=${input.getAttribute("title")}`)
      .then((response) => {
        response = response.json();
        return response;
      })
      .then((res) => {
        [...document.querySelectorAll(".cart-total")].forEach((tot) => {
          tot.innerHTML = res.total;
        });
      });
  });
  number.querySelector(".plus").addEventListener("click", () => {
    input.value = Number(input.value) + 1;
    input.dispatchEvent(change);
  });
  number.querySelector(".minus").addEventListener("click", () => {
    input.value = Number(input.value) - 1;
    input.dispatchEvent(change);
  });
}
// buy start
let radios = document.querySelectorAll(".radio input[type='radio']");
for (let radi of radios) {
  radi.addEventListener("change", () => {
    [...document.querySelectorAll(".adress label")].forEach((label) => {
      label.classList.remove("active");
    });
    document.querySelector(`label[for="${radi.id}"]`).classList.add("active");
  });
}
// CART END    ----------------------------------
msg_btn.onclick = () => {
  massage.style.display = "none";
};
// swiper start
let swiper = document.querySelector(".slider .slides");
let margin = document.querySelector(".slides .img-box:first-child");
let Xstart, index;
let radio = document.querySelectorAll("input[type='radio']");
swiper.addEventListener("touchstart", (event) => {
  for (let i = 0; i < radio.length; i++) {
    if (radio[i].checked) {
      index = i;
      break;
    }
  }
  Xstart = event.targetTouches.item(0).clientX;
});

swiper.addEventListener("touchend", (e) => {
  if (Xstart - e.changedTouches.item(0).clientX > 100) {
    if (index < 3) {
      radio[index + 1].checked = true;
    } else {
      radio[3].checked = true;
      console.log(index);
    }
  } else if (Xstart - e.changedTouches.item(0).clientX < -100) {
    if (index > 0) {
      radio[index - 1].checked = true;
    } else {
      radio[0].checked = true;
    }
  } else {
    radio[index].checked = true;
  }
});
// Swiper end
