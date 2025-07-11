document.addEventListener("DOMContentLoaded", () => {
    let datePicker;

    // Initialize the date picker
    const initializeDatePicker = () => {
        datePicker = flatpickr("#id_date", {
            enable: [], // initially no dates are enabled
            dateFormat: "Y-m-d", // format as year-month-day
        });
    };

    // Pre-fill selected values
    const setSelectedValue = (id, value) => {
        if (value) {
            const element = document.getElementById(id);
            element.value = value;
            $(element).trigger('change');
        }
    };

    const prefillData = async () => {
        setSelectedValue("id_doctor", selectedDoctor);
        setSelectedValue("id_branch", selectedBranch);

        if (selectedDoctor && selectedBranch) {
            await fetchAvailableDates(selectedDoctor, selectedBranch);
        }

        if (selectedDate) {
            const formattedDate = flatpickr.formatDate(new Date(selectedDate), "Y-m-d");
            setSelectedValue("id_date", formattedDate);
            datePicker.setDate(formattedDate, true);
        }

        if (selectedDoctor && selectedDate) {
            await fetchTimeSlots(selectedDoctor, selectedDate);
            $('#id_start_time').val(selectedTime);
        }
    };

    // Fetch branches based on doctor ID
    const fetchBranches = async (doctorId) => {
        try {
            const response = await $.ajax({
                url: `/doctor/branches`,
                type: "GET",
                data: { doctor_id: doctorId },
                dataType: "json"
            });
            const branches = response.branches;
            const $branchSelect = $('#id_branch');
            $branchSelect.empty().append('<option value="">Select a branch</option>');
            branches.forEach(branch => {
                $branchSelect.append(`<option value="${branch.id}">${branch.address}</option>`);
            });
            if (!branches.length) {
                alert("No branches available for this doctor.");
            }
        } catch (error) {
            console.error("Error loading branches:", error);
        }
    };

    // Fetch available dates based on doctor and branch IDs
    const fetchAvailableDates = async (doctorId, branchId) => {
        try {
            const response = await $.ajax({
                url: `/doctor/dates`,
                type: "GET",
                data: { doctor_id: doctorId, branch_id: branchId },
                dataType: "json"
            });
            const dates = response.dates.map(date => flatpickr.formatDate(new Date(date), "Y-m-d"));
            datePicker.set('enable', dates);
            if (selectedDate) {
                datePicker.setDate(flatpickr.formatDate(new Date(selectedDate), "Y-m-d"), true);
            }
            if (!dates.length) {
                alert("No available dates for this doctor at this location.");
            }
        } catch (error) {
            console.error("Error loading dates:", error);
        }
    };

    // Fetch time slots based on doctor ID and selected date
    const fetchTimeSlots = async (doctorId, selectedDate) => {
        try {
            const response = await $.ajax({
                url: "/doctor/dates/slots",
                type: "GET",
                data: { doctor_id: doctorId, date: selectedDate },
                dataType: "json"
            });
            const $timeSelect = $('#id_start_time');
            $timeSelect.empty().append('<option value="">Select a time</option>');
            response.times.forEach(time => {
                $timeSelect.append(`<option value="${time}">${time}</option>`);
            });
            if (!response.times.length) {
                alert("No available time slots for this date and doctor.");
            }
        } catch (error) {
            console.error("Error loading times:", error);
        }
    };

    // Initialize the date picker and pre-fill data
    initializeDatePicker();
    prefillData(); // Prefill form values after initializing the date picker

    // Event Listeners
    $("#id_doctor").on("change", async function () {
        const doctorId = this.value;
        if (doctorId) {
            await fetchBranches(doctorId); // Await branches to be fetched before clearing dates
            datePicker.clear(); // Clear dates after fetching branches
            $('#id_start_time').empty().append('<option value="">Select a time</option>'); // Reset time select
        } else {
            $('#id_branch').empty().append('<option value="">Select a branch</option>');
            datePicker.clear(); // Clear dates if no doctor is selected
            $('#id_start_time').empty().append('<option value="">Select a time</option>'); // Reset time select
        }
    });

    $("#id_branch").on("change", async function () {
        const branchId = this.value;
        const doctorId = $('#id_doctor').val();
        if (doctorId && branchId) {
            await fetchAvailableDates(doctorId, branchId); // Fetch dates when both doctor and branch are selected
        } else {
            datePicker.clear(); // Clear dates if either doctor or branch is missing
            $('#id_start_time').empty().append('<option value="">Select a time</option>'); // Reset time select
        }
    });

    $("#id_date").on("change", async function () {
        const doctorId = $('#id_doctor').val();
        const selectedDate = this.value;
        if (doctorId && selectedDate) {
            await fetchTimeSlots(doctorId, selectedDate); // Fetch time slots when both doctor and date are selected
        } else {
            $('#id_start_time').empty().append('<option value="">Select a time</option>'); // Reset time select
        }
    });
});
