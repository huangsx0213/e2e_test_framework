(function(window) {
    // Global variables
    window.currentSortColumn = 7;  // Default sort by lastUpdate
    window.currentSortOrder = 'desc';

    // Mapping column index to field name
    const columnToFieldMap = {
        1: 'referenceNo',
        2: 'from',
        3: 'to',
        4: 'amount',
        5: 'messageType',
        6: 'status',
        7: 'lastUpdate'
    };

    function applyFilter() {
        if (window.isLoading) {
            console.log("Data is already loading, skipping this filter application");
            return;
        }
        window.isLoading = true;

        window.loadData()
            .then(() => {
                window.displayTable();
                window.updatePagination();
            })
            .catch(error => {
                console.error("Error applying filter:", error);
                alert("An error occurred while applying the filter. Please try again.");
            })
            .finally(() => {
                window.isLoading = false;
            });
    }

    function fetchSummary() {
        return fetch('/api/summary', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})  // No need to send any filter parameters
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(summary => {
            $("#totalAmount").text(`$${summary.totalAmount.toFixed(2)}`);
            $("#totalCount").text(summary.totalCount);
            $("#activeAmount").text(`$${summary.activeAmount.toFixed(2)}`);
            $("#inactiveAmount").text(`$${summary.inactiveAmount.toFixed(2)}`);
            $("#activeCount").text(summary.activeCount);
            $("#inactiveCount").text(summary.inactiveCount);
        })
        .catch(error => {
            console.error("Error fetching summary:", error);
        });
    }

    function updateSummary() {
        fetchSummary().catch(error => {
            console.error("Error updating summary:", error);
        });
    }

    $("#applyFilter").click(function() {
        if (!window.isLoading) {
            window.currentPage = 1;  // Reset to first page when applying a new filter
            applyFilter();
        }
    });

    $("#resetFilter").click(function() {
        if (window.isLoading) return;
        $("#statusFilter").val("");
        $("#minAmount").val("");
        $("#maxAmount").val("");
        window.currentPage = 1;  // Reset to first page when resetting filter
        applyFilter();
    });

    // Remove the event listener for status filter change
    // $("#statusFilter").off('change');

    // Event listeners for filter inputs to apply filter on change
    $("#minAmount, #maxAmount").on('change', function() {
        if (!window.isLoading) {
            window.currentPage = 1;
            applyFilter();
        }
    });

    // Expose necessary functions to global scope
    window.applyFilter = applyFilter;
    window.updateSummary = updateSummary;
    window.fetchSummary = fetchSummary;

})(window);