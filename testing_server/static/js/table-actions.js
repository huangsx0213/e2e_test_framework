// Global variables
let itemToDelete;
let currentItem;

// Function to get the maximum REF number
function getMaxRefNumber() {
    let maxRef = 0;
    window.filteredData.forEach(item => {
        const refNumber = parseInt(item.referenceNo.replace('REF', ''));
        if (!isNaN(refNumber) && refNumber > maxRef) {
            maxRef = refNumber;
        }
    });
    return maxRef;
}

$(document).ready(function() {
    console.log("table-actions.js loaded");

    // Edit button click handler
    $(document).on('click', '.edit', function(e) {
        e.preventDefault();
        var id = $(this).data('id');
        console.log("Edit button clicked for id:", id);
        currentItem = window.filteredData.find(item => item.id === id);
        if (currentItem) {
            console.log("Found transfer for editing:", currentItem);
            $('#referenceNo').val(currentItem.referenceNo || '');
            $('#from').val(currentItem.from || '');
            $('#to').val(currentItem.to || '');
            $('#amount').val(currentItem.amount || '');
            $('#messageType').val(currentItem.messageType || '');
            $('#status').val(currentItem.status || '');
            $('#editModalLabel').text('Edit Transfer');
            $('#editModal').modal('show');
        } else {
            console.error("Transfer not found for editing:", id);
        }
    });

    // Delete button click handler
    $(document).on('click', '.delete', function(e) {
        e.preventDefault();
        var id = $(this).data('id');
        console.log("Delete button clicked for id:", id);
        itemToDelete = window.filteredData.find(item => item.id === id);
        if (itemToDelete) {
            console.log("Found transfer for deletion:", itemToDelete);
            $('#deleteItemDetails').html(`
                <p><strong>Reference No:</strong> ${itemToDelete.referenceNo}</p>
                <p><strong>From:</strong> ${itemToDelete.from}</p>
                <p><strong>To:</strong> ${itemToDelete.to}</p>
                <p><strong>Amount:</strong> ${itemToDelete.amount}</p>
                <p><strong>Message Type:</strong> ${itemToDelete.messageType}</p>
                <p><strong>Status:</strong> ${itemToDelete.status}</p>
            `);
            $('#deleteModal').modal('show');
        } else {
            console.error("Transfer not found for deletion:", id);
        }
    });

    // Add new button click handler
    $("#addNewBtn").click(function() {
        console.log("Add new button clicked");

        // Get the next REF number
        const nextRefNumber = getMaxRefNumber() + 1;
        const paddedRefNumber = String(nextRefNumber).padStart(4, '0');

        // Reset form fields with default values
        $('#referenceNo').val(`REF${paddedRefNumber}`);
        $('#from').val('');
        $('#to').val('');
        $('#amount').val('');
        $('#messageType').val('pacs.008');
        $('#status').val('Active');

        currentItem = null;
        $('#editModalLabel').text('Add New Transfer');
        $('#editModal').modal('show');
    });

    // Save changes button click handler (for both edit and add)
    $("#saveChanges").off('click').on('click', function() {
        console.log("Save changes button clicked");
        let transferData = {
            referenceNo: $('#referenceNo').val(),
            from: $('#from').val(),
            to: $('#to').val(),
            amount: $('#amount').val(),
            messageType: $('#messageType').val(),
            status: $('#status').val(),
            lastUpdate: new Date().toISOString()
        };

        if (currentItem) {
            // Editing existing transfer
            transferData.id = currentItem.id;
            updateItem(transferData).then(() => {
                console.log("Transfer updated successfully");
                $('#editModal').modal('hide');
                applyFilter();
                window.fetchSummary();
            }).catch(error => {
                console.error("Error updating transfer:", error);
                alert("An error occurred while updating the transfer. Please try again.");
            });
        } else {
            // Adding new transfer
            addItem(transferData).then(() => {
                console.log("New transfer added successfully");
                $('#editModal').modal('hide');
                applyFilter();
                window.fetchSummary();
            }).catch(error => {
                console.error("Error adding new transfer:", error);
                alert("An error occurred while adding the new transfer. Please try again.");
            });
        }
    });

    // Confirm delete button click handler
    $("#confirmDelete").click(function() {
        console.log("Confirm delete button clicked");
        if (itemToDelete) {
            console.log("Deleting transfer:", itemToDelete);
            deleteItem(itemToDelete.id).then(() => {
                console.log("Transfer deleted successfully");
                $('#deleteModal').modal('hide');
                applyFilter();
                window.fetchSummary();  // Update summary
                itemToDelete = null;
            }).catch(error => {
                console.error("Error deleting transfer:", error);
                alert("An error occurred while deleting the transfer. Please try again.");
            });
        } else {
            console.error("No transfer selected for deletion");
        }
    });
});

// Function to center modals
function centerModal() {
    $(this).css('display', 'flex');
    var modalDialog = $(this).find('.modal-dialog');
    modalDialog.css({
        'display': 'flex',
        'align-items': 'center',
        'margin-top': 0,
        'margin-bottom': 0
    });
}

// Apply centerModal function to all modals
$('.modal').on('show.bs.modal', centerModal);
$(window).on('resize', function() {
    $('.modal:visible').each(centerModal);
});