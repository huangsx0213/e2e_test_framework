function applyFilter() {
    var status = $("#statusFilter").val();
    var minAmount = parseFloat($("#minAmount").val()) || 0;
    var maxAmount = parseFloat($("#maxAmount").val()) || Infinity;

    window.filteredData = window.data.filter(item => {
        var amount = parseFloat(item.due.replace('$', '').replace(',', ''));
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
    var activeAmount = 0;
    var inactiveAmount = 0;
    var activeCount = 0;
    var inactiveCount = 0;
    var totalCount = window.filteredData.length;

    window.filteredData.forEach(item => {
        var amount = parseFloat(item.due.replace('$', '').replace(',', ''));
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

    $("#totalAmount").text(`$${totalAmount.toFixed(2)}`);
    $("#activeAmount").text(`$${activeAmount.toFixed(2)}`);
    $("#inactiveAmount").text(`$${inactiveAmount.toFixed(2)}`);
    $("#totalCount").text(totalCount);
    $("#activeCount").text(activeCount);
    $("#inactiveCount").text(inactiveCount);
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