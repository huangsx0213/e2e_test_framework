let itemToDelete;
let currentItem;

$(document).on('click', '.edit', function(e){
    e.preventDefault();
    var id = $(this).data('id');
    currentItem = window.data.find(item => item.id === id);
    if (currentItem) {
        $('#referenceNo').val(currentItem.referenceNo || '');
        $('#name').val(currentItem.name || '');
        $('#email').val(currentItem.email || '');
        $('#amount').val(currentItem.amount || '');
        $('#website').val(currentItem.website || '');
        $('#status').val(currentItem.status || '');
        $('#editModal').modal('show');
    } else {
        console.error("Item not found for editing:", id);
    }
});

$("#saveChanges").click(function(){
    if (currentItem) {
        currentItem.referenceNo = $('#referenceNo').val();
        currentItem.name = $('#name').val();
        currentItem.email = $('#email').val();
        currentItem.amount = $('#amount').val();
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
        referenceNo: "New",
        name: "Person",
        email: "new@example.com",
        amount: "$0.00",
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