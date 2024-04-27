import {rooms, is_bye, tournament_data} from './tournament_data.js'

class TournamentDataHandler {
    constructor() {
        this.idtocell = {}
        this.cellidcounter = 0

        this.teamCellIds = {}
        this.matchingCellId = {}
    }

    registerCell(cell) {
        const id = this.getNextCellId()
        this.idtocell[id] = cell
        cell.cellid = id
        return id
    }

    getNextCellId() {
        let t = this.cellidcounter
        this.cellidcounter += 1
        return t
    }

    addTeamCellId(team, cellId) {
        if (this.teamCellIds[team] === undefined) {
            this.teamCellIds[team] = []
        }
        this.teamCellIds[team].push(cellId)
    }

    setMatchingCells(cell1, cell2) {
        this.matchingCellId[cell1] = cell2
        this.matchingCellId[cell2] = cell1
    }

    getCell(id) {
        return this.idtocell[id]
    }
}
const tdh = new TournamentDataHandler()

class ColorsClass {
    constructor() {
        this.WON_MATCH = 'rgba(25,155,11,0.38)';
        this.LOST_MATCH = 'rgba(185,0,0,0.47)'
        this.CLEAR_MATCH = 'white'

        this.SELECTED_CELL = 'orange'
        this.SELECTED_TEAM_CELL = 'blue'
    }
}
const Colors = new ColorsClass()

function loadTournamentDataIntoTable() {
    const tableBody = document.querySelector('#mainTable tbody');

    if (is_bye) {
        const byeRow = document.createElement('tr')
        tournament_data.forEach(round_data => {
            const byeCell = document.createElement('td'); byeCell.classList.add('byeCell')
            const cellId = tdh.registerCell(byeCell)
            const team = round_data[0].trim()

            byeCell.textContent = team
            tdh.addTeamCellId(team, cellId)
            byeRow.appendChild(byeCell)
        })
        tableBody.appendChild(byeRow)
    }

    for (let i = 0; i < rooms; i++) {
        const room_row = document.createElement('tr')
        tournament_data.forEach(round_data => {
            const matchup = round_data[i + 1]
            const matchupCell = document.createElement('td');
            matchupCell.classList.add('matchupCell')

            const matchupTable = document.createElement('table');
            const matchupRow = document.createElement('tr');

            const t1cell = document.createElement('td'); t1cell.classList.add('teamCell')
            const t1cellId = tdh.registerCell(t1cell);
            const t1 = matchup[0].trim()
            t1cell.textContent = t1;
            tdh.addTeamCellId(t1, t1cellId)
            matchupRow.appendChild(t1cell);

            const t2cell = document.createElement('td'); t2cell.classList.add('teamCell')
            const t2cellId = tdh.registerCell(t2cell)
            const t2 = matchup[1].trim()
            t2cell.textContent = t2;
            tdh.addTeamCellId(t2, t2cellId)
            matchupRow.appendChild(t2cell);

            tdh.setMatchingCells(t1cellId, t2cellId)

            matchupTable.appendChild(matchupRow);
            matchupCell.appendChild(matchupTable);
            room_row.appendChild(matchupCell);

        });
        tableBody.appendChild(room_row);
    }
}

loadTournamentDataIntoTable();

let selectedCellId = null
let selectedTeam = null

function setSelectedTeam(team) {
    const teamCellIds = tdh.teamCellIds;
    if (selectedTeam !== null) {
        for (const teamCellId of teamCellIds[selectedTeam]) {
            tdh.getCell(teamCellId).style.borderColor = ''
            tdh.getCell(teamCellId).style.borderLeftWidth = ''
        }
    }

    selectedTeam = team
    if (team !== null) {
        for (const teamCellId of teamCellIds[team]) {
            tdh.getCell(teamCellId).style.borderColor = Colors.SELECTED_TEAM_CELL
            tdh.getCell(teamCellId).style.borderLeftWidth = '3px'
        }
    }
}

function selectedWonMatch() {
    tdh.getCell(selectedCellId).style.backgroundColor = Colors.WON_MATCH
    const matchingCell = tdh.getCell(tdh.matchingCellId[selectedCellId])
    if (matchingCell !== undefined) {
        matchingCell.style.backgroundColor = Colors.LOST_MATCH
    }
}

function selectedLostMatch() {
    tdh.getCell(selectedCellId).style.backgroundColor = Colors.LOST_MATCH
    const matchingCell = tdh.getCell(tdh.matchingCellId[selectedCellId])
    if (matchingCell !== undefined) {
        matchingCell.style.backgroundColor = Colors.WON_MATCH
    }
}

function selectedClearMatch() {
    tdh.getCell(selectedCellId).style.backgroundColor = Colors.CLEAR_MATCH
    const matchingCell = tdh.getCell(tdh.matchingCellId[selectedCellId])
    if (matchingCell !== undefined) {
        matchingCell.style.backgroundColor = Colors.CLEAR_MATCH
    }
}

function addListeners() {
    const teamCellIds = tdh.teamCellIds;
    for (const team in teamCellIds) {
        for (const cellId of teamCellIds[team]) {
            const cell = tdh.getCell(cellId)
            cell.addEventListener('click', () => {
                selectedCellId = cellId
                setSelectedTeam(team)
                cell.style.borderColor = Colors.SELECTED_CELL
            })
        }
    }

    document.addEventListener('keydown', (event) => {
        if (event.key === 'w') {
            selectedWonMatch()
        }
        if (event.key === 'q') {
            selectedLostMatch()
        }
        if (event.key === 'c') {
            selectedClearMatch()
        }

        if (event.key === 'Escape') {
            selectedCellId = null
            setSelectedTeam(null)
        }
    })
}
addListeners()
