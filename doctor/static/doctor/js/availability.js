$(document).ready(function () {
    // Initialize the month picker for month-year
    $("#id_month_year").datepicker({
        changeMonth: true,
        changeYear: true,
        showButtonPanel: true,
        dateFormat: 'MM yy',
        onClose: function (dateText, inst) {
            let month = inst.selectedMonth + 1; // jQuery months are 0-based
            let year = inst.selectedYear;
            let url = $("#id_month_year").data("url");
            loadAvailabilityForMonth(month, year, url);
        },
        beforeShow: function (input, inst) {
            $(inst.dpDiv).addClass('monthpicker');
        }
    });

    // Handle Apply to All Days checkbox
    $("#apply_to_all").change(function () {
        if (this.checked) {
            applyTimesToAllDays();
        }
        var isChecked = $(this).is(':checked');
        $("input[name^='available_']").prop('checked', isChecked);
    });

    function loadAvailabilityForMonth(month, year, url) {
        $.ajax({
            url: url,
            data: {
                month: month,
                year: year,
                doctor_id:$('#doctor_id').val(),
            },
            method: 'GET',
            success: function (response) {
                updateTable(response);
            },
            error: function () {
                alert('Error fetching availability data.');
            }
        });
    }

    function updateTable(availabilityData) {
        var $tbody = $('#availability-table tbody');
        $tbody.empty();  // Clear previous rows

        availabilityData.days.forEach(function (day) {
            var isChecked = day.available ? 'checked' : ''; // Check if availability exists for that day
            $tbody.append(`
                        <tr>
                            <td>${day.date} (${day.day_of_week})</td> <!-- Display date with day of the week -->
                            <td><input type="checkbox" name="available_${day.date}" ${isChecked}></td>
                            <td><input type="time" name="start_time_${day.date}" class="form-control" value="${day.start_time || ''}"></td>
                            <td><input type="time" name="end_time_${day.date}" class="form-control" value="${day.end_time || ''}"></td>
                            <td><input type="time" name="lunch_start_time_${day.date}" class="form-control" value="${day.lunch_start_time || ''}"></td>
                            <td><input type="time" name="lunch_end_time_${day.date}" class="form-control" value="${day.lunch_end_time || ''}"></td>
                            <td class="error"></td> <!-- Column for displaying errors -->
                        </tr>
                    `);
        });
    }

    function applyTimesToAllDays() {
        var startTime = $("#apply_start_time").val();
        var endTime = $("#apply_end_time").val();
        var lunchStartTime = $("#apply_lunch_start_time").val();
        var lunchEndTime = $("#apply_lunch_end_time").val();

        $("#availability-table tbody tr").each(function () {
            $(this).find('input[name^="start_time_"]').val(startTime);
            $(this).find('input[name^="end_time_"]').val(endTime);
            $(this).find('input[name^="lunch_start_time_"]').val(lunchStartTime);
            $(this).find('input[name^="lunch_end_time_"]').val(lunchEndTime);
        });
    }

    $("form").submit(function (event) {
        event.preventDefault();  // Prevent the default form submission

        // Serialize form data
        var formData = $(this).serialize();

        $.ajax({
            url: $(this).attr('action'),  // Form action URL
            method: 'POST',
            data: formData,
            success: function (response) {
                if (response.status === 'success') {
                    alert('Availability saved successfully!');
                    window.location.href = '/user/';  // Redirect on success
                }
            },
            error: function (jqXHR) {
                var response = jqXHR.responseJSON;
                if (response.status === 'error') {
                    // Clear previous errors
                    $('.error').empty();

                    // Display new errors
                    response.errors.forEach(function (error) {
                        var date = error.date;
                        var errorText = error.error;
                        var row = $('input[name="available_' + date + '"]').closest('tr');
                        row.find('.error').text(errorText);
                    });
                } else {
                    alert('An error occurred.');
                }
            }
        });
    });
});