function load_table(url, form, page = 1) {
    console.log('fetching');
    if (page !== null) {
        url = `${url}?page=${page}`;
    }
    url = url.replaceAll('amp;', ''); // Fix URL encoding issue
    let formData = form ? $(form).serialize() : {};

    $.ajax({
        type: "GET",
        url: url,
        data: formData,
        beforeSend: function () {
            $('#loading-image').show();
        },
        success: function (data) {
            $('#table').empty().append(data);
        },
        complete: function () {
            $('#loading-image').hide();
        },
        error: function () {
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: 'Something went wrong!',
                footer: `<b>Error Details:</b> ${xhr.responseText}`
            });
        }
    });
}
