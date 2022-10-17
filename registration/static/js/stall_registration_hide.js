;(function() {

  // Set vars
  var tcheck = $("#id_trestle_required");
  var tquant = $("#id_trestle_quantity");

  // check to see if checkbox is ticked
      if (tcheck.is(':checked')) {
        tquant.show();
        $('label[for=id_trestle_quantity], input#id_trestle_quantity').show();
      } else {
        tquant.hide();
        $('label[for=id_trestle_quantity], input#id_trestle_quantity').hide();
      }

  // tcheck event listener
  tcheck.change(function() {
    // See if checked, show/hide
    if (tcheck.is(':checked')) {
      tquant.show();
      $('label[for=id_trestle_quantity], input#id_trestle_quantity').show();
    } else {
      tquant.hide();
      $('label[for=id_trestle_quantity], input#id_trestle_quantity').hide();
    }
  });
})();