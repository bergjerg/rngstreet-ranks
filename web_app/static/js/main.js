// Function to format the join date to "Sep 2021"
function formatJoinDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short' };
    return date.toLocaleDateString('en-GB', options);
}

fetch(`/members?nocache=${new Date().getTime()}`)
    .then(response => response.json())
    .then(data => {
        const tableBody = document.querySelector('#membersTable tbody');
        const rankFilter = document.getElementById('rankFilter');
        const nextRankFilter = document.getElementById('nextRankFilter');
        const inGameRankFilter = document.getElementById('inGameRankFilter');
        const discordRankFilter = document.getElementById('discordRankFilter');
        const accountTypeFilter = document.getElementById('accountTypeFilter');

        const rankSet = new Set();
        const nextRankSet = new Set();
        const inGameRankSet = new Set();
        const discordRankSet = new Set();
        const accountTypeSet = new Set();

        // Populating dropdowns based on member data
        data.forEach(memberData => {
            rankSet.add(memberData.rank);
            nextRankSet.add(memberData.nextRank);
            inGameRankSet.add(memberData.inGameRank);
            discordRankSet.add(memberData.discordRank);
            accountTypeSet.add(memberData.accountType);
        });

        populateDropdown(rankFilter, Array.from(rankSet));
        populateDropdown(nextRankFilter, Array.from(nextRankSet));
        populateDropdown(inGameRankFilter, Array.from(inGameRankSet));
        populateDropdown(discordRankFilter, Array.from(discordRankSet));
        populateDropdown(accountTypeFilter, Array.from(accountTypeSet));

        // Organize members by their WOM_ID and group them by rank
        const memberMap = new Map();
        const parentToChildrenMap = new Map();
        const childToParentMap = new Map();
        const rankGroups = new Map(); // Group by rank

        data.forEach(memberData => {
            const mainWomId = memberData.mainWomId || 0;
        
            // Only group main accounts by rank
            if (mainWomId === 0) {
                if (!rankGroups.has(memberData.rank)) {
                    rankGroups.set(memberData.rank, []);
                }
                rankGroups.get(memberData.rank).push(memberData);
            }
        
            if (!memberMap.has(mainWomId)) {
                memberMap.set(mainWomId, []);
            }
            memberMap.get(mainWomId).push(memberData);
        
            if (mainWomId !== 0) {
                if (!parentToChildrenMap.has(mainWomId)) {
                    parentToChildrenMap.set(mainWomId, []);
                }
                parentToChildrenMap.get(mainWomId).push(memberData);
                childToParentMap.set(memberData.wom_id, mainWomId);
            }
        });

        // Sort rank groups by name or currentRankPoints (if applicable)
        const sortedRanks = Array.from(rankGroups.keys()).sort((a, b) => {
            const rankA = rankGroups.get(a)[0].currentRankPoints || 0;
            const rankB = rankGroups.get(b)[0].currentRankPoints || 0;
            return rankB - rankA;
        });

        // Create collapsible sections for each rank// Create collapsible sections for each rank
        sortedRanks.forEach(rank => {
            const rankGroup = rankGroups.get(rank);
            let currentRankPoints = rankGroup[0].currentRankPoints;    // Calculate the number of members with a different nextRank
            const nextRankCount = rankGroup.filter(member => member.nextRank && member.nextRank !== member.rank).length;
        

            if (currentRankPoints === null || currentRankPoints === undefined) {
                currentRankPoints = "Special Consideration";
            } else {
                currentRankPoints = currentRankPoints + " Points";
            }
            
            // Create rank header row
            const rankHeaderRow = document.createElement('tr');
            rankHeaderRow.classList.add('rank-header');

            // Add the toggle functionality to the entire row (not just the button)
            rankHeaderRow.addEventListener('click', () => toggleRankSection(rank, rankHeaderRow));

            // Only display the nextRank count column if nextRankCount > 0
            let nextRankColumn = '';
            if (nextRankCount > 0) {
                nextRankColumn = `<td colspan="1" style="color: #00ffcc;">${nextRankCount} Rank Ups</td>`;
            } else {
                nextRankColumn = `<td colspan="1"></td>`;
            }
            rankHeaderRow.innerHTML = `
                <td colspan="1"><span class="toggle-rank">+</span></td>
                <td colspan="1">
                    <img src="/static/images/ranks/${rank}.webp" loading="lazy" alt="" class="rank-image" style="width: 20px; height: 20px; vertical-align: middle;">
                    ${rank}
                </td>
                <td colspan="1">${currentRankPoints}</td>
                <td colspan="1">${rankGroup.length} Members</td>
                 ${nextRankColumn}
                <td colspan="6"></td>
            `;
        
        
            tableBody.appendChild(rankHeaderRow);
            
            // Generate rows for the members in this rank
            rankGroup.forEach(memberData => {
                const hasChildren = parentToChildrenMap.has(memberData.wom_id);
                const toggleButton = hasChildren ? `<button class="toggle-button" onclick="toggleChildren(${memberData.wom_id}, this)">+</button>` : '';
                const rsnCellContent = memberData.rsn !== memberData.name ? memberData.rsn : '';

                let actionsContent = `<button class="theme-button" onclick="editMember(${memberData.wom_id}, ${memberData.discordRank})">Edit</button>`;
                let rankUpContent = ``;
                if (memberData.nextRank && memberData.nextRank !== memberData.rank) {
                    //actionsContent += `<button class="theme-button" onclick="approveRankUp(${memberData.wom_id})">Approve Rank Up</button>`;
                    rankUpContent = `<button class="theme-button" onclick="approveRankUp(${memberData.wom_id})">${memberData.nextRank}</button>`;
                }
                let discordContent = ``;
                if (memberData.discordRank) {
                    // Add a class to customize the link style
                    discordContent = `<a href="discord://discordapp.com/users/${memberData.discordRank}" class="discord-link">${memberData.discordRank}</a>`;
                }                
                

                const row = document.createElement('tr');
                row.classList.add('parent-row');
                row.dataset.rank = rank;
                row.dataset.id = memberData.wom_id;
                row.style.display = 'none'; // Initially hidden

                
                row.innerHTML = `
                    <td class="name-column">
                        ${toggleButton}
                        ${memberData.name}
                    </td>
                    <td>${rsnCellContent}</td>
                    <td>${Math.floor(memberData.points)}</td>
                    <td>${memberData.rank}</td>
                    <td>${rankUpContent}</td>
                    <td>${memberData.inGameRank}</td>
                    <td>${discordContent}</td>
                    <td>${formatJoinDate(memberData.joinDate)}</td>
                    <td>${memberData.accountType}</td>
                    <td>${memberData.lastActive}</td>
                `;
                row.addEventListener('click', () => {
                    if (!event.target.closest('button') && !event.target.closest('a')) {
                        editMember(memberData.wom_id, memberData.discordRank)
                    }
                });
                    
                tableBody.appendChild(row);

                // Add rows for alternate accounts, initially hidden
                const altAccounts = parentToChildrenMap.get(memberData.wom_id) || [];
                altAccounts.forEach(altMemberData => {
                    const altRsnCellContent = altMemberData.rsn !== altMemberData.name ? altMemberData.rsn : '';


                    let altActionsContent = `<button class="theme-button" onclick="editMember(${altMemberData.wom_id}, ${altMemberData .discordRank})">Edit</button>`;
                    let rankUpContent = ``;
                    if (altMemberData.nextRank && altMemberData.nextRank !== altMemberData.rank) {
                        //actionsContent += `<button class="theme-button" onclick="approveRankUp(${memberData.wom_id})">Approve Rank Up</button>`;
                        rankUpContent = `<button class="theme-button" onclick="approveRankUp(${altMemberData.wom_id})">${altMemberData.nextRank}</button>`;
                    }

                    const altRow = document.createElement('tr');
                    altRow.classList.add('child-row');
                    altRow.dataset.parentId = memberData.wom_id;
                    altRow.dataset.id = altMemberData.wom_id;
                    altRow.style.display = 'none';
                    //Hide disocrd ID for alts
                    altRow.innerHTML = `
                        <td class="name-column">${altMemberData.name}</td>
                        <td>${altRsnCellContent}</td>
                        <td>${Math.floor(altMemberData.points)}</td>
                        <td>${altMemberData.rank}</td>
                        <td>${rankUpContent}</td>
                        <td>${altMemberData.inGameRank}</td>
                        <td></td> 
                        <td>${formatJoinDate(altMemberData.joinDate)}</td>
                        <td>${altMemberData.accountType}</td>
                        <td>${altMemberData.lastActive}</td>
                    `;
                    altRow.addEventListener('click', () => {
                        if (!event.target.closest('button') && !event.target.closest('a')) {
                            editMember(altMemberData.wom_id, altMemberData.discordRank)
                        }
                    });
                    tableBody.appendChild(altRow);
                });
            });
        });


        // Filter the table based on search input
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', applyFilters);

        // Filter dropdowns
        rankFilter.addEventListener('change', applyFilters);
        nextRankFilter.addEventListener('change', applyFilters);
        inGameRankFilter.addEventListener('change', applyFilters);
        discordRankFilter.addEventListener('change', applyFilters);
        accountTypeFilter.addEventListener('change', applyFilters);

        // Toggle Rank Ups
        const rankUpsToggle = document.getElementById('toggleRankUpsBtn');
        rankUpsToggle.addEventListener('change', applyFilters);

        // Toggle Rank Mismatches
        const rankMismatchesToggle = document.getElementById('toggleRankMismatchesBtn');
        rankMismatchesToggle.addEventListener('change', applyFilters);
        

        function applyFilters() {
            const searchValue = searchInput.value.toLowerCase();
            const rankValue = rankFilter.value;
            const nextRankValue = nextRankFilter.value;
            const inGameRankValue = inGameRankFilter.value;
            const discordRankValue = discordRankFilter.value;
            const accountTypeValue = accountTypeFilter.value;
            const isRankUpsOn = rankUpsToggle.checked;
            const isRankMismatchesOn = rankMismatchesToggle.checked;
            const rows = tableBody.querySelectorAll('tr');
            const rowsToShow = new Set();
            
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
        
                // Only filter member rows (skip rank headers)
                if (row.dataset.id && cells.length >= 9) {
                    const nameCell = cells[0].textContent.toLowerCase();
                    const rsnCell = cells[1].textContent.toLowerCase();
                    const rankCell = cells[3].textContent;
                    const nextRankCell = cells[4].textContent;
                    const inGameRankCell = cells[5].textContent;
                    const discordRankCell = cells[6].textContent;
                    const accountTypeCell = cells[8].textContent;
                    const rowId = row.dataset.id;
                    const parentId = row.dataset.parentId;
                    const rowRank = row.dataset.rank;
        
                    // Filter logic
                    const matchesSearch = nameCell.includes(searchValue) || rsnCell.includes(searchValue);
                    const matchesRank = rankValue === '' || rowRank === rankValue;
                    const matchesNextRank = nextRankValue === '' || nextRankCell === nextRankValue;
                    const matchesInGameRank = inGameRankValue === '' || inGameRankCell === inGameRankValue;
                    const matchesDiscordRank = discordRankValue === '' || discordRankCell === discordRankValue;
                    const matchesAccountType = accountTypeValue === '' || accountTypeCell === accountTypeValue;
        
                    // Toggle filters for rank ups and mismatches
                    const matchesRankUps = !isRankUpsOn || (nextRankCell);
                    const matchesRankMismatches = !isRankMismatchesOn || ((inGameRankCell) && inGameRankCell != "Not In Clan");
        
                    const shouldShowRow = matchesSearch && matchesRank && matchesNextRank && matchesInGameRank && matchesDiscordRank && matchesAccountType && matchesRankUps && matchesRankMismatches;
        
                    if (shouldShowRow) {
                        rowsToShow.add(rowId); // Show parent row if it matches
        
                        if (parentId) {
                            rowsToShow.add(parentId); // Ensure parent row is shown if a child matches
                        }
                    } else if (childToParentMap.has(rowId) && searchValue) {
                        rowsToShow.add(childToParentMap.get(rowId)); // Show parent if search matches child
                    }
                }
            });
        
            // Show or hide rows based on filtering
            rows.forEach(row => {
                const rowId = row.dataset.id;
                const parentId = row.dataset.parentId;
        
                // If it's a rank header, always display it
                if (row.classList.contains('rank-header')) {
                    row.style.display = ''; // Always show rank headers
                } else {
                    // For member rows, show if the row or its parent should be shown
                    if (rowsToShow.has(rowId) || (parentId && rowsToShow.has(parentId) && rowsToShow.has(rowId))) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                }
            });
        }
        
        
        
        
        
        
    });

