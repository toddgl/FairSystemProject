;(function() {

  // Set vars
  var tcheck = $("#id_trestle_required");
  var tquant = $("#id_trestle_quantity");
  var pcheck = $("#id_power_required");
  var pselect1 = $("#id_event_power_first");
  var pselect2 = $("#id_event_power_second");

  // Hide fields
  tquant.hide();
  pselect1.hide();
  pselect2.hide();

  // Hide field label
  $('label[for=id_trestle_quantity], input#id_trestle_quantity').hide();
  $('label[for=id_event_power_first], input#id_event_power_first').hide();
  $('label[for=id_event_power_second], input#id_event_power_second').hide();

  // tcheck event listener
  tcheck.change(function() {
    // See if checked, show/hide
    if (tcheck.is(':checked')) {
      tquant.show();
      $('label[for=id_trestle_quantity], input#id_trestle_quantity').show();
    } else {
      tquant.hide();
      $('label[for=id_trestle_quantity], input#id_trestle_quantiy').hide();
    }
  });

  // pcheck event listener
  pcheck.change(function() {
    // See if checked, show/hide
    if (pcheck.is(':checked')) {
      pselect1.show();
      pselect2.show();
      $('label[for=id_event_power_first], input#id_event_power_first').show();
      $('label[for=id_event_power_second], input#id_event_power_second').show();
    } else {
      pselect1.hide();
      pselect2.hide();
      $('label[for=id_event_power_first], input#id_event_power_first').hide();
      $('label[for=id_event_power_second], input#id_event_power_second').hide();
    }
  });
})();