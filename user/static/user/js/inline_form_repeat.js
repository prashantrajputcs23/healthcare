function add_inline_repeat_form(formset, inline_factory_form_prefix, newFormRow) {
    const $totalForms = $(`input[name="${inline_factory_form_prefix}-TOTAL_FORMS"]`);
    const newFormIndex = parseInt($totalForms.val(), 10);

    // Clone the new form row and update indices
    const newFormRowClone = newFormRow.clone();
    const regex = new RegExp(`${inline_factory_form_prefix}-(\\d+)-`, 'g');
    newFormRowClone.html(newFormRowClone.html().replace(regex, `${inline_factory_form_prefix}-${newFormIndex}-`));
    // Append the cloned row and update TOTAL_FORMS
    formset.append(newFormRowClone);
    $totalForms.val(newFormIndex + 1);
}

function remove_repeat_form(button, formset, inline_factory_form_prefix) {
    const $totalForms = $(`input[name="${inline_factory_form_prefix}-TOTAL_FORMS"]`);
    const $row = $(button).closest('tr');

    // Remove the row if there are multiple rows
    if (formset.children('tr').length > 1) {
        $row.remove();
    } else {
        // Reset the row fields if it's the only row
        $row.find('input, select, textarea').each(function () {
            if (this.type === 'checkbox' || this.type === 'radio') {
                this.checked = false;
            }
        });
    }

    // Update TOTAL_FORMS count
    $totalForms.val(formset.children('tr').length);
}
