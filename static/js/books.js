function setupTableFilter(inputId, tableId, emptyStateId) {
    var input = document.getElementById(inputId);
    var table = document.getElementById(tableId);
    var emptyState = document.getElementById(emptyStateId);
    if (!input || !table) {
        return;
    }

    var rows = Array.from(table.querySelectorAll("tbody tr"));

    function applyFilter() {
        var query = input.value.toLowerCase().trim();
        var visible = 0;
        rows.forEach(function (row) {
            var content = row.getAttribute("data-search") || "";
            var match = query === "" || content.indexOf(query) !== -1;
            row.style.display = match ? "" : "none";
            if (match) {
                visible += 1;
            }
        });
        if (emptyState) {
            emptyState.classList.toggle("hidden", visible > 0);
        }
    }

    input.addEventListener("input", applyFilter);
}

setupTableFilter("bookSearch", "booksTable", "noResults");
setupTableFilter("issueBookSearch", "issueBooksTable", "issueNoResults");
