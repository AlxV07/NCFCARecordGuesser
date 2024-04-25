import {is_bye, tournament_data, rooms} from './tournament_data.js'

function generateTableRows() {
    const tableBody = document.querySelector('#myTable tbody');

    if (is_bye) {
        const bye_row = document.createElement('tr')
        tournament_data.forEach(round_data => {
            const bye_cell = document.createElement('td')
            bye_cell.textContent = round_data[0]
            bye_row.appendChild(bye_cell)
        })
        tableBody.appendChild(bye_row)
    }

    for (let i = 0; i < rooms; i++) {
        const room_row = document.createElement('tr')
        tournament_data.forEach(round_data => {
            const matchup = round_data[i + 1]
            const matchupContainerCell = document.createElement('td');
            matchupContainerCell.classList.add('matchup_cell')

            const matchupTable = document.createElement('table');
            const matchupRow = document.createElement('tr');

            const t1cell = document.createElement('td');
            t1cell.classList.add('team_cell')
            t1cell.textContent = matchup[0];
            matchupRow.appendChild(t1cell);

            const t2cell = document.createElement('td');
            t2cell.classList.add('team_cell')
            t2cell.textContent = matchup[1];
            matchupRow.appendChild(t2cell);

            matchupTable.appendChild(matchupRow);

            matchupContainerCell.appendChild(matchupTable);

            room_row.appendChild(matchupContainerCell);

        });
        tableBody.appendChild(room_row);
    }
}

generateTableRows();