function toggleRankSection(rank, headerRow) {
    const rows = document.querySelectorAll(`tr[data-rank="${rank}"]`);
    
    // Toggle the display of the rows associated with the rank
    rows.forEach(row => {
        const isVisible = row.style.display === 'none' ? '' : 'none';
        row.style.display = isVisible;

        // Check if there is an expanded section after the row and remove it if collapsing
        const expandedSection = row.nextElementSibling;
        if (isVisible === 'none' && expandedSection && expandedSection.classList.contains('expanded-section')) {
            expandedSection.remove();
        }

        // Collapse child rows (alt accounts) associated with this rank when collapsing the rank
        const childRows = document.querySelectorAll(`tr[data-parent-id="${row.dataset.id}"]`);
        childRows.forEach(child => {
            child.style.display = 'none';  // Collapse child row

            // Also remove expanded sections of child rows
            const childExpandedSection = child.nextElementSibling;
            if (childExpandedSection && childExpandedSection.classList.contains('expanded-section')) {
                childExpandedSection.remove();
            }
        });
    });

    // Toggle the + or − sign
    const toggleSymbol = headerRow.querySelector('.toggle-rank');
    toggleSymbol.textContent = toggleSymbol.textContent === '+' ? '−' : '+';
}
    



// Function to toggle the visibility of child rows
function toggleChildren(parentId) {
    const children = document.querySelectorAll(`tr[data-parent-id="${parentId}"]`);
    console.log(children);

    children.forEach(child => {
        const isVisible = child.style.display === 'none' ? '' : 'none';
        child.style.display = isVisible;

        // Check if there is an expanded section (edit section) after the child row and remove it if collapsing
        const expandedSection = child.nextElementSibling;
        if (isVisible === 'none' && expandedSection && expandedSection.classList.contains('expanded-section')) {
            expandedSection.remove();
        }
    });

    // Toggle the + or − sign for the child toggle button
    button.textContent = button.textContent === '+' ? '−' : '+';
}


