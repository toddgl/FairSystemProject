;(function() {

  // Set vars
  var fcheck = $("#id_has_food_certificate");
  var fcertdate = $("#id_certificate_expiry_date");
  var fcertificate = $("#id_food_registration_certificate");

  // check to see if checkbox is ticked
      if (fcheck.is(':checked')) {
        fcertdate.show();
        $('label[for=id_certificate_expiry_date], input#id_certificate_expiry_date').show();
        fcertificate.show();
        $('label[for=id_food_registration_certificate], input#id_food_registration_certificate').show();
      } else {
        fcertdate.hide();
        $('label[for=id_certificate_expiry_date], input#id_certificate_expiry_date').hide();
        fcertificate.hide();
        $('label[for=id_food_registration_certificate], input#id_food_registration_certificate').hide();
      }

  // fcheck event listener
  fcheck.change(function() {
    // See if checked, show/hide
    if (fcheck.is(':checked')) {
        fcertdate.show();
        $('label[for=id_certificate_expiry_date], input#id_certificate_expiry_date').show();
        fcertificate.show();
        $('label[for=id_food_registration_certificate], input#id_food_registration_certificate').show();
    } else {
        fcertdate.hide();
        $('label[for=id_certificate_expiry_date], input#id_certificate_expiry_date').hide();
        fcertificate.hide();
        $('label[for=id_food_registration_certificate], input#id_food_registration_certificate').hide();
    }
  });
})();