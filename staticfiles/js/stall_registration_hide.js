;(function() {

  // Set vars
  var tcheck = $("#id_trestle_required");
  var vcheck = $("#id_vehicle_on_site");
  var tquant = $("#id_trestle_quantity");
  var vlength = $('#id_vehicle_length');
  var vwidth = $('#id_vehicle_width');
  var vimage = $('#id_vehicle_image');
  var scheck = $('#id_multi_site');
  var ssite = $('#required_sites')

  // check to see if trestle checkbox is ticked
      if (tcheck.is(':checked')) {
        tquant.show();
        $('label[for=id_trestle_quantity], input#id_trestle_quantity').show();
      } else {
        tquant.hide();
        $('label[for=id_trestle_quantity], input#id_trestle_quantity').hide();
      }

  // tcheck event listener
  tcheck.change(function() {
    // See if trestle checkbox is changed show/hide
    if (tcheck.is(':checked')) {
      tquant.show();
      $('label[for=id_trestle_quantity], input#id_trestle_quantity').show();
    } else {
      tquant.hide();
      $('label[for=id_trestle_quantity], input#id_trestle_quantity').hide();
    }
  });

  // check to see if vehicle checkbox is ticked
      if (vcheck.is(':checked')) {
        vlength.show();
        $('label[for=id_vehicle_length], input#id_vehicle_length').show();
        vwidth.show();
        $('label[for=id_vehicle_width], input#id_vehicle_width').show();
        vimage.show();
        $('label[for=id_vehicle_image], input#id_vehicle_image').show();
      } else {
        vlength.hide();
        $('label[for=id_vehicle_length], input#id_vehicle_length').hide();
        vwidth.hide();
        $('label[for=id_vehicle_width], input#id_vehicle_width').hide();
        vimage.hide();
        $('label[for=id_vehicle_image], input#id_vehicle_image').hide();
      }
  // vcheck event listener
  vcheck.change(function() {
    // See if vehicle checkbox is changed, show/hide
      if (vcheck.is(':checked')) {
        vlength.show();
        $('label[for=id_vehicle_length], input#id_vehicle_length').show();
        vwidth.show();
        $('label[for=id_vehicle_width], input#id_vehicle_width').show();
        vimage.show();
        $('label[for=id_vehicle_image], input#id_vehicle_image').show();
      } else {
        vlength.hide();
        $('label[for=id_vehicle_length], input#id_vehicle_length').hide();
        vwidth.hide();
        $('label[for=id_vehicle_width], input#id_vehicle_width').hide();
        vimage.hide();
        $('label[for=id_vehicle_image], input#id_vehicle_image').hide();
      }
  });

  // check to see if the multi_site checkbox is ticked
      if (scheck.is(':checked')) {
        ssite.show();
      } else {
        ssite.hide();
      }

  // scheck event listener
  scheck.change(function() {
    // See if multi_site checkbox is changed show/hide
    if (scheck.is(':checked')) {
      ssite.show();
    } else {
      ssite.hide();
    }
  });
})();