// Global variables
window.data = [];
window.filteredData = [];
window.itemsPerPage = 10;
window.currentPage = 1;
window.totalPages = 1;

function loadData() {
    return fetch('/api/data')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(jsonData => {
            console.log("JSON data loaded successfully:", jsonData);
            if (jsonData && jsonData.data && Array.isArray(jsonData.data)) {
                window.data = jsonData.data;
                window.filteredData = [...window.data];
                return window.data;
            } else {
                throw new Error("Invalid JSON data structure");
            }
        });
}

function saveData(newData) {
    return fetch('/api/data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ data: newData }),
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
    return fetch(`/api/delete_item/${itemId}`, {
        method: 'DELETE',
    }).then(response => response.json());
}