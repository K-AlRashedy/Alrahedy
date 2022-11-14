// Selection start
document.querySelector("#catagory").addEventListener("change", (e) => {
  fetch(`/addcatagory?c=${e.target.value}`)
    .then((response) => {
      response = response.json();
      return response;
    })
    .then((res) => {
      let sub_catagory = document.querySelector("#sub-catagory");
      sub_catagory.innerHTML = "";

      for (let sub of res) {
        sub_catagory.innerHTML += `<option value="${sub}">${sub}</option>`;
      }
    });
});
// Selection End
// main start
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

// display an uploaded image
for (let i = 0; i < 4; i++) {
  let uploaded_image = "";
  document.querySelector(`input#image${i}`).addEventListener("change", () => {
    let file = document.querySelector(`input#image${i}`).files[0];
    const reader = new FileReader();
    reader.addEventListener("load", () => {
      uploaded_image = reader.result;
      document.querySelector(
        `label[for='image${i}']`
      ).innerHTML = `<img src='${uploaded_image}'>`;      
      document.querySelector(
        `label[for='radio${i}']`
      ).innerHTML = `<img src='${uploaded_image}'>`;
    });
    reader.readAsDataURL(file);
  });
}
// main end
function create() {
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
}

document.querySelector("#product").addEventListener("submit", () => {
  document.querySelector(
    "main"
  ).innerHTML = `      <form action="/createadmin" method="post">
        <input type="text" name="username" required placeholder="UserName" />
        <input
          type="password"
          name="password"
          id="password"
          required
          placeholder="Password"
        /><input
          type="password"
          name="confirmation"
          id="confirmation"
          required
          placeholder="Confirm password"
        />
        <p id="confirm"></p>
        <input type="submit" value="Create">
      </form>`;
});
