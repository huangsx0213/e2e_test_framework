let newStatus;

function updateFloatingBar() {
    var selectedCheckboxes = $(".rowCheckbox:checked");
    if (selectedCheckboxes.length > 0) {
        var selectedIds = selectedCheckboxes.map(function() {
            return $(this).data('id');
        }).get();
        var selectedItems = window.filteredData.filter(item => selectedIds.includes(item.id));
        var allActive = selectedItems.every(item => item.status === "Active");
        var allInactive = selectedItems.every(item => item.status === "Inactive");

        $("#selectedCount").text(`${selectedItems.length} item(s) selected`);
        $("#calculateBtn").show();
        $("#calculationResult").text('');

        if (allActive || allInactive) {
            $("#setStatusBtn").text(allActive ? "Set Inactive" : "Set Active").show();
            $("#statusWarning").hide();
        } else {
            $("#setStatusBtn").hide();
            $("#statusWarningText").text('Selected items have different statuses');
            $("#statusWarning").show();
        }

        $("#floatingBar").show();
    } else {
        $("#floatingBar").hide();
    }
}

$(document).on('click', '#selectAll', function(){
    $(".rowCheckbox").prop('checked', this.checked);
    updateFloatingBar();
});

$(document).on('click', '.rowCheckbox', function(){
    var allChecked = $(".rowCheckbox:not(:checked)").length === 0;
    $("#selectAll").prop('checked', allChecked);
    updateFloatingBar();
});

$("#calculateBtn").click(function() {
    var selectedCheckboxes = $(".rowCheckbox:checked");
    var selectedIds = selectedCheckboxes.map(function() {
        return $(this).data('id');
    }).get();
    var selectedItems = window.filteredData.filter(item => selectedIds.includes(item.id));

    var totalDue = calculateTotalAmount(selectedItems);

    $("#calculationResult").text(`Total amount: $${totalDue.toFixed(2)}`);
});

function calculateTotalAmount(items) {
    return items.reduce((sum, item) => {
        var amount = parseFloat(item.due.replace('$', '').replace(',', ''));
        return sum + (isNaN(amount) ? 0 : amount);
    }, 0);
}

$("#setStatusBtn").click(function() {
    newStatus = $(this).text() === "Set Active" ? "Active" : "Inactive";
    var selectedCheckboxes = $(".rowCheckbox:checked");
    var selectedIds = selectedCheckboxes.map(function() {
        return $(this).data('id');
    }).get();
    var selectedItems = window.filteredData.filter(item => selectedIds.includes(item.id));

    var totalAmount = calculateTotalAmount(selectedItems);

    $("#selectedAmount").text(`$${totalAmount.toFixed(2)}`);
    $("#statusChangeModalLabel").text($(this).text());
    $("#statusChangeModal").modal('show');
});

$("#confirmStatusChange").click(function() {
    var selectedCheckboxes = $(".rowCheckbox:checked");
    var selectedIds = selectedCheckboxes.map(function() {
        return $(this).data('id');
    }).get();

    window.data = window.data.map(item => {
        if (selectedIds.includes(item.id)) {
            return {...item, status: newStatus, lastUpdate: new Date().toISOString()};
        }
        return item;
    });

    saveData(window.data).then(() => {
        applyFilter();
        $("#statusChangeModal").modal('hide');
        $("#floatingBar").hide();
        updateSummary();
    }).catch(error => {
        console.error("Error saving data:", error);
        alert("An error occurred while saving the data. Please try again.");
    });
});

$("#deleteSelectedBtn").click(function(){
    var selectedIds = $(".rowCheckbox:checked").map(function() {
        return $(this).data('id');
    }).get();
    if (selectedIds.length > 0) {
        var selectedItems = window.data.filter(item => selectedIds.includes(item.id));
        var detailsHtml = selectedItems.map(item =>
            `<p>${item.lastName}, ${item.firstName} (${item.email}) - ${item.due}</p>`
        ).join('');

        $('#deleteItemDetails').html(`
            <p>The following ${selectedItems.length} item(s) will be deleted:</p>
            ${detailsHtml}
        `);
        $('#deleteModal').modal('show');

        $("#confirmDelete").one('click', function() {
            Promise.all(selectedIds.map(id => deleteItem(id)))
                .then(() => {
                    window.data = window.data.filter(item => !selectedIds.includes(item.id));
                    $("#selectAll").prop('checked', false);
                    $('#deleteModal').modal('hide');
                    applyFilter();
                    updateSummary();
                })
                .catch(error => {
                    console.error("Error deleting items:", error);
                    alert("An error occurred while deleting the items. Please try again.");
                });
        });
    }
});

// 新增：批量更新状态的功能
$("#updateStatusBtn").click(function() {
    var selectedIds = $(".rowCheckbox:checked").map(function() {
        return $(this).data('id');
    }).get();

    if (selectedIds.length > 0) {
        var newStatus = $("#bulkStatusSelect").val();
        window.data = window.data.map(item => {
            if (selectedIds.includes(item.id)) {
                return {...item, status: newStatus, lastUpdate: new Date().toISOString()};
            }
            return item;
        });

        saveData(window.data).then(() => {
            applyFilter();
            updateSummary();
            $("#floatingBar").hide();
            alert(`Status updated to ${newStatus} for ${selectedIds.length} item(s).`);
        }).catch(error => {
            console.error("Error updating status:", error);
            alert("An error occurred while updating the status. Please try again.");
        });
    }
});