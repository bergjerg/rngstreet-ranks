document.addEventListener('DOMContentLoaded', () => {
    let editModeEnabled = false;
    const tableBody = document.querySelector('#pointsConfigTable tbody');
    const applyChangesButton = document.getElementById('applyChangesButton');
    const addButton = document.getElementById('addButton');
    const editModeSwitch = document.getElementById('editModeSwitch');

    // Initially disable the Add button
    addButton.disabled = true;

    fetch('/get_points_config')
        .then(response => response.json())
        .then(data => {
            data.forEach(config => {
                const row = createRow(config, false); // Rows from the server are not immediately editable
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error fetching points config data:', error));

    editModeSwitch.addEventListener('change', () => {
        editModeEnabled = editModeSwitch.checked;
        document.querySelector('.table-container').classList.toggle('editable', editModeEnabled);
        
        document.querySelectorAll('.editable-field').forEach(field => {
            field.disabled = !editModeEnabled;
            field.classList.toggle('active-edit', editModeEnabled);
        });

        // Enable or disable the Add button based on edit mode
        addButton.disabled = !editModeEnabled;
        applyChangesButton.disabled = !editModeEnabled;
    });

    applyChangesButton.addEventListener('click', () => {
        const rows = tableBody.querySelectorAll('tr');
        const updates = [];

        rows.forEach(row => {
            const id = row.dataset.id || ''; // Use dataset to retrieve the ID
            const code = row.querySelector('.code-input').value;
            const name = row.querySelector('.name-input').value;
            const value = row.querySelector('.value-input').value;
            const monthlyLimit = row.querySelector('.monthly-limit-input').value;

            updates.push({ id, code, name, value, monthlyLimit });
        });

        fetch('/update_points_config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updates)
        })
        .then(response => {
            if (response.ok) {
                alert('Changes applied successfully');
                applyChangesButton.disabled = true;
            } else {
                alert('Failed to apply changes');
            }
        });
    });

    addButton.addEventListener('click', () => {
        if (!editModeEnabled) return; // Ensure the button only works in edit mode

        // Create a new row with empty editable fields, which are immediately editable
        const newRow = createRow({ ID: '', CODE: '', NAME: '', VALUE: '', MONTHLY_LIMIT: '' }, true);
        tableBody.appendChild(newRow);
        applyChangesButton.disabled = false; // Enable the Apply Changes button since we now have changes to apply
    });

    function createRow(config, isEditable) {
        const row = document.createElement('tr');
        row.dataset.id = config.ID; // Ensure ID is set on the row element

        const disabledState = isEditable ? '' : 'disabled';

        row.innerHTML = `
            <td><input type="text" value="${config.CODE}" class="code-input editable-field ${isEditable ? 'active-edit' : ''}" ${disabledState}></td>
            <td><input type="text" value="${config.NAME}" class="name-input editable-field ${isEditable ? 'active-edit' : ''}" ${disabledState}></td>
            <td><input type="number" step="0.1" value="${config.VALUE}" class="value-input editable-field ${isEditable ? 'active-edit' : ''}" ${disabledState}></td>
            <td><input type="number" value="${config.MONTHLY_LIMIT}" class="monthly-limit-input editable-field ${isEditable ? 'active-edit' : ''}" ${disabledState}></td>
        `;

        return row;
    }
});
