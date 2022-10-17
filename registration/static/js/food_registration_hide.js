;(function() {

  // Set vars
  var fcheck = $("#id_has_food_prep");
  var fprep = $("#id_food_storage_prep_method");

  // check to see if checkbox is ticked
      if (fcheck.is(':checked')) {
        fprep.show();
        $('label[for=id_food_storage_prep_method], input#id_food_storage_prep_method').show();
      } else {
        fprep.hide();
        $('label[for=id_food_storage_prep_method], input#id_food_storage_prep_method').hide();
      }

  // fcheck event listener
  fcheck.change(function() {
    // See if checked, show/hide
    if (fcheck.is(':checked')) {
      fprep.show();
      $('label[for=id_food_storage_prep_method], input#id_food_storage_prep_method').show();
    } else {
     fprep .hide();
      $('label[for=id_food_storage_prep_method], input#id_food_storage_prep_method').hide();
    }
  });
})();