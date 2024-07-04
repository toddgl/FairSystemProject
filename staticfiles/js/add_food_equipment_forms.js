/*  static/js/add_food_equipment_forms.js */

 document.addEventListener('click', (event)=>{
        if (event.target.id == 'add-more') {
            add_new_form(event)
        }
    })
    function add_new_form(event) {
        if (event) {
            event.preventDefault()
        }
        const totalNewForms = document.getElementById('id_form-TOTAL_FORMS')
        const currentIngredientForms = document.getElementsByClassName('equipment-form')
        const currentFormCount = currentIngredientForms.length // + 1
        const formCopyTarget = document.getElementById('equipment-form-list')
        const copyEmptyFormEl = document.getElementById('empty-form').cloneNode(true)
        copyEmptyFormEl.setAttribute('class', 'equipment-form')
        copyEmptyFormEl.setAttribute('id', `form-${currentFormCount}`)
        const regex = new RegExp('__prefix__', 'g')
        copyEmptyFormEl.innerHTML = copyEmptyFormEl.innerHTML.replace(regex, currentFormCount)
        totalNewForms.setAttribute('value', currentFormCount + 1)
        // now add new empty form element to our html form
        formCopyTarget.append(copyEmptyFormEl)
    }
