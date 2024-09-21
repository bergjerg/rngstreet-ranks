document.addEventListener('DOMContentLoaded', () => {
    let editModeEnabled = false;
    const tableBody = document.querySelector('#rankConfigTable tbody');
    const applyChangesButton = document.getElementById('applyChangesButton');
    const addButton = document.getElementById('addButton');
    const editModeSwitch = document.getElementById('editModeSwitch');

    // Initially disable the Add button
    addButton.disabled = true;

    fetch('/get_rank_config')
        .then(response => response.json())
        .then(data => {
            data.forEach(rank => {
                const row = createRow(rank, false); // Rows from the server are not immediately editable
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error fetching rank config data:', error));

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
            const name = row.querySelector('.name-input').value;
            const description = row.querySelector('.description-input').value;
            const points = row.querySelector('.points-input').value;

            updates.push({ id, name, description, points });
        });

        fetch('/update_rank_config', {
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
        const newRow = createRow({ ID: '', NAME: '', DESCRIPTION: '', POINTS: '' }, true);
        tableBody.appendChild(newRow);
        applyChangesButton.disabled = false; // Enable the Apply Changes button since we now have changes to apply
    });

    function createRow(rank, isEditable) {
        const row = document.createElement('tr');
        row.dataset.id = rank.ID; // Ensure ID is set on the row element

        const disabledState = isEditable ? '' : 'disabled';

        row.innerHTML = `
            <td><input type="text" value="${rank.NAME}" class="name-input editable-field ${isEditable ? 'active-edit' : ''}" ${disabledState}></td>
            <td><input type="text" value="${rank.DESCRIPTION}" class="description-input editable-field ${isEditable ? 'active-edit' : ''}" ${disabledState}></td>
            <td><input type="number" value="${rank.POINTS}" class="points-input editable-field ${isEditable ? 'active-edit' : ''}" ${disabledState}></td>
        `;

        return row;
    }
});