function populateDropdown(dropdown, options) {
    options.sort().forEach(option => {
        const opt = document.createElement('option');
        opt.value = option;
        opt.text = option;
        dropdown.add(opt);
    });
}

function approveRankUp(wom_id) {
    fetch(`/approve_rank_up/${wom_id}`, {
        method: 'POST'
    })
    .then(response => {
        if (response.ok) {
            // Fetch updated data for the row
            refreshRow(wom_id);
        } else {
            alert('Failed to approve rank up');
        }
    })
    .catch(error => console.error('Error:', error));
}

// Function to toggle the highlight class
function toggleHighlight(element, shouldHighlight) {
    if (shouldHighlight) {
        element.classList.add('highlight');
    } else {
        element.classList.remove('highlight');
    }
}

// CSS class for highlighting
const style = document.createElement('style');
style.innerHTML = `
    .highlight {
        background-color: #555555; /* Slightly lighter grey background */
        color: #ffffff; /* White text for good contrast */
        font-weight: bold;
    }
`;
document.head.appendChild(style);
// Toggle Expand/Collapse for all ranks
const expandCollapseToggle = document.getElementById('toggleExpandCollapseBtn');
expandCollapseToggle.addEventListener('change', () => {
    const isExpanded = expandCollapseToggle.checked;
    
    // Toggle all rank sections (parent rows grouped by rank)
    document.querySelectorAll('.parent-row').forEach(parentRow => {
        const parentId = parentRow.dataset.id;
        
        // Toggle parent rows (main accounts)
        parentRow.style.display = isExpanded ? '' : 'none';
        
        // Get all child (alt) rows for this parent
        const altRows = document.querySelectorAll(`tr[data-parent-id="${parentId}"]`);
        
        // If collapsing, hide all alt accounts (child rows)
        if (!isExpanded) {
            altRows.forEach(altRow => {
                altRow.style.display = 'none';
            });
        }
    });
    
    // Update the toggle button for each rank header
    document.querySelectorAll('.toggle-rank').forEach(button => {
        button.textContent = isExpanded ? '−' : '+';
    });
});


