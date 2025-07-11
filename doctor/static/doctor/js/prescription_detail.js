$(function () {
    var loadForm = function () {
        var btn = $(this);
        $.ajax({
            url: btn.attr("data-url"),
            type: 'get',
            dataType: 'json',
            beforeSend: function () {
                $("#modal-prescription .modal-content").html("");
                $("#modal-prescription").modal("show");
                console.log('show');
            },
            success: function (data) {
                $("#modal-prescription .modal-content").html(data.html_form);
            }
        });
    };

    var saveForm = function () {
        var form = $(this);
        $.ajax({
            url: form.attr("action"),
            data: form.serialize(),
            type: form.attr("method"),
            dataType: 'json',
            success: function (data) {
                if (data.form_is_valid) {
                    $("#prescription-detail-table tbody").html(data.html_prescription_detail_list);
                    $("#modal-prescription").modal("hide");
                    if (data.is_deleted) {
                        Swal.fire({
                            title: 'Successfully Deleted',
                            icon: 'error',
                            showConfirmButton: false,
                            timer: 2000, // Auto-close after 2 seconds (2000 milliseconds)
                            timerProgressBar: true,
                        });
                    } else {
                        Swal.fire({
                            title: 'Successfully saved',
                            icon: 'success',
                            showConfirmButton: false,
                            timer: 2000,
                            timerProgressBar: true,
                        });
                    }
                } else {
                    $("#modal-prescription .modal-content").html(data.html_form);
                }
            }
        });
        return false;
    };
    $(".js-create-prescription-detail").click(loadForm);
});
