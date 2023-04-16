/*  static/js/checkbox_value_capture.js */

function isempty() {
	 if(document.getElementById("hidden").value=="") {
            document.getElementById('submitbtn').disabled = true;
        } else {
            document.getElementById('submitbtn').disabled = false;
        }
    }
window.onload= isempty();
