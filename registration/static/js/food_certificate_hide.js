;(function() {

  // Set vars
  var fcheck = $("#id_has_food_certificate");
  var fcertdate = $("#id_certificate_expiry_date");
  var fcertificate = $("#id_food_registration_certificate");
  var conscheck = $('#id_food_fair_consumed')
  var conssource = $('#id_food_source')
  var prepcheck = $('#id_has_food_prep')
  var prepmethod = $('#id_food_storage_prep_method')

  // check to see if has certificate checkbox is ticked
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

  // check to see if food consumed at the fair checkbox is ticked
      if (conscheck.is(':checked')) {
        conssource.show();
        $('label[for=id_food_source], input#id_food_source').show();
      } else {
        conssource.hide();
        $('label[for=id_food_source], input#id_food_source').hide();
      }

  // conscheck event listener
  conscheck.change(function() {
    // See if checked, show/hide
    if (conscheck.is(':checked')) {
        conssource.show();
        $('label[for=id_food_source], input#id_food_source').show();
    } else {
        conssource.hide();
        $('label[for=id_food_source], input#id_food_source').hide();
    }
  });

  // check to see if food  prepared on site at the fair checkbox is ticked
      if (prepcheck.is(':checked')) {
        prepmethod.show();
        $('label[for=id_food_storage_prep_method], input#id_food_storage_prep_method').show();
      } else {
        prepmethod.hide();
        $('label[for=id_food_storage_prep_method], input#id_food_storage_prep_method').hide();
      }

  // consprep event listener
  prepcheck.change(function() {
    // See if checked, show/hide
    if (prepcheck.is(':checked')) {
        prepmethod.show();
        $('label[for=id_food_storage_prep_method], input#id_food_storage_prep_method').show();
    } else {
        prepmethod.hide();
        $('label[for=id_food_storage_prep_method], input#id_food_storage_prep_method').hide();
    }
  });
})();
