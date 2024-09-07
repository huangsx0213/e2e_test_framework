let itemToDelete;
let currentItem;

$(document).on('click', '.edit', function(e){
    e.preventDefault();
    var id = $(this).data('id');
    currentItem = window.data.find(item => item.id === id);
    if (currentItem) {
        $('#lastName').val(currentItem.lastName || '');
        $('#firstName').val(currentItem.firstName || '');
        $('#email').val(currentItem.email || '');
        $('#due').val(currentItem.due || '');
        $('#website').val(currentItem.website || '');
        $('#status').val(currentItem.status || '');
        $('#editModal').modal('show');
    } else {
        console.error("Item not found for editing:", id);
    }
});

$("#saveChanges").click(function(){
    if (currentItem) {
        currentItem.lastName = $('#lastName').val();
        currentItem.firstName = $('#firstName').val();
        currentItem.email = $('#email').val();
        currentItem.due = $('#due').val();
        currentItem.website = $('#website').val();
        currentItem.status = $('#status').val();
        currentItem.lastUpdate = new Date().toISOString();

        updateItem(currentItem).then(() => {
            $('#editModal').modal('hide');
            applyFilter();
            updateSummary();
        }).catch(error => {
            console.error("Error updating item:", error);
            alert("An error occurred while updating the item. Please try again.");
        });
    }
});

$(document).on('click', '.delete', function(e){
    e.preventDefault();
    var id = $(this).data('id');
    itemToDelete = window.data.find(item => item.id === id);
    if (itemToDelete) {
        $('#deleteItemDetails').html(`
            <p><strong>Last Name:</strong> ${itemToDelete.lastName}</p>
            <p><strong>First Name:</strong> ${itemToDelete.firstName}</p>
            <p><strong>Email:</strong> ${itemToDelete.email}</p>
            <p><strong>Due:</strong> ${itemToDelete.due}</p>
            <p><strong>Status:</strong> ${itemToDelete.status}</p>
        `);
        $('#deleteModal').modal('show');
    } else {
        console.error("Item not found for deletion:", id);
    }
});

$("#confirmDelete").click(function(){
    if (itemToDelete) {
        deleteItem(itemToDelete.id).then(() => {
            window.data = window.data.filter(item => item.id !== itemToDelete.id);
            $('#deleteModal').modal('hide');
            applyFilter();
            updateSummary();
            itemToDelete = null;
        }).catch(error => {
            console.error("Error deleting item:", error);
            alert("An error occurred while deleting the item. Please try again.");
        });
    }
});

$("#addNewBtn").click(function(){
    var newId = window.data.length > 0 ? Math.max(...window.data.map(item => item.id)) + 1 : 1;
    var newItem = {
        id: newId,
        lastName: "New",
        firstName: "Person",
        email: "new@example.com",
        due: "$0.00",
        website: "http://www.example.com",
        status: "Active",
        lastUpdate: new Date().toISOString()
    };

    addItem(newItem).then(response => {
        window.data.push(response.item);
        applyFilter();
        updateSummary();
    }).catch(error => {
        console.error("Error adding new item:", error);
        alert("An error occurred while adding a new item. Please try again.");
    });
});