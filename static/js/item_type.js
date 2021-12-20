    $(document).ready(function() {
      $('#id_item_type').on('change',function(){
        console.log($(this).val());
        if( $(this).val()==1){
          $("#id_site_size").show();
          $('label[for="id_site_size"]').show();
          $("#id_item_quantity").hide();
          $('label[for="id_item_quantity"]').hide();
        }
        else if(( $(this).val()==3) ||( $(this).val()==4)) {
          $("#id_site_size").hide();
          $('label[for="id_site_size"]').hide();
          $("#id_item_quantity").hide();
          $('label[for="id_item_quantity"]').hide();
        }
        else{
          $("#id_site_size").hide();
          $('label[for="id_site_size"]').hide();
          $("#id_item_quantity").show();
          $('label[for="id_item_quantity"]').show();
        }
      });
   });