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

        $("#selectedCount").text(`${selectedItems.length} transfer(s) selected`);
        $("#calculateBtn").show();
        $("#calculationResult").text('');

        if (allActive || allInactive) {
            $("#setStatusBtn").text(allActive ? "Set Inactive" : "Set Active").show();
            $("#statusWarning").hide();
        } else {
            $("#setStatusBtn").hide();
            $("#statusWarningText").text('Selected transfers have different statuses');
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

    var totalAmount = calculateTotalAmount(selectedItems);

    $("#calculationResult").text(`Total amount: $${totalAmount.toFixed(2)}`);
});

function calculateTotalAmount(items) {
    return items.reduce((sum, item) => {
        var amount = parseFloat(item.amount.replace('$', '').replace(',', ''));
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
    var selectedIds = $(".rowCheckbox:checked").map(function() {
        return $(this).data('id');
    }).get();

    if (selectedIds.length > 0) {
        bulkUpdateStatus(selectedIds, newStatus).then(() => {
            console.log("Bulk status update successful");
            $("#statusChangeModal").modal('hide');
            $("#floatingBar").hide();
            applyFilter();
            window.fetchSummary();  // Update summary
        }).catch(error => {
            console.error("Error updating status:", error);
            alert("An error occurred while updating the status. Please try again.");
        });
    }
});

$("#deleteSelectedBtn").click(function(){
    var selectedIds = $(".rowCheckbox:checked").map(function() {
        return $(this).data('id');
    }).get();
    if (selectedIds.length > 0) {
        var selectedItems = window.filteredData.filter(item => selectedIds.includes(item.id));
        var detailsHtml = selectedItems.map(item =>
            `<p>${item.referenceNo}: ${item.from} → ${item.to}, ${item.amount} (${item.messageType})</p>`
        ).join('');

        $('#deleteItemDetails').html(`
            <p>The following ${selectedItems.length} transfer(s) will be deleted:</p>
            ${detailsHtml}
        `);
        $('#deleteModal').modal('show');

        $("#confirmDelete").one('click', async function() {
            $('#deleteModal').modal('hide');

            // Create a floating progress bar
            var progressContainer = $('<div class="floating-progress"><h5>Deleting Transfers...</h5><div class="progress"><div class="progress-bar" role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div></div></div>');
            $('body').append(progressContainer);

            for (let i = 0; i < selectedIds.length; i++) {
                try {
                    await deleteItemWithDelay(selectedIds[i]);

                    // Update progress bar
                    let progress = Math.round((i + 1) / selectedIds.length * 100);
                    progressContainer.find('.progress-bar').css('width', progress + '%').attr('aria-valuenow', progress).text(progress + '%');
                } catch (error) {
                    console.error("Error deleting transfer:", error);
                    alert(`An error occurred while deleting transfer ${selectedIds[i]}. Please try again.`);
                }
            }

            // Remove progress bar after completion
            setTimeout(() => {
                progressContainer.remove();
            }, 1000);

            $("#selectAll").prop('checked', false);
            applyFilter();
            updateSummary();
        });
    }
});

function deleteItemWithDelay(id) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            deleteItem(id)
                .then(resolve)
                .catch(reject);
        }, 100);
    });
}

// Bulk update status functionality
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
            alert(`Status updated to ${newStatus} for ${selectedIds.length} transfer(s).`);
        }).catch(error => {
            console.error("Error updating status:", error);
            alert("An error occurred while updating the status. Please try again.");
        });
    }
});