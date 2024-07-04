;(function() {

  // Set vars
  var acheck = $("#id_is_archived");
  var isactive = $("#id_is_active");
  var isdone = $('#id_is_done')

  // check to see if is archived checkbox is ticked
      if (acheck.is(':checked')) {
        isactive.hide();
        $('label[for=id_is_active], input#id_is_active').hide();
        isdone.hide();
        $('label[for=id_is_done], input#id_is_done').hide();

      } else {
        isactive.show();
        $('label[for=id_is_active], input#id_is_active').show();
        isdone.hide();
        $('label[for=id_is_done], input#id_is_done').show();
      }

  // acheck event listener
  acheck.change(function() {
    // See if checked, show/hide
    if (acheck.is(':checked')) {
        isactive.hide();
        $('label[for=id_is_active], input#id_is_active').hide();
        isdone.hide();
        $('label[for=id_is_done], input#id_is_done').hide();
    } else {
        isactive.show();
        $('label[for=id_is_active], input#id_is_active').show();
        isdone.hide();
        $('label[for=id_is_done], input#id_is_done').show();
    }
  });

  // check to see if is active checkbox is ticked
      if (isactive.is(':checked')) {
        isdone.hide();
        $('label[for=id_is_done], input#id_is_done').hide();

      } else {
        isdone.show();
        $('label[for=id_is_done], input#id_is_done').show();
      }

  // isactive event listener
 isactive.change(function() {
    // See if checked, show/hide
    if (isactive.is(':checked')) {
        isdone.hide();
        $('label[for=id_is_done], input#id_is_done').hide();
    } else {
        isdone.show();
        $('label[for=id_is_done], input#id_is_done').show();
    }
  });

  // check to see if is done checkbox is ticked
      if (isdone.is(':checked')) {
        isactive.hide();
        $('label[for=id_is_active], input#id_is_active').hide();

      } else {
        isactive.show();
        $('label[for=id_is_active], input#id_is_active').show();
      }

  // isdone event listener
  isdone.change(function() {
    // See if checked, show/hide
    if (isdone.is(':checked')) {
        isactive.hide();
        $('label[for=id_is_active], input#id_is_active').hide();
    } else {
        isactive.show();
        $('label[for=id_is_active], input#id_is_active').show();
    }
  });

})();