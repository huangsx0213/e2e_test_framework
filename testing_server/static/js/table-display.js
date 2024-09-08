(function(window) {
    // Check if fetchSummary is available
    if (typeof window.fetchSummary !== 'function') {
        console.error('fetchSummary function is not available. Make sure filtering.js is loaded before table-display.js');
    }

    function displayTable() {
        console.log("Displaying table for page:", window.currentPage);
        var tbody = $("#dataTable tbody");
        tbody.empty();

        if (window.filteredData.length === 0) {
            tbody.html('<tr><td colspan="9" class="text-center">No data available</td></tr>');
            return;
        }

        $.each(window.filteredData, function(index, item) {
            var row = $("<tr>");
            row.append($("<td>").append($("<input>", {type: "checkbox", class: "rowCheckbox", "data-id": item.id})));
            row.append($("<td>").text(item.referenceNo || ''));
            row.append($("<td>").text(item.from || ''));
            row.append($("<td>").text(item.to || ''));
            row.append($("<td>").text(item.amount || ''));
            row.append($("<td>").text(item.messageType || ''));
            row.append($("<td>").text(item.status || ''));
            row.append($("<td>").text(item.lastUpdate ? new Date(item.lastUpdate).toLocaleString() : ''));
            row.append($("<td>").append(
                $("<button>", {class: "edit btn btn-outline-primary me-1", "data-id": item.id}).text("Edit"),
                $("<button>", {class: "delete btn btn-outline-danger", "data-id": item.id}).text("Delete")
            ));
            tbody.append(row);
        });

        updatePagination();
        updateTableInfo();
        updateFloatingBar();

        // Update tablesorter's sort state
        var sortingCss = window.currentSortOrder === 'asc' ? 'tablesorter-headerAsc' : 'tablesorter-headerDesc';
        $("#dataTable thead th").removeClass('tablesorter-headerAsc tablesorter-headerDesc');
        $("#dataTable thead th:eq(" + window.currentSortColumn + ")").addClass(sortingCss);

        $("#dataTable").trigger("update");
    }

    function updatePagination() {
        $("#pageInput").val(window.currentPage);
        $("#prevPage").prop("disabled", window.currentPage === 1);
        $("#nextPage").prop("disabled", window.currentPage === window.totalPages);
        $("#pageInfo").text(`Page ${window.currentPage} of ${window.totalPages}`);
    }

    function updateTableInfo() {
        var start = (window.currentPage - 1) * window.itemsPerPage + 1;
        var end = Math.min(window.currentPage * window.itemsPerPage, window.totalItems);

        $("#dataInfo").text(`Showing ${start} to ${end} of ${window.totalItems} entries`);
    }

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

    function initTableSorter() {
        $("#dataTable").tablesorter({
            headers: {
                0: { sorter: false },
                8: { sorter: false }
            },
            sortList: [[7,1]],  // Default sort by lastUpdate in descending order
            widgets: ['zebra'],
            widgetOptions: {
                zebra: ['even', 'odd'],
            },
        }).on('sortEnd', function(e, table) {
            var sortList = table.config.sortList;
            if (sortList.length > 0) {
                window.currentSortColumn = sortList[0][0];
                window.currentSortOrder = sortList[0][1] === 0 ? 'asc' : 'desc';
                loadAndDisplayData();
            }
        });
    }

    function loadAndDisplayData(fetchSummaryFlag = false) {
        if (window.isLoading) {
            console.log("Data is already loading, skipping this request");
            return Promise.resolve();
        }
        window.isLoading = true;

        return window.loadData()
            .then(() => {
                displayTable();
                updatePagination();
                if (fetchSummaryFlag) {
                    return window.fetchSummary();
                }
            })
            .catch(error => {
                console.error("Error loading data:", error);
                alert("An error occurred while loading the data. Please try again.");
            })
            .finally(() => {
                window.isLoading = false;
            });
    }

    $(document).ready(function() {
        loadAndDisplayData(true);
        $("#prevPage").click(function() {
            if (window.currentPage > 1 && !window.isLoading) {
                window.currentPage--;
                loadAndDisplayData(false);
            }
        });

        $("#nextPage").click(function() {
            if (window.currentPage < window.totalPages && !window.isLoading) {
                window.currentPage++;
                loadAndDisplayData(false);
            }
        });

        $("#goToPage").click(function() {
            if (window.isLoading) return;
            var pageNumber = parseInt($("#pageInput").val());
            if (pageNumber >= 1 && pageNumber <= window.totalPages) {
                window.currentPage = pageNumber;
                loadAndDisplayData(false);
            } else {
                alert("Invalid page number. Please enter a number between 1 and " + window.totalPages);
            }
        });

        $("#pageInput").on('keypress', function(e) {
            if (e.which == 13) { // Enter key
                $("#goToPage").click();
            }
        });

        $(document).on('click', '#selectAll', function(){
            $(".rowCheckbox").prop('checked', this.checked);
            updateFloatingBar();
        });

        $(document).on('click', '.rowCheckbox', function(){
            var allChecked = $(".rowCheckbox:not(:checked)").length === 0;
            $("#selectAll").prop('checked', allChecked);
            updateFloatingBar();
        });
    });

    // Expose necessary functions to global scope
    window.displayTable = displayTable;
    window.updatePagination = updatePagination;
    window.updateTableInfo = updateTableInfo;
    window.updateFloatingBar = updateFloatingBar;
    window.initTableSorter = initTableSorter;
    window.loadAndDisplayData = loadAndDisplayData;

})(window);