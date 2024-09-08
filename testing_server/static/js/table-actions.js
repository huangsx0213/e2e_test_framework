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
// 在添加新项目后
$("#addNewBtn").click(function(){
    // ... 添加项目的代码 ...
    addItem(newItem).then(response => {
        window.data.push(response.item);
        applyFilter();
        window.fetchSummary();  // 更新摘要
    }).catch(error => {
        console.error("Error adding new item:", error);
        alert("An error occurred while adding a new item. Please try again.");
    });
});

// 在编辑项目后
$("#saveChanges").click(function(){
    if (currentItem) {
        // ... 更新项目的代码 ...
        updateItem(currentItem).then(() => {
            $('#editModal').modal('hide');
            applyFilter();
            window.fetchSummary();  // 更新摘要
        }).catch(error => {
            console.error("Error updating item:", error);
            alert("An error occurred while updating the item. Please try again.");
        });
    }
});

// 在删除项目后
$("#confirmDelete").click(function(){
    if (itemToDelete) {
        deleteItem(itemToDelete.id).then(() => {
            window.data = window.data.filter(item => item.id !== itemToDelete.id);
            $('#deleteModal').modal('hide');
            applyFilter();
            window.fetchSummary();  // 更新摘要
            itemToDelete = null;
        }).catch(error => {
            console.error("Error deleting item:", error);
            alert("An error occurred while deleting the item. Please try again.");
        });
    }
});