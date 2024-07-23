document.addEventListener('DOMContentLoaded', function () {
    const checkboxes = document.querySelectorAll('.toggle-column');

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const columnClass = this.getAttribute('data-column');
            const isChecked = this.checked;

            const cells = document.querySelectorAll(`.${columnClass}`);
            cells.forEach(cell => {
                cell.style.display = isChecked ? '' : 'none';
            });
        });
    });
});
