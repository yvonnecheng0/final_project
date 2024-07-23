document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.toggle-column');

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const columnClass = this.dataset.column;
            const columns = document.querySelectorAll(`.${columnClass}`);
            columns.forEach(column => {
                column.style.display = this.checked ? '' : 'none';
            });
        });
    });
});
