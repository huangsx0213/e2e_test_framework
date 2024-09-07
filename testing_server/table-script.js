$(function(){
    var data = [];
    var filteredData = [];
    var itemsPerPage = 10;
    var currentPage = 1;
    var totalPages = 1;
    var newStatus;

    // Load JSON data
    fetch('table.json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(jsonData => {
            console.log("JSON data loaded successfully:", jsonData);
            if (jsonData && jsonData.data && Array.isArray(jsonData.data)) {
                data = jsonData.data;
                filteredData = [...data];
                totalPages = Math.ceil(filteredData.length / itemsPerPage);
                displayTable(currentPage);
                updateSummary();
            } else {
                throw new Error("Invalid JSON data structure");
            }
        })
        .catch(error => {
            console.error("Error loading or parsing JSON data:", error);
            $('#dataTable tbody').html('<tr><td colspan="9" class="text-center">Error loading data. Please try again later.</td></tr>');
        });

    function displayTable(page) {
        console.log("Displaying table for page:", page);
        var start = (page - 1) * itemsPerPage;
        var end = start + itemsPerPage;
        var pageData = filteredData.slice(start, end);

        var tbody = $("#dataTable tbody");
        tbody.empty();

        if (pageData.length === 0) {
            tbody.html('<tr><td colspan="9" class="text-center">No data available</td></tr>');
            return;
        }

        $.each(pageData, function(index, item) {
            var row = $("<tr>");
            row.append($("<td>").append($("<input>", {type: "checkbox", class: "rowCheckbox", "data-id": item.id})));
            row.append($("<td>").text(item.lastName || ''));
            row.append($("<td>").text(item.firstName || ''));
            row.append($("<td>").text(item.email || ''));
            row.append($("<td>").text(item.due || ''));
            row.append($("<td>").text(item.website || ''));
            row.append($("<td>").text(item.status || ''));
            row.append($("<td>").text(item.lastUpdate ? new Date(item.lastUpdate).toLocaleString() : ''));
            row.append($("<td>").append(
                $("<a>", {href: "#", class: "edit btn btn-sm btn-outline-primary me-2", "data-id": item.id}).text("Edit"),
                $("<a>", {href: "#", class: "delete btn btn-sm btn-outline-danger", "data-id": item.id}).text("Delete")
            ));
            tbody.append(row);
        });

        updatePagination();
        updateTableInfo();
        $("#dataTable").trigger("update");
        updateFloatingBar();
    }

    function updatePagination() {
        $("#pageInput").val(currentPage);
        $("#prevPage").prop("disabled", currentPage === 1);
        $("#nextPage").prop("disabled", currentPage === totalPages);
    }

    function updateTableInfo() {
        var totalItems = filteredData.length;
        var start = (currentPage - 1) * itemsPerPage + 1;
        var end = Math.min(start + itemsPerPage - 1, totalItems);

        $("#pageInfo").text(`Page ${currentPage} of ${totalPages}`);
        $("#dataInfo").text(`Showing ${start} to ${end} of ${totalItems} entries`);
    }

    function updateSummary() {
        var totalAmount = 0;
        var activeAmount = 0;
        var inactiveAmount = 0;
        var activeCount = 0;
        var inactiveCount = 0;
        var totalCount = filteredData.length;

        filteredData.forEach(item => {
            var amount = parseFloat(item.due.replace('$', ''));
            if (!isNaN(amount)) {
                totalAmount += amount;
                if (item.status === 'Active') {
                    activeAmount += amount;
                    activeCount++;
                } else {
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

    $("#dataTable").tablesorter({
        headers: {
            0: { sorter: false },
            8: { sorter: false }
        }
    });

    // Handle select all checkbox
    $("#selectAll").click(function(){
        $(".rowCheckbox").prop('checked', this.checked);
        updateFloatingBar();
    });

    // Update select all checkbox when individual checkboxes change
    $(document).on('click', '.rowCheckbox', function(){
        var allChecked = $(".rowCheckbox:checked").length === $(".rowCheckbox").length;
        $("#selectAll").prop('checked', allChecked);
        updateFloatingBar();
    });

    function updateFloatingBar() {
        var selectedCheckboxes = $(".rowCheckbox:checked");
        if (selectedCheckboxes.length > 0) {
            var selectedIds = selectedCheckboxes.map(function() {
                return $(this).data('id');
            }).get();
            var selectedItems = filteredData.filter(item => selectedIds.includes(item.id));
            var allActive = selectedItems.every(item => item.status === "Active");
            var allInactive = selectedItems.every(item => item.status === "Inactive");

            $("#selectedCount").text(`${selectedItems.length} item(s) selected`);
            $("#calculateBtn").show();
            $("#calculationResult").text('');  // Clear previous calculation

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

    $("#calculateBtn").click(function() {
        var selectedCheckboxes = $(".rowCheckbox:checked");
        var selectedIds = selectedCheckboxes.map(function() {
            return $(this).data('id');
        }).get();
        var selectedItems = filteredData.filter(item => selectedIds.includes(item.id));

        var totalDue = calculateTotalAmount(selectedItems);

        $("#calculationResult").text(`Total amount: $${totalDue.toFixed(2)}`);
    });

    function calculateTotalAmount(items) {
        return items.reduce((sum, item) => {
            var amount = parseFloat(item.due.replace('$', ''));
            return sum + (isNaN(amount) ? 0 : amount);
        }, 0);
    }

    $("#setStatusBtn").click(function() {
        newStatus = $(this).text() === "Set Active" ? "Active" : "Inactive";
        var selectedCheckboxes = $(".rowCheckbox:checked");
        var selectedIds = selectedCheckboxes.map(function() {
            return $(this).data('id');
        }).get();
        var selectedItems = filteredData.filter(item => selectedIds.includes(item.id));

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

        data = data.map(item => {
            if (selectedIds.includes(item.id)) {
                return {...item, status: newStatus, lastUpdate: new Date().toISOString()};
            }
            return item;
        });

        applyFilter();
        $("#statusChangeModal").modal('hide');
        $("#floatingBar").hide();
    });

    var currentItem;

    // Handle edit button click
    $(document).on('click', '.edit', function(e){
        e.preventDefault();
        var id = $(this).data('id');
        currentItem = data.find(item => item.id === id);
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

    // Handle save changes button click
    $("#saveChanges").click(function(){
        if (currentItem) {
            currentItem.lastName = $('#lastName').val();
            currentItem.firstName = $('#firstName').val();
            currentItem.email = $('#email').val();
            currentItem.due = $('#due').val();
            currentItem.website = $('#website').val();
            currentItem.status = $('#status').val();
            currentItem.lastUpdate = new Date().toISOString();
            $('#editModal').modal('hide');
            applyFilter();
        }
    });

    // Handle delete button click
    $(document).on('click', '.delete', function(e){
        e.preventDefault();
        var id = $(this).data('id');
        if(confirm('Are you sure you want to delete this row?')) {
            data = data.filter(item => item.id !== id);
            applyFilter();
        }
    });

    // Handle add new button click
    $("#addNewBtn").click(function(){
        var newId = data.length > 0 ? Math.max(...data.map(item => item.id)) + 1 : 1;
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
        data.push(newItem);
        applyFilter();
    });

    // Handle delete selected button click
    $("#deleteSelectedBtn").click(function(){
        var selectedIds = $(".rowCheckbox:checked").map(function() {
            return $(this).data('id');
        }).get();
        if (selectedIds.length > 0 && confirm('Are you sure you want to delete all selected rows?')) {
            data = data.filter(item => !selectedIds.includes(item.id));
            $("#selectAll").prop('checked', false);
            applyFilter();
        }
    });

    // Handle previous page button click
    $("#prevPage").click(function() {
        if (currentPage > 1) {
            currentPage--;
            displayTable(currentPage);
        }
    });

    // Handle next page button click
    $("#nextPage").click(function() {
        if (currentPage < totalPages) {
            currentPage++;
            displayTable(currentPage);
        }
    });

    // Handle go to page button click
    $("#goToPage").click(function() {
        var pageNumber = parseInt($("#pageInput").val());
        if (pageNumber >= 1 && pageNumber <= totalPages) {
            currentPage = pageNumber;
            displayTable(currentPage);
        } else {
            alert("Invalid page number. Please enter a number between 1 and " + totalPages);
        }
    });

    // Allow Enter key in page input to trigger go to page
    $("#pageInput").keypress(function(e) {
        if (e.which == 13) {
            $("#goToPage").click();
            return false;
        }
    });

    // Filter functionality
    function applyFilter() {
        var status = $("#statusFilter").val();
        var minAmount = parseFloat($("#minAmount").val()) || 0;
        var maxAmount = parseFloat($("#maxAmount").val()) || Infinity;

        filteredData = data.filter(item => {
            var amount = parseFloat(item.due.replace('$', ''));
            return (status === "" || item.status === status) &&
                   (amount >= minAmount && amount <= maxAmount);
        });

        totalPages = Math.ceil(filteredData.length / itemsPerPage);
        currentPage = 1;
        displayTable(currentPage);
        updateSummary();
    }

    $("#applyFilter").click(applyFilter);

    $("#resetFilter").click(function() {
        $("#statusFilter").val("");
        $("#minAmount").val("");
        $("#maxAmount").val("");
        filteredData = [...data];
        totalPages = Math.ceil(filteredData.length / itemsPerPage);
        currentPage = 1;
        displayTable(currentPage);
        updateSummary();
    });

    // Initialize tooltips
    $('[data-toggle="tooltip"]').tooltip();

    // Initialize the table
    displayTable(currentPage);
});