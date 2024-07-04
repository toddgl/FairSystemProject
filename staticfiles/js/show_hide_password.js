/*  static/js/show_hide_password.js */

function togglePassword(){
  var x = document.getElementById("id_password");
  var c = x.nextElementSibling
  if (x.type === "password") {
    x.type = "text";
    c.removeAttribute("class");
    c.setAttribute("class", "eye-icon bi bi-eye");
  } else {
    x.type = "password";
    c.removeAttribute("class");
    c.setAttribute("class","eye-icon bi bi-eye-slash");
  }
}

