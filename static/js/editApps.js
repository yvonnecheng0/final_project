document.addEventListener('DOMContentLoaded', function() {
    const editableElements = document.querySelectorAll('.editable');

    editableElements.forEach(element => {
        element.addEventListener('click', function() {
            const originalText = this.textContent;
            const input = document.createElement('input');
            input.type = 'text';
            input.value = originalText;
            input.addEventListener('blur', function() {
                const newText = input.value;
                const applicationId = element.dataset.id;
                const column = element.dataset.column;
                element.textContent = newText;

                // Preserve scroll position
                const scrollTop = window.scrollY;

                fetch('/update_application', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        application_id: applicationId,
                        column: column,
                        value: newText
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (!data.success) {
                        element.textContent = originalText;
                        alert('Error updating application');
                    }
                })
                .finally(() => {
                    window.scrollTo(0, scrollTop);  // Restore scroll position
                });
            });

            this.textContent = '';
            this.appendChild(input);
            input.focus();
        });
    });
});
