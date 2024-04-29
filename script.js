import {RawTournamentData, parse_raw_tournament_data} from './tournament_data.js'

const Colors = {
    WON_MATCH : 'rgba(25,155,11,0.38)',
    LOST_MATCH : 'rgba(185,0,0,0.47)',
    CLEAR_MATCH : 'white',
    SELECTED_CELL : 'orange',
    SELECTED_TEAM_CELL : 'blue',
}

class TournamentDataHandler {
    constructor() {
        this.cells = {
            0: {},
            1: {},
            2: {},
            3: {},
            4: {},
            5: {},
        }
        this.marks = {}

        this.teamCells = {}
        this.matchingCellId = {}

        this.teamtoid = {}
        this.idtoteam = {}
        this.rounds = {}
        this.rooms = {}

        this.selectedCellId = null
        this.selectedTeamId = null
    }

    getCell(id) {
        // id format: 7x...y
        // x: round 0-based {0, 1, 2, 3, 4, 5}
        // ...: roomid 1-2 digits
        // y: {0, 1}  t1 or t2
        // ... + y === '', x = round x bye cell
        let s = id.toString().substring(1);
        if (s.length === 1) {
            return this.rounds[parseInt(id)]['BYE']
        }
        const round = parseInt(s.substring(0, 1))
        const room = parseInt(s.substring(1, s.length - 1))
        const t = parseInt(s.substring(s.length - 1))
        return this.cells[round][room][t]
    }

    getMatchingCell(id) {
        let s = id.toString().substring(1);
        const round = parseInt(s.substring(0, 1))
        const room = parseInt(s.substring(1, s.length - 1))
        const t = parseInt(s.substring(s.length - 1)) === 0 ? 1 : 0
        return this.cells[round][room][t]
    }

    removeAllTableCells() {
        const tableBody = document.querySelector('#mainTable tbody');
        while (tableBody.firstChild) {
            tableBody.removeChild(tableBody.firstChild)
        }
    }

    generateTableCells(rooms) {
        const tableBody = document.querySelector('#mainTable tbody');

        // Build bye cells
        const byeRow = document.createElement('tr')
        for (let round = 0; round < 6; round++) {
            const byeCell = document.createElement('td'); byeCell.classList.add('byeCell')
            byeCell.cellid = '7' + round
            this.cells[round]['BYE']  = byeCell
            byeRow.appendChild(byeCell)
        }

        // Build room cells
        for (let roomid = 0; roomid < rooms; roomid++) {
            const roomRow = document.createElement('tr')

            for (let round = 0; round < 6; round++) {
                const roomCell = document.createElement('td');
                const roomTable = document.createElement('table');
                const roomInnerRow = document.createElement('tr');

                const t1cell = document.createElement('td'); t1cell.classList.add('teamCell')
                t1cell.cellid = parseInt('7' + round.toString() + roomid.toString() + '0')
                const t2cell = document.createElement('td'); t2cell.classList.add('teamCell')
                t2cell.cellid = parseInt('7' + round.toString() + roomid.toString() + '1')
                roomInnerRow.appendChild(t1cell);
                roomInnerRow.appendChild(t2cell);

                this.cells[round][roomid] = [t1cell, t2cell]

                roomTable.appendChild(roomInnerRow);
                roomCell.appendChild(roomTable);
                roomRow.appendChild(roomCell);
            }
            tableBody.appendChild(roomRow);
        }
    }

    update() {
        const teamtoid_idtoteam_rounds_rooms = parse_raw_tournament_data()
        this.teamtoid = teamtoid_idtoteam_rounds_rooms[0]
        this.idtoteam = teamtoid_idtoteam_rounds_rooms[1]
        this.rounds = teamtoid_idtoteam_rounds_rooms[2]
        this.rooms = teamtoid_idtoteam_rounds_rooms[3]
        this.updateTableCells()
    }

    updateTableCells() {
        this.removeAllTableCells()
        this.generateTableCells(this.rooms)

        this.teamCells = {}

        for (let round = 0; round < 6; round++) {
            if (this.rounds[round] === null) {
                break
            }
            for (let roomid = 0; roomid < this.rooms; roomid++) {
                const t1_t2 = this.rounds[round][roomid]
                const c1_c2 = this.cells[round][roomid]
                c1_c2[0].textContent = this.idtoteam[t1_t2[0]]
                this.addTeamCell(t1_t2[0], c1_c2[0])
                c1_c2[1].textContent = this.idtoteam[t1_t2[1]]
                this.addTeamCell(t1_t2[1], c1_c2[1])
            }
        }
        for (const team in this.teamCells) {
            for (const cell of this.teamCells[team]) {
                cell.addEventListener('click', () => {
                    this.selectedCellId = cell.cellid
                    this.setSelectedTeam(team)
                    cell.style.borderColor = Colors.SELECTED_CELL
                })
            }
        }
    }

    addTeamCell(team, cell) {
        if (this.teamCells[team] === undefined) {
            this.teamCells[team] = []
        }
        this.teamCells[team].push(cell)
    }

    setSelectedTeam(team) {
        if (this.selectedTeamId !== null) {
            for (const teamCell of this.teamCells[this.selectedTeamId]) {
                teamCell.style.borderColor = ''; teamCell.style.borderLeftWidth = ''
            }
        }
        this.selectedTeamId = team
        if (team !== null) {
            for (const teamCell of this.teamCells[team]) {
                teamCell.style.borderColor = Colors.SELECTED_TEAM_CELL
                teamCell.style.borderLeftWidth = '3px'
            }
        }
        document.getElementById('selectedTeam').textContent = this.selectedTeamId !== null ? this.idtoteam[this.selectedTeamId] : 'null'
    }

    selectedWonMatch() {
        if (this.selectedCellId === null) {return}
        this.getCell(this.selectedCellId).style.backgroundColor = Colors.WON_MATCH
        const matchingCell = this.getMatchingCell(this.selectedCellId)
        if (matchingCell !== undefined) {
            matchingCell.style.backgroundColor = Colors.LOST_MATCH
        }
    }

    selectedLostMatch() {
        if (this.selectedCellId === null) {return}
        this.getCell(this.selectedCellId).style.backgroundColor = Colors.LOST_MATCH
        const matchingCell = this.getMatchingCell(this.selectedCellId)
        if (matchingCell !== undefined) {
            matchingCell.style.backgroundColor = Colors.WON_MATCH
        }
    }

    selectedClearMatch() {
        if (this.selectedCellId === null) {return}
        this.getCell(this.selectedCellId).style.backgroundColor = Colors.CLEAR_MATCH
        const matchingCell = this.getMatchingCell(this.selectedCellId)
        if (matchingCell !== undefined) {
            matchingCell.style.backgroundColor = Colors.CLEAR_MATCH
        }
    }

    setSelectedTeamNull() {
        this.selectedCellId = null
        this.setSelectedTeam(null)
    }
}
const tdh = new TournamentDataHandler()
tdh.update()

function help() {
    alert('<3')
}

function addListeners() {
    document.addEventListener('keydown', (event) => {
        if (event.key === 'p') {
            document.getElementById('settingsButton').click()
        }
        if (event.key === 'h') {
            document.getElementById('helpButton').click()
        }
        if (event.key === 'o') {
            document.getElementById('saveButton').click()
        }
        if (event.key === 'l') {
            document.getElementById('loadButton').click()
        }


        if (event.key === 'w') {
            document.getElementById('wonButton').click()
        }
        if (event.key === 'q') {
            document.getElementById('lostButton').click()
        }
        if (event.key === 'c') {
            document.getElementById('clearButton').click()
        }

        if (event.key === 'Escape') {
            tdh.setSelectedTeamNull()
        }

        // Navigate Cells
        if (event.key === 'ArrowUp') {
        }
        if (event.key === 'ArrowDown') {
        }
        if (event.key === 'ArrowLeft') {
        }
        if (event.key === 'ArrowRight') {
        }
    })
    document.getElementById('settingsButton').onclick = null
    document.getElementById('helpButton').onclick = help
    document.getElementById('saveButton').onclick = null
    document.getElementById('loadButton').onclick = null

    document.getElementById('wonButton').onclick = () => {tdh.selectedWonMatch()}
    document.getElementById('lostButton').onclick = () => {tdh.selectedLostMatch()}
    document.getElementById('clearButton').onclick = () => {tdh.selectedClearMatch()}
}
addListeners()


// TODO: Cell navigation, settings page, load postings, progress saving online
