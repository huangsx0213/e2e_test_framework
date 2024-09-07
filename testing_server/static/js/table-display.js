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
        row.append($("<td>").text(item.referenceNo || ''));
        row.append($("<td>").text(item.name || ''));
        row.append($("<td>").text(item.email || ''));
        row.append($("<td>").text(item.amount || ''));
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

$(document).ready(function() {
    $("#prevPage").click(function() {
        if (window.currentPage > 1) {
            window.currentPage--;
            displayTable(window.currentPage);
        }
    });

    $("#nextPage").click(function() {
        if (window.currentPage < window.totalPages) {
            window.currentPage++;
            displayTable(window.currentPage);
        }
    });

    $("#goToPage").click(function() {
        var pageNumber = parseInt($("#pageInput").val());
        if (pageNumber >= 1 && pageNumber <= window.totalPages) {
            window.currentPage = pageNumber;
            displayTable(window.currentPage);
        } else {
            alert("Invalid page number. Please enter a number between 1 and " + window.totalPages);
        }
    });

    $("#pageInput").on('keypress', function(e) {
        if (e.which == 13) { // Enter key
            $("#goToPage").click();
        }
    });
});