$(document).ready(function() {
    loadTableData();

    // Trigger AJAX request when column headers are clicked
    $('th a').click(function(e) {
        e.preventDefault();
        var column = $(this).data('column');
        loadTableData(column);
    });
});

function loadTableData(sortColumn) {
    var url = "{% url 'dynamic-tracker-list' %}"; // Replace with the actual URL
    var filters = {
        carrier: $('#id_carrier').val(),
        sort: sortColumn
    };

    $.ajax({
        url: url,
        type: 'GET',
        data: filters,
        success: function(response) {
            var tableBody = $('#table-body');
            tableBody.empty();

            $.each(response, function(index, tracker) {
                var row = $('<tr>');
                row.append($('<td>').text(tracker.carrier));
                row.append($('<td>').text(tracker.number));
                row.append($('<td>').text(tracker.get_tracking_link()));
                row.append($('<td>').text(tracker.status));
                row.append($('<td>').text(tracker.delivery_estimate));
                row.append($('<td>').text(tracker.purchase_request));
                row.append($('<td>').text(tracker.vendor));
                row.append($('<td>').text(tracker.earliest_event_time));
                tableBody.append(row);
            });
        },
        error: function(xhr, status, error) {
            console.log(error);
        }
    });
}
