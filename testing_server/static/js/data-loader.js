// Global variables
window.data = [];
window.filteredData = [];
window.itemsPerPage = 10;
window.currentPage = 1;
window.totalPages = 1;
window.totalItems = 0;
window.currentSortColumn = 7;  // Default sort by lastUpdate
window.currentSortOrder = 'desc';
window.isLoading = false;  // Add this flag to prevent multiple simultaneous loads

// Mapping column index to field name
const columnToFieldMap = {
    1: 'referenceNo',
    2: 'name',
    3: 'email',
    4: 'amount',
    5: 'website',
    6: 'status',
    7: 'lastUpdate'
};

function loadData(params = {}) {
    console.log("Loading data...");

    const payload = {
        action: 'get',
        filter: {
            status: $("#statusFilter").val(),
            minAmount: $("#minAmount").val(),
            maxAmount: $("#maxAmount").val()
        },
        sort: {
            field: columnToFieldMap[window.currentSortColumn] || 'lastUpdate',
            order: window.currentSortOrder
        },
        page: window.currentPage,
        itemsPerPage: window.itemsPerPage
    };

    return fetch('/api/data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(jsonData => {
        console.log("JSON data loaded successfully:", jsonData);
        if (jsonData && jsonData.data && Array.isArray(jsonData.data)) {
            window.filteredData = jsonData.data;
            window.totalItems = jsonData.totalItems;
            window.totalPages = jsonData.totalPages;
            console.log("Total pages:", window.totalPages);
            console.log("Current page:", window.currentPage);
            console.log("Total items:", window.totalItems);
            return window.filteredData;
        } else {
            throw new Error("Invalid JSON data structure");
        }
    })
    .catch(error => {
        console.error("Error loading data:", error);
        throw error;
    });
}

function saveData(newData) {
    return fetch('/api/data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: 'update', data: newData }),
    }).then(response => response.json());
}

function addItem(item) {
    return fetch('/api/add_item', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(item),
    }).then(response => response.json());
}

function updateItem(item) {
    return fetch(`/api/update_item/${item.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(item),
    }).then(response => response.json());
}

function deleteItem(itemId) {
    return fetch('/api/data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: 'delete', id: itemId }),
    }).then(response => response.json());
}

function bulkUpdateStatus(ids, status) {
    return fetch('/api/bulk_update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ids: ids, status: status }),
    }).then(response => response.json());
}

// Expose necessary functions to global scope
window.loadData = loadData;
window.saveData = saveData;
window.addItem = addItem;
window.updateItem = updateItem;
window.deleteItem = deleteItem;
window.bulkUpdateStatus = bulkUpdateStatus;