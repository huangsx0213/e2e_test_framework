function displayTable(page) {
    $("#selectAll").prop('checked', false);
    console.log("Displaying table for page:", page);
    var start = (page - 1) * window.itemsPerPage;
    var end = start + window.itemsPerPage;
    var pageData = window.filteredData.slice(start, end);

    var tbody = $("#dataTable tbody");
    tbody.empty();

    if (pageData.length === 0) {
        tbody.html('<tr><td colspan="9" class="text-center">No data available</td></tr>');
        return;
    }

    $.each(pageData, function(index, item) {
        var row = $("<tr>");
        row.append($("<td>").append($("<input>", {type: "checkbox", class: "rowCheckbox", "data-id": item.id})));
        row.append($("<td>").text(item.lastName || ''));
        row.append($("<td>").text(item.firstName || ''));
        row.append($("<td>").text(item.email || ''));
        row.append($("<td>").text(item.due || ''));
        row.append($("<td>").text(item.website || ''));
        row.append($("<td>").text(item.status || ''));
        row.append($("<td>").text(item.lastUpdate ? new Date(item.lastUpdate).toLocaleString() : ''));
        row.append($("<td>").append(
            $("<button>", {class: "edit btn btn-outline-primary me-1", "data-id": item.id}).text("Edit"),
            $("<button>", {class: "delete btn btn-outline-danger", "data-id": item.id}).text("Delete")
        ));
        tbody.append(row);
    });

    updatePagination();
    updateTableInfo();
    updateFloatingBar();
    $("#dataTable").trigger("update");
}

function updatePagination() {
    $("#pageInput").val(window.currentPage);
    $("#prevPage").prop("disabled", window.currentPage === 1);
    $("#nextPage").prop("disabled", window.currentPage === window.totalPages);
}

function updateTableInfo() {
    var totalItems = window.filteredData.length;
    var start = (window.currentPage - 1) * window.itemsPerPage + 1;
    var end = Math.min(start + window.itemsPerPage - 1, totalItems);

    $("#pageInfo").text(`Page ${window.currentPage} of ${window.totalPages}`);
    $("#dataInfo").text(`Showing ${start} to ${end} of ${totalItems} entries`);
}

function initTableSorter() {
    $("#dataTable").tablesorter({
        headers: {
            0: { sorter: false },
            8: { sorter: false }
        },
        sortList: [[7,0]],
        widgets: ['zebra', 'saveSort'],
        widgetOptions: {
            zebra: ['even', 'odd'],
        },
    }).on('sortEnd', function() {
        updateFloatingBar();
    });
}