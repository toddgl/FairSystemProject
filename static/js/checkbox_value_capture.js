/*  static/js/checkbox_value_capture.js */

$(document).ready(function() {
  var hidden = $('#hidden');
    var vals = [];
    $("[name='currentsites']").each(function() {
        if($(this).prop('checked') == true) {
            vals.push($(this).val());
        }
    });
    hidden.val(vals.toString());
  });
  $("input[name='currentsites']").change(function() {
    var hidden = $('#hidden');
    var values = [];
    $("[name='currentsites']").each(function() {
        if($(this).prop('checked') == true) {
            values.push($(this).val());
        }
    });
    hidden.val(values.toString());
  });
