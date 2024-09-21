document.addEventListener('DOMContentLoaded', () => {
    let dataChanged = false;

    const monthHeading = document.getElementById('monthHeading');

    function updateSaveAllButtonState() {
        const saveAllButton = document.querySelector('#saveAllButton');
        saveAllButton.disabled = !dataChanged;
    }

    function updateTotalPoints(row) {
        const xpPoints = parseFloat(row.querySelector('.xp-points').textContent) || 0;
        const ehbPoints = parseFloat(row.querySelector('.ehb-points').textContent) || 0;
        const eventPoints = parseFloat(row.querySelector('.editable.event').value) || 0;
        const splitPoints = parseFloat(row.querySelector('.editable.split').value) || 0;
        const timePoints = parseFloat(row.querySelector('.editable.time').value) || 0;
        const totalPointsCell = row.querySelector('.total-points');
        const totalPoints = xpPoints + ehbPoints + eventPoints + splitPoints + timePoints;
        totalPointsCell.textContent = totalPoints.toFixed(1);
    }

    function loadMonthsAndData() {
        fetch('/get_months')
            .then(response => response.json())
            .then(months => {
                const monthSelect = document.getElementById('monthSelect');
                monthSelect.innerHTML = ''; // Clear existing options
                
                // Add a placeholder option
                const placeholderOption = document.createElement('option');
                placeholderOption.value = '';
                placeholderOption.textContent = 'Select Month';
                placeholderOption.disabled = true;
                placeholderOption.selected = true;
                monthSelect.appendChild(placeholderOption);

                months.forEach(month => {
                    const option = document.createElement('option');
                    option.value = month;
                    option.textContent = formatMonth(month);
                    monthSelect.appendChild(option);
                });

                // Automatically load data for the first available month
                if (months.length > 0) {
                    loadDataForMonth(months[0]);
                    updateMonthHeading(months[0]);
                }
            })
            .catch(error => console.error('Error fetching months:', error));
    }

    function loadDataForMonth(month) {
        fetch(`/points_tracking_data?month=${month}`)
            .then(response => response.json())
            .then(data => {
                const tableBody = document.querySelector('#pointsTable tbody');
                tableBody.innerHTML = '';

                data.forEach(row => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td class="name-column">${row.NAME}</td>
                        <td class="rsn-column">${row.RSN}</td>
                        <td class="total-points">${row.TOTAL_POINTS}</td>
                        <td class="xp-points">${row.XP_POINTS}</td>
                        <td class="ehb-points">${row.EHB_POINTS}</td>
                        <td><input type="text" value="${row.EVENT_POINTS}" data-wom-id="${row.WOM_ID}" class="editable event" /></td>
                        <td><input type="text" value="${row.SPLIT_POINTS}" data-wom-id="${row.WOM_ID}" class="editable split" /></td>
                        <td><input type="text" value="${row.TIME_POINTS}" data-wom-id="${row.WOM_ID}" class="editable time" /></td>
                        <td><button class="apply-button" data-wom-id="${row.WOM_ID}" data-month="${month}" disabled>Apply</button></td>
                    `;
                    tableBody.appendChild(tr);
                });

                document.querySelectorAll('.editable').forEach(input => {
                    input.addEventListener('input', () => {
                        dataChanged = true;
                        updateSaveAllButtonState();
                        const applyButton = input.closest('tr').querySelector('.apply-button');
                        applyButton.disabled = false;
                    });
                });

                document.querySelectorAll('.apply-button').forEach(button => {
                    button.addEventListener('click', () => {
                        const row = button.closest('tr');
                        const inputs = row.querySelectorAll('.editable');
                        const womId = button.dataset.womId;
                        const updatedRow = {
                            WOM_ID: womId,
                            MONTH: month,
                            EVENT_POINTS: inputs[0].value,
                            SPLIT_POINTS: inputs[1].value,
                            TIME_POINTS: inputs[2].value
                        };
                        fetch(`/update_points/${womId}/${month}`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(updatedRow),
                        })
                        .then(response => response.json())
                        .then(() => {
                            updateTotalPoints(row);
                            button.disabled = true;
                            dataChanged = Array.from(document.querySelectorAll('.editable')).some(input => input.value !== '');
                            updateSaveAllButtonState();
                        })
                        .catch(error => console.error('Error updating points data:', error));
                    });
                });
            })
            .catch(error => console.error('Error fetching points data:', error));
    }

    function updateMonthHeading(month) {
        if (month === '0') {
            monthHeading.textContent = "Revs Old System - Pre Sept 2021";
        } else {
            const formattedMonth = formatMonth(month);
            monthHeading.textContent = `${formattedMonth}`;
        }
    }

    function formatMonth(month) {
        if (month === '0' || month === 0) {
            return "Revs Old System";
        }
        const year = Math.floor(month / 100);
        const monthIndex = (month % 100) - 1;
        const monthNames = ["January", "February", "March", "April", "May", "June",
                            "July", "August", "September", "October", "November", "December"];
        return `${monthNames[monthIndex]} ${year}`;
    }

    document.getElementById('monthSelect').addEventListener('change', function() {
        const selectedMonth = this.value;
        loadDataForMonth(selectedMonth);
        updateMonthHeading(selectedMonth); // Update heading when month changes
    });

    loadMonthsAndData(); // Initialize the dropdown and load data
});
