function add_inline_repeat_form(formset, inline_factory_form_prefix, newFormRow) {
    const $totalForms = $(`input[name="${inline_factory_form_prefix}-TOTAL_FORMS"]`);
    const newFormIndex = parseInt($totalForms.val(), 10);

    // Clone the new form row and update indices
    const newFormRowClone = newFormRow.clone();
    const regex = new RegExp(`${inline_factory_form_prefix}-(\\d+)-`, 'g');
    newFormRowClone.html(newFormRowClone.html().replace(regex, `${inline_factory_form_prefix}-${newFormIndex}-`));

    // Clear the input, select, and textarea values in the cloned row
    newFormRowClone.find('input, select, textarea').each(function () {
        const nameAttr = $(this).attr('name');
        if (nameAttr) {
            $(this).val(''); // Reset value
        }
        if ($(this).is(':checkbox, :radio')) {
            $(this).prop('checked', false); // Reset checkboxes and radios
        }
    });

    // Append the cloned row and update TOTAL_FORMS
    formset.append(newFormRowClone);
    $totalForms.val(newFormIndex + 1);

    // Reinitialize any required plugins or events for the new row
    if (typeof reinitializePlugins === 'function') {
        reinitializePlugins(newFormRowClone);
    }
}

function remove_repeat_form(button, formset, inline_factory_form_prefix) {
    const $totalForms = $(`input[name="${inline_factory_form_prefix}-TOTAL_FORMS"]`);
    const $row = $(button).closest('tr');

    // Remove the row only if there are multiple rows
    if (formset.children('tr').length > 1) {
        $row.remove();

        // Reindex remaining forms to keep proper order
        formset.children('tr').each((index, row) => {
            const regex = new RegExp(`${inline_factory_form_prefix}-(\\d+)-`, 'g');
            $(row).html($(row).html().replace(regex, `${inline_factory_form_prefix}-${index}-`));
        });
    } else {
        // Reset the row fields if it's the only row
        $row.find('input, select, textarea').each(function () {
            $(this).val('');
            if ($(this).is(':checkbox, :radio')) {
                $(this).prop('checked', false);
            }
        });
    }

    // Update TOTAL_FORMS count
    $totalForms.val(formset.children('tr').length);
}
