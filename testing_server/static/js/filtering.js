function applyFilter() {
    var status = $("#statusFilter").val();
    var minAmount = parseFloat($("#minAmount").val()) || 0;
    var maxAmount = parseFloat($("#maxAmount").val()) || Infinity;

    window.filteredData = window.data.filter(item => {
        var amount = parseFloat(item.amount.replace('$', '').replace(',', ''));
        return (status === "" || item.status === status) &&
               (amount >= minAmount && amount <= maxAmount);
    });

    window.totalPages = Math.ceil(window.filteredData.length / window.itemsPerPage);
    window.currentPage = 1;
    displayTable(window.currentPage);
    updateSummary();
    $("#dataTable").trigger("update");
}

function updateSummary() {
    var totalAmount = 0;
    var totalCount = window.data.length;
    var activeAmount = 0;
    var inactiveAmount = 0;
    var activeCount = 0;
    var inactiveCount = 0;
    var filteredActiveAmount = 0;
    var filteredInactiveAmount = 0;
    var filteredActiveCount = 0;
    var filteredInactiveCount = 0;
    var filteredCount = window.filteredData.length;

    // Calculate totals for all data
    window.data.forEach(item => {
        var amount = parseFloat(item.amount.replace('$', '').replace(',', ''));
        if (!isNaN(amount)) {
            totalAmount += amount;
            if (item.status === 'Active') {
                activeAmount += amount;
                activeCount++;
            } else if (item.status === 'Inactive') {
                inactiveAmount += amount;
                inactiveCount++;
            }
        }
    });

    // Calculate totals for filtered data
    window.filteredData.forEach(item => {
        var amount = parseFloat(item.amount.replace('$', '').replace(',', ''));
        if (!isNaN(amount)) {
            if (item.status === 'Active') {
                filteredActiveAmount += amount;
                filteredActiveCount++;
            } else if (item.status === 'Inactive') {
                filteredInactiveAmount += amount;
                filteredInactiveCount++;
            }
        }
    });

    // Update total summary (not affected by filter)
    $("#totalAmount").text(`$${totalAmount.toFixed(2)}`);
    $("#totalCount").text(totalCount);

    // Update filtered summary
    $("#activeAmount").text(`$${filteredActiveAmount.toFixed(2)}`);
    $("#inactiveAmount").text(`$${filteredInactiveAmount.toFixed(2)}`);
    $("#activeCount").text(filteredActiveCount);
    $("#inactiveCount").text(filteredInactiveCount);

    // Update filtered total (optional, uncomment if you want to display this information)
    // var filteredTotalAmount = filteredActiveAmount + filteredInactiveAmount;
    // $("#filteredTotalAmount").text(`$${filteredTotalAmount.toFixed(2)}`);
    // $("#filteredTotalCount").text(filteredCount);
}

$("#applyFilter").click(applyFilter);

$("#resetFilter").click(function() {
    $("#statusFilter").val("");
    $("#minAmount").val("");
    $("#maxAmount").val("");
    window.filteredData = [...window.data];
    window.totalPages = Math.ceil(window.filteredData.length / window.itemsPerPage);
    window.currentPage = 1;
    displayTable(window.currentPage);
    updateSummary();
});

// Add event listeners for real-time filtering (optional)
$("#statusFilter, #minAmount, #maxAmount").on('change input', function() {
    applyFilter();
});

// Initialize filtering when the page loads
$(document).ready(function() {
    applyFilter();
});