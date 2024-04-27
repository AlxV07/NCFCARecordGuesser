import {is_bye, tournament_data, rooms} from './tournament_data.js'

class TournamentDataHandler {
    constructor() {
        this.cellidcount = 0
        this.idtocell = {}
        this.cellDefaultColor = {}

        this.teamCellIds = {}
        this.partnerCellId = {}
    }

    registerCell(cell) {
        const id = this.getNextCellId()
        this.idtocell[id] = cell
        this.cellDefaultColor[id] = 'white'
        return id
    }

    getNextCellId() {
        let t = this.cellidcount
        this.cellidcount += 1
        return t
    }

    appendTeamCellId(team, cellId) {
        if (this.teamCellIds[team] === undefined) {
            this.teamCellIds[team] = []
        }
        this.teamCellIds[team].push(cellId)
    }

    setPartnerCells(cell1, cell2) {
        this.partnerCellId[cell1] = cell2
        this.partnerCellId[cell2] = cell1
    }

    getCell(id) {
        return this.idtocell[id]
    }

    setCellBgToDefault(id) {
        this.idtocell[id].style.backgroundColor = this.cellDefaultColor[id]
    }
}
const tdh = new TournamentDataHandler()


function loadTournamentDataIntoTable() {
    const tableBody = document.querySelector('#myTable tbody');

    if (is_bye) {
        const byeRow = document.createElement('tr')
        tournament_data.forEach(round_data => {
            const byeCell = document.createElement('td'); byeCell.classList.add('byeCell')
            const cellId = tdh.registerCell(byeCell)
            const team = round_data[0].trim()

            byeCell.textContent = team
            tdh.appendTeamCellId(team, cellId)
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
            tdh.appendTeamCellId(t1, t1cellId)
            matchupRow.appendChild(t1cell);

            const t2cell = document.createElement('td'); t2cell.classList.add('teamCell')
            const t2cellId = tdh.registerCell(t2cell)
            const t2 = matchup[1].trim()
            t2cell.textContent = t2;
            tdh.appendTeamCellId(t2, t2cellId)
            matchupRow.appendChild(t2cell);

            tdh.setPartnerCells(t1cellId, t2cellId)

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
            tdh.getCell(teamCellId).style.borderColor = 'black'
            tdh.getCell(teamCellId).style.borderLeftWidth = '2px'
        }
    }
}

function selectedWin() {
    const won = 'rgba(25,155,11,0.62)';
    const lost = 'rgba(185,0,0,0.76)'

    tdh.cellDefaultColor[selectedCellId] = won
    tdh.getCell(selectedCellId).style.backgroundColor = won

    const partnerCellId = tdh.partnerCellId[selectedCellId]
    const partnerCell = tdh.getCell(tdh.partnerCellId[selectedCellId])
    if (partnerCell !== undefined) {
        tdh.cellDefaultColor[partnerCellId] = lost
        tdh.getCell(partnerCellId).style.backgroundColor = lost
    }
}

function selectedLose() {
    const won = 'rgba(25,155,11,0.62)'
    const lost = 'rgba(185,0,0,0.76)'

    tdh.cellDefaultColor[selectedCellId] = lost
    tdh.getCell(selectedCellId).style.backgroundColor = lost

    const partnerCellId = tdh.partnerCellId[selectedCellId]
    const partnerCell = tdh.getCell(tdh.partnerCellId[selectedCellId])
    if (partnerCell !== undefined) {
        tdh.cellDefaultColor[partnerCellId] = won
        tdh.getCell(partnerCellId).style.backgroundColor = won
    }
}

function selectedClear() {
    tdh.cellDefaultColor[selectedCellId] = 'white'
    tdh.getCell(selectedCellId).style.backgroundColor = 'white'

    const partnerCellId = tdh.partnerCellId[selectedCellId]
    const partnerCell = tdh.getCell(tdh.partnerCellId[selectedCellId])
    if (partnerCell !== undefined) {
        tdh.cellDefaultColor[partnerCellId] = 'white'
        tdh.getCell(partnerCellId).style.backgroundColor = 'white'
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
                cell.style.borderColor = 'yellow'
            })
        }
    }

    document.addEventListener('keydown', (event) => {
        if (event.key === 'w') {
            selectedWin()
        }
        if (event.key === 'l') {
            selectedLose()
        }
        if (event.key === 'c') {
            selectedClear()
        }

        if (event.key === 'Escape') {
            selectedCellId = null
            setSelectedTeam(null)
        }
    })
}
addListeners()