let cachedRankConfig = null; // Cache the rank config data
let cachedUserList = []; // Cache the user list from the Name column

function editMember(wom_id, discordRank) {

    const memberRow = document.querySelector(`tr[data-id="${wom_id}"]`);
    if (!memberRow) {
        console.error(`Row with WOM_ID ${wom_id} not found`);
        return;
    }

    // Extract the user names from the Name column if not already cached
    if (cachedUserList.length === 0) {
        const rows = document.querySelectorAll('#membersTable tbody tr');
        rows.forEach(row => {
            const nameCell = row.querySelector('td:first-child');
            const userName = nameCell.textContent.trim().replace(/^(\\+|---)\\s*/, ''); // Remove prefixes
            const userWomId = row.getAttribute('data-id'); // Get WOM ID from the row

            if (userName && userWomId) {
                cachedUserList.push({ name: userName, wom_id: userWomId });
            }
        });
    }

    // Check if the section already exists to toggle visibility
    let expandedSection = memberRow.nextElementSibling;
    if (expandedSection && expandedSection.classList.contains('expanded-section')) {
        expandedSection.style.display = expandedSection.style.display === 'none' ? '' : 'none';
        return;
    }

    // Fetch the rank configuration if not already cached
    if (!cachedRankConfig) {
        fetch('/get_rank_config')
            .then(response => response.json())
            .then(rankConfig => {
                cachedRankConfig = rankConfig.sort((a, b) => a.ID - b.ID); // Sort by rank ID
                renderExpandedSection(wom_id, memberRow, discordRank);
            })
            .catch(error => {
                console.error('Error fetching rank config:', error);
                alert('Failed to fetch necessary data.');
            });
    } else {
        renderExpandedSection(wom_id, memberRow, discordRank);
    }
}


function renderExpandedSection(wom_id, memberRow, discordRank) {

    // Remove existing expanded section if any
    let expandedSection = memberRow.nextElementSibling;
    if (expandedSection && expandedSection.classList.contains('expanded-section')) {
        expandedSection.remove();
    }

    // Create and insert the expanded section
    expandedSection = document.createElement('tr');
    expandedSection.classList.add('expanded-section');
    
    expandedSection.innerHTML = `
        <td colspan="10">
            <div class="expanded-content" style="display: flex; justify-content: space-between;">
                <!-- Buttons on the left (vertical layout) -->
                <div class="buttons-container" style="flex: 1; display: flex; flex-direction: column; gap: 10px;margin-top: 40px">
                    <button class="theme-button" onclick="showForm('rank', ${wom_id})">Rank</button>
                    <button class="theme-button" onclick="showForm('name', ${wom_id})">Name</button>
                    <button class="theme-button" onclick="showForm('link', ${wom_id})">Link Account</button>
                    
                    ${discordRank ? `<button class="theme-button" onclick="showForm('unlink', ${wom_id})">Unlink Account</button>` : ''}

                    <button class="theme-button" onclick="showForm('rsn', ${wom_id})">Assign New RSN</button>
                    <button class="red-button" onclick="showForm('archive', ${wom_id})">Archive Member</button>
                </div>
                <div id="formContainer${wom_id}" style="width: 20%" class="form-container"></div>


                <!-- Points on the right -->
                <div id="pointsContainer${wom_id}" class="points-container" style="flex: 1 60%; margin-left: 20px;"></div>
            </div>
        </td>
    `;

    // Insert the expanded section directly after the current row
    memberRow.insertAdjacentElement('afterend', expandedSection);
    expandedSection.style.display = ''; // Ensure the section is displayed

    // Fetch and display member points directly (no button)
    fetchMemberPoints(wom_id);
}




function showForm(action, wom_id) {
    const formContainer = document.getElementById(`formContainer${wom_id}`);
    let formContent = '';

    switch (action) {
        case 'rsn':
            formContent = `
                <h4>Change this members RSN</h4>
                <input type="text" id="userSearch${wom_id}" placeholder="Search user by name" oninput="filterUserList('${action}', ${wom_id})">
                <div id="userList${wom_id}" class="user-list"></div>
                <select id="pointsOption${wom_id}">
                    <option value="merge">Merge Points</option>
                    <option value="keep">Keep only this user's points</option>
                </select>
                <button class="theme-button" id="submitBtn${wom_id}" onclick="submitForm('${action}', ${wom_id})" disabled>Submit</button>
            `;
            break;
        case 'link':
            formContent = `
                <h4>Link to another member</h4>
                <input type="text" id="userSearch${wom_id}" placeholder="Search user by name" oninput="filterUserList('${action}', ${wom_id})">
                <div id="userList${wom_id}" class="user-list"></div>
                <button class="theme-button" id="submitBtn${wom_id}" onclick="submitForm('${action}', ${wom_id})" disabled>Submit</button>
            `;
            break;
        case 'unlink':
            formContent = `
                <h4>Unlink Account</h4>
                <p>Are you sure you want to unlink this account?</p>
                <button class="red-button" onclick="submitForm('unlink', ${wom_id})">Unlink</button>
            `;
            break;
        case 'name':
            formContent = `
                <h4>Change Name</h4>
                <input type="text" id="newName${wom_id}" placeholder="Enter new name">
                <button class="theme-button" onclick="submitForm('name', ${wom_id})">Submit</button>
            `;
            break;
        case 'rank':
            formContent = `
                <h4>Change Rank</h4>
                <select id="newRank${wom_id}">
                    ${cachedRankConfig.map(rank => `<option value="${rank.NAME}">${rank.NAME}</option>`).join('')}
                </select>
                <button class="theme-button" onclick="submitForm('rank', ${wom_id})">Submit</button>
            `;
            break;
        case 'archive':
            formContent = `
                <h4>Archive Member</h4>
                <select id="archiveOption${wom_id}">
                    <option value="archive">Archive User's Points</option>
                    <option value="merge">Merge Points to Another User</option>
                </select>
                <div id="userSearchContainer${wom_id}" style="display:none;">
                    <input type="text" id="userSearch${wom_id}" placeholder="Search user by name" oninput="filterUserList('archive', ${wom_id})">
                    <div id="userList${wom_id}" class="user-list"></div>
                </div>
                <button class="red-button" id="submitBtn${wom_id}" onclick="submitForm('archive', ${wom_id})" disabled>Submit</button>
            `;
            break;
    }

    formContainer.innerHTML = formContent;
    console.log(`Form content rendered for ${action} action.`); // Debug log

    // Add event listener for the archive option to show/hide the user search input
    if (action === 'archive') {
        const archiveOption = document.getElementById(`archiveOption${wom_id}`);
        archiveOption.addEventListener('change', () => {
            const userSearchContainer = document.getElementById(`userSearchContainer${wom_id}`);
            if (archiveOption.value === 'merge') {
                userSearchContainer.style.display = '';
            } else {
                userSearchContainer.style.display = 'none';
            }
        });
    }
}
// Function to fetch and display member points data
function fetchMemberPoints(wom_id) {
    fetch(`/get_member_points/${wom_id}`)
        .then(response => response.json())
        .then(data => {
            // Create a table with an Edit button for each row
            const pointsTable = `
                <div class="scrollable-table-container">
                    <table class="points-table">
                        <thead>
                            <tr>
                                <th colspan=2></th>
                                <th>Skilling</th>
                                <th>Bossing</th>
                                <th>Splits</th>
                                <th>Events</th>
                                <th>Time</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.map(row => `
                                <tr id="row-${row.MONTH}">
                                    <td><strong>${formatMonth(row.MONTH)}</strong></td>
                                    <td><strong class="total-points">${row.TOTAL_POINTS}</strong></td>
                                    <td><strong style="color: #888;" class="xp-points">${row.XP_POINTS}</strong></td>
                                    <td><strong style="color: #888;" class="ehb-points">${row.EHB_POINTS}</strong></td>
                                    <td><strong style="color: #888;" class="split-points">${row.SPLIT_POINTS}</strong></td>
                                    <td><strong style="color: #888;" class="event-points">${row.EVENT_POINTS}</strong></td>
                                    <td><strong style="color: #888;" class="time-points">${row.TIME_POINTS}</strong></td>
                                    <td>
                                        <button class="edit-button" onclick="editRow(${wom_id}, ${row.MONTH})">Edit</button>
                                        <button class="apply-button" style="display:none;" onclick="applyChanges(${wom_id}, ${row.MONTH})">Apply</button>
                                        <button class="cancel-button" style="display:none;" onclick="cancelEdit(${wom_id})">Cancel</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
            document.getElementById(`pointsContainer${wom_id}`).innerHTML = pointsTable;
        })
        .catch(error => console.error('Error fetching member points:', error));
}


function formatMonth(month) {
    if (month === '0' || month === 0) {
        return "Old System";
    }
    const year = Math.floor(month / 100);
    const monthIndex = (month % 100) - 1;
    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return `${monthNames[monthIndex]}, ${year}`;
}

// Function to make row cells editable
function editRow(wom_id, month) {
    const row = document.getElementById(`row-${month}`);
    const xpPoints = row.querySelector('.xp-points');
    const ehbPoints = row.querySelector('.ehb-points');
    const splitPoints = row.querySelector('.split-points');
    const eventPoints = row.querySelector('.event-points');
    const timePoints = row.querySelector('.time-points');

    // Change cells to input fields for editing with specific width
    xpPoints.innerHTML = `<input type="text" value="${xpPoints.textContent}" disabled style="width: 40px;" />`;
    ehbPoints.innerHTML = `<input type="text" value="${ehbPoints.textContent}" disabled style="width: 40px;" />`;
    splitPoints.innerHTML = `<input type="text" value="${splitPoints.textContent}" style="width: 40px;" />`;
    eventPoints.innerHTML = `<input type="text" value="${eventPoints.textContent}" style="width: 40px;" />`;
    timePoints.innerHTML = `<input type="text" value="${timePoints.textContent}" style="width: 40px;" />`;

    // Toggle visibility of buttons
    row.querySelector('.edit-button').style.display = 'none';
    row.querySelector('.apply-button').style.display = 'inline';
    row.querySelector('.cancel-button').style.display = 'inline';
}


// Function to apply changes and update the row
function applyChanges(wom_id, month) {
    const row = document.getElementById(`row-${month}`);
    const splitPoints = row.querySelector('.split-points input').value;
    const eventPoints = row.querySelector('.event-points input').value;
    const timePoints = row.querySelector('.time-points input').value;

    // Send the updated points to the backend
    fetch(`/update_points/${wom_id}/${month}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            SPLIT_POINTS: splitPoints,
            EVENT_POINTS: eventPoints,
            TIME_POINTS: timePoints
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Refresh the points table after updating
            fetchMemberPoints(wom_id);
        } else {
            console.error('Failed to update points');
        }
    })
    .catch(error => console.error('Error updating points:', error));
}

// Function to cancel editing
function cancelEdit(wom_id) {
    fetchMemberPoints(wom_id);
}



function getFormTitle(action) {
    switch (action) {
        case 'rsn': return 'Assign New RSN';
        case 'main': return 'Assign Main Account';
        case 'link': return 'Link';
        default: return '';
    }
}

function filterUserList(action, wom_id) {
    const searchInput = document.getElementById(`userSearch${wom_id}`).value.toLowerCase();
    const userListContainer = document.getElementById(`userList${wom_id}`);
    const submitBtn = document.getElementById(`submitBtn${wom_id}`);  // Corrected the submit button reference

    const filteredUsers = cachedUserList.filter(user => user.name.toLowerCase().includes(searchInput));

    if (filteredUsers.length > 0) {
        userListContainer.innerHTML = filteredUsers.map(user => `
            <div class="user-item" onclick="selectUser('${action}', ${wom_id}, '${user.wom_id}')">${user.name}</div>
        `).join('');
    } else {
        userListContainer.innerHTML = '<div class="no-user">No users found</div>';
    }

    // Disable the submit button initially
    submitBtn.disabled = true;
}


function selectUser(action, wom_id, selectedWomId) {
    const searchInput = document.getElementById(`userSearch${wom_id}`);
    const submitBtn = document.getElementById(`submitBtn${wom_id}`);

    const selectedUser = cachedUserList.find(user => user.wom_id === selectedWomId);
    if (selectedUser) {
        searchInput.value = selectedUser.name;
        submitBtn.dataset.selectedWomId = selectedWomId; // Store the selected user's WOM ID
        submitBtn.disabled = false; // Enable the submit button when a valid user is selected

        // Optionally, clear the user list to remove the dropdown after selection
        const userListContainer = document.getElementById(`userList${wom_id}`);
        userListContainer.innerHTML = '';
    }
}

function submitForm(action, wom_id) {
    console.log(`Submit button clicked for action: ${action}, WOM_ID: ${wom_id}`); // Debug log

    let data = {};
    let endpoint = '';

    switch (action) {
        case 'rsn': {
            const submitBtn = document.getElementById(`submitBtn${wom_id}`);
            if (!submitBtn) {
                console.error('Submit button not found!');
                return; // Exit the function if the button is not found
            }

            const selectedWomId = submitBtn.dataset.selectedWomId;
            if (!selectedWomId) {
                console.error('Selected WOM ID not found on the submit button!');
                return; // Exit if the selected WOM ID is not set
            }

            const pointsOption = document.getElementById(`pointsOption${wom_id}`).value;

            data = {
                current_wom_id: wom_id,       // The WOM ID of the member being edited
                new_wom_id: selectedWomId,    // The WOM ID of the selected user
                points_option: pointsOption   // "Merge Points" or "Keep only this user's points"
            };
            endpoint = `/update_rsn/${wom_id}`;
            break;
        }
        case 'link': {
            const submitBtn = document.getElementById(`submitBtn${wom_id}`);
            const selectedWomId = parseInt(submitBtn.dataset.selectedWomId, 10);
            
            data = {
                main_wom_id: wom_id,       // The WOM ID of the member being edited
                alt_wom_id: selectedWomId     // The WOM ID of the selected user, now an integer
            };
            endpoint = `/link_account/${wom_id}`;            
            break;
        }
        case 'unlink': {
            data = { wom_id: wom_id }; 
            endpoint = `/unlink_account/${wom_id}`;
            break;
        }
        case 'name': {
            const newName = document.getElementById(`newName${wom_id}`).value;
            data = { name: newName };
            endpoint = `/update_name/${wom_id}`;
            break;
        }
        case 'rank': {
            const newRank = document.getElementById(`newRank${wom_id}`).value;
            data = { rank: newRank };
            endpoint = `/update_rank/${wom_id}`;
            break;
        }
        default:
            console.error('Unknown action:', action);
            return;
    }

    console.log('Data to be sent:', data); // Debug log
    console.log('Endpoint:', endpoint); // Debug log

    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log(response);
        if (response.ok) {
            console.log(`${action} updated successfully for WOM_ID ${wom_id}`);

            // For the 'link' action, refresh to the root directory
            if (action === 'link' || action == 'unlink') {
                window.location.href = '/';
            } else {
                // Fetch updated data for the row
                refreshRow(wom_id);
            }
        } else {
            // Handle non-2xx responses
            return response.json().then(errorData => {
                console.error(`Error updating ${action} for WOM_ID ${wom_id}:`, errorData);
                alert(`Error: ${errorData.error || 'Unknown error occurred'}`);
            });
        }
    })
    .catch(error => console.error('Error:', error));
}



function refreshRow(wom_id) {
    // Fetch the updated member data for the specific WOM ID
    fetch(`/get_member/${wom_id}`)
        .then(response => response.json())
        .then(updatedMember => {
            // Find the row in the table
            console.log(updatedMember);
            const memberRow = document.querySelector(`tr[data-id="${wom_id}"]`);
            if (memberRow) {
                memberRow.style.transition = 'background-color 0.5s ease';
                memberRow.style.backgroundColor = '#888'; // Darker grey color

                setTimeout(() => {
                    memberRow.style.backgroundColor = ''; // Fade back to default color
                }, 1500);
            }
            let actionsContent = `<button class="theme-button" onclick="editMember(${updatedMember.wom_id}, ${updatedMember.discordRank})">Edit</button>`;
            let rankUpContent = ``;
            if (updatedMember.nextRank && updatedMember.nextRank !== updatedMember.rank) {
                //actionsContent += `<button class="theme-button" onclick="approveRankUp(${memberData.wom_id})">Approve Rank Up</button>`;
                rankUpContent = `<button class="theme-button" onclick="approveRankUp(${updatedMember.wom_id})">${updatedMember.nextRank}</button>`;
            }
            let discordContent = ``;
            if (updatedMember.discordRank) {
                // Add a class to customize the link style
                discordContent = `<a href="discord://discordapp.com/users/${updatedMember.discordRank}" class="discord-link">${updatedMember.discordRank}</a>`;
            }       
            let rsn = ``;
            if (updatedMember.name != updatedMember.rsn) {
                rsn = updatedMember.rsn;
            }
            memberRow.classList.add('parent-row');
            if (memberRow) {
                // Update the row with the new data
                memberRow.innerHTML = `
                    <td>${updatedMember.name}</td>
                    <td>${rsn}</td>
                    <td>${updatedMember.points}</td>
                    <td>${updatedMember.rank}</td>
                    <td>${rankUpContent}</td>
                    <td>${updatedMember.inGameRank}</td>
                    <td>${discordContent}</td>
                    <td>${formatJoinDate(updatedMember.joinDate)}</td>
                    <td>${updatedMember.accountType}</td>
                    <td>${updatedMember.lastActive}</td>
                `;
                altRow.addEventListener('click', () => {
                    if (!event.target.closest('button') && !event.target.closest('a')) {
                        editMember(updatedMember.wom_id, updatedMember.discordRank)
                    }
                });
            }
        })
        .catch(error => console.error('Error fetching updated member data:', error));
}













function assignRSN(wom_id) {
    console.log(`Assign New RSN for WOM_ID: ${wom_id}`);
    // Additional logic to handle RSN assignment can be added here
}

function assignMain(wom_id) {
    console.log(`Assign Main Account for WOM_ID: ${wom_id}`);
    // Additional logic to handle Main Account assignment can be added here
}

function assignAlt(wom_id) {
    console.log(`Assign Alt Account for WOM_ID: ${wom_id}`);
    // Additional logic to handle Alt Account assignment can be added here
}

