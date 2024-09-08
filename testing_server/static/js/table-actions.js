// Global variables
let itemToDelete;
let currentItem;

$(document).ready(function() {
    console.log("table-actions.js loaded");

    // Edit button click handler
    $(document).on('click', '.edit', function(e) {
        e.preventDefault();
        var id = $(this).data('id');
        console.log("Edit button clicked for id:", id);
        currentItem = window.filteredData.find(item => item.id === id);
        if (currentItem) {
            console.log("Found item for editing:", currentItem);
            $('#referenceNo').val(currentItem.referenceNo || '');
            $('#name').val(currentItem.name || '');
            $('#email').val(currentItem.email || '');
            $('#amount').val(currentItem.amount || '');
            $('#website').val(currentItem.website || '');
            $('#status').val(currentItem.status || '');
            $('#editModalLabel').text('Edit Item');
            $('#editModal').modal('show');
        } else {
            console.error("Item not found for editing:", id);
        }
    });

    // Delete button click handler
    $(document).on('click', '.delete', function(e) {
        e.preventDefault();
        var id = $(this).data('id');
        console.log("Delete button clicked for id:", id);
        itemToDelete = window.filteredData.find(item => item.id === id);
        if (itemToDelete) {
            console.log("Found item for deletion:", itemToDelete);
            $('#deleteItemDetails').html(`
                <p><strong>Reference No:</strong> ${itemToDelete.referenceNo}</p>
                <p><strong>Name:</strong> ${itemToDelete.name}</p>
                <p><strong>Email:</strong> ${itemToDelete.email}</p>
                <p><strong>Amount:</strong> ${itemToDelete.amount}</p>
                <p><strong>Status:</strong> ${itemToDelete.status}</p>
            `);
            $('#deleteModal').modal('show');
        } else {
            console.error("Item not found for deletion:", id);
        }
    });

    // Save changes button click handler
    $("#saveChanges").click(function() {
        console.log("Save changes button clicked");
        if (currentItem) {
            console.log("Current item before update:", currentItem);
            currentItem.referenceNo = $('#referenceNo').val();
            currentItem.name = $('#name').val();
            currentItem.email = $('#email').val();
            currentItem.amount = $('#amount').val();
            currentItem.website = $('#website').val();
            currentItem.status = $('#status').val();
            currentItem.lastUpdate = new Date().toISOString();
            console.log("Current item after update:", currentItem);

            updateItem(currentItem).then(() => {
                console.log("Item updated successfully");
                $('#editModal').modal('hide');
                applyFilter();
                window.fetchSummary();  // Update summary
            }).catch(error => {
                console.error("Error updating item:", error);
                alert("An error occurred while updating the item. Please try again.");
            });
        } else {
            console.error("No item selected for update");
        }
    });

    // Confirm delete button click handler
    $("#confirmDelete").click(function() {
        console.log("Confirm delete button clicked");
        if (itemToDelete) {
            console.log("Deleting item:", itemToDelete);
            deleteItem(itemToDelete.id).then(() => {
                console.log("Item deleted successfully");
                $('#deleteModal').modal('hide');
                applyFilter();
                window.fetchSummary();  // Update summary
                itemToDelete = null;
            }).catch(error => {
                console.error("Error deleting item:", error);
                alert("An error occurred while deleting the item. Please try again.");
            });
        } else {
            console.error("No item selected for deletion");
        }
    });

    // Add new button click handler
    $("#addNewBtn").click(function() {
        console.log("Add new button clicked");
        // Reset form fields
        $('#referenceNo').val('');
        $('#name').val('');
        $('#email').val('');
        $('#amount').val('');
        $('#website').val('');
        $('#status').val('Active');
        currentItem = null;
        $('#editModalLabel').text('Add New Item');
        $('#editModal').modal('show');
    });

// Save changes button click handler
$("#saveChanges").off('click').on('click', function() {
    console.log("Save changes button clicked");
    if (currentItem) {
        console.log("Current item before update:", currentItem);
        currentItem.referenceNo = $('#referenceNo').val();
        currentItem.name = $('#name').val();
        currentItem.email = $('#email').val();
        currentItem.amount = $('#amount').val();
        currentItem.website = $('#website').val();
        currentItem.status = $('#status').val();
        currentItem.lastUpdate = new Date().toISOString();
        console.log("Current item after update:", currentItem);

        updateItem(currentItem).then(() => {
            console.log("Item updated successfully");
            $('#editModal').modal('hide');
            applyFilter();
            window.fetchSummary();  // Update summary
        }).catch(error => {
            console.error("Error updating item:", error);
            alert("An error occurred while updating the item. Please try again.");
        });
    } else {
        console.error("No item selected for update");
    }
});
});