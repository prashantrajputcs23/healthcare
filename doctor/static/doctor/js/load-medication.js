function initializeSelect2(element=$('.medication-dropdown')) {
    element.select2({
        ajax: {
            url: '/your-ajax-url/',  // Django URL to load options dynamically
            dataType: 'json',
            delay: 250,  // Delay for AJAX request
            data: function (params) {
                return {
                    search: params.term  // Search term entered by the user
                };
            },
            processResults: function (data) {
                // Process the response into a format that Select2 expects
                return {
                    results: $.map(data.results, function (item) {
                        return {
                            id: item.id,
                            text: item.text
                        };
                    })
                };
            },
            cache: true  // Cache the AJAX response to avoid unnecessary requests
        },
        minimumInputLength: 2,  // Minimum characters before AJAX call
        dropdownParent: $('#modal-prescription')  // Append dropdown to modal to prevent z-index issues
    });
}