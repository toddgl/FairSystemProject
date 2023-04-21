/*  static/js/isempty.js */

$(document).ready(function() {
    if (!$('#hidden').val()) {
            $('#movebtn').prop('disabled', true);
            $('#removebtn').prop('disabled', true);
        } else {
            $('#movebtn').prop('disabled', false);
            $('#removebtn').prop('disabled', false);
        }
});
$(document).on("change input paste", function() {
    if (!$('#hidden').val()) {
            $('#movebtn').prop('disabled', true);
            $('#removebtn').prop('disabled', true);
        } else {
            $('#movebtn').prop('disabled', false);
            $('#removebtn').prop('disabled', false);
        }
});
