import {RawTournamentData, parse_raw_tournament_data} from './tournament_data.js'

const Colors = {
    WON_MATCH : 'rgba(25,155,11,0.38)',
    LOST_MATCH : 'rgba(185,0,0,0.47)',
    CLEAR_MATCH : 'rgba(255,255,255,0.47)',
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
        this.marks = {
            // [t1, t2] 0=unset, 1=t1won, 2=t1loss
            0: {},
            1: {},
            2: {},
            3: {},
            4: {},
            5: {},
        }

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

    generateMarks() {
        this.marks = {}
        for (let round = 0; round < 6; round++) {
            this.marks[round] = {}
            this.marks[round]['BYE']  = 0
            for (let roomid = 0; roomid < this.rooms; roomid++) {
                this.marks[round][roomid] = 0
            }
        }
    }

    generateTableCells() {
        const tableBody = document.querySelector('#mainTable tbody');

        // Build bye cells
        const byeRow = document.createElement('tr')
        for (let round = 0; round < 6; round++) {
            const byeCell = document.createElement('td'); byeCell.classList.add('byeCell')
            byeCell.cellid = '7' + round
            this.cells[round]['BYE']  = byeCell
            byeRow.appendChild(byeCell)
        }
        tableBody.appendChild(byeRow)

        // Build room cells
        for (let roomid = 0; roomid < this.rooms; roomid++) {
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

    updateFromRaw() {
        const teamtoid_idtoteam_rounds_rooms = parse_raw_tournament_data()
        this.teamtoid = teamtoid_idtoteam_rounds_rooms[0]
        this.idtoteam = teamtoid_idtoteam_rounds_rooms[1]
        this.rounds = teamtoid_idtoteam_rounds_rooms[2]
        this.rooms = teamtoid_idtoteam_rounds_rooms[3]
        this.regenerateTableCells()
    }

    regenerateTableCells() {
        this.removeAllTableCells()
        this.generateTableCells()

        this.teamCells = {}

        for (let round = 0; round < 6; round++) {
            if (this.rounds[round] === null) {
                break
            }
            const bye_team = this.rounds[round]['BYE']
            let bye_cell = this.cells[round]['BYE'];
            bye_cell.textContent = this.idtoteam[bye_team]
            this.addTeamCell(bye_team, bye_cell)

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

    setMark(id, mark) {
        if (id === null) {
            return;
        }
        const s = id.toString().substring(1);
        if (s.length === 1) { // Bye
            return
        }
        const round = parseInt(s.substring(0, 1))
        const room = parseInt(s.substring(1, s.length - 1))
        const t = parseInt(s.substring(s.length - 1))
        this.marks[round][room] = (mark === 0) ? 0 : (t === 0 ? (mark === 1 ? 1 : 2) : (mark === 1 ? 2 : 1))
    }

    paintCells() {
        for (let round = 0; round < 6; round++) {
            for (let roomid = 0; roomid < this.rooms; roomid++) {
                const mark = this.marks[round][roomid]
                const c1_c2 = this.cells[round][roomid]
                const c1 = c1_c2[0]
                const c2 = c1_c2[1]
                let c1color = null
                let c2color = null
                if (mark === 0) {
                    c1color = Colors.CLEAR_MATCH
                    c2color = Colors.CLEAR_MATCH
                } else if (mark === 1) {
                    c1color = Colors.WON_MATCH
                    c2color = Colors.LOST_MATCH
                } else if (mark === 2) {
                    c1color = Colors.LOST_MATCH
                    c2color = Colors.WON_MATCH
                } else {
                    throw new Error(`Invalid Mark: ${mark}`)
                }
                c1.style.backgroundColor = c1color
                c2.style.backgroundColor = c2color
            }
        }
    }

    selectedWonMatch() {
        this.setMark(this.selectedCellId, 1)
        this.paintCells()
    }

    selectedLostMatch() {
        this.setMark(this.selectedCellId, 2)
        this.paintCells()
    }

    selectedClearMatch() {
        this.setMark(this.selectedCellId, 0)
        this.paintCells()
    }

    setSelectedTeamNull() {
        this.selectedCellId = null
        this.setSelectedTeam(null)
    }

    login() {
        // Sets dbh.sb; creates client with given Url and Key
        try {
            const p = prompt('Login Url.Key:')
            if (p === null) {
                alert('Cancelled Login.')
                return false;
            }
            const url_key = p.trim().split('|')
            const url = 'https://' + url_key[0].trim() + '.supabase.co'
            const key = url_key[1].trim()
            dbh.setSB(url, key)
            return true;
        } catch (e) {
            alert(e)
            return false;
        }
    }

    async override() {
        // Overrides table data with current data.
        const confirm = prompt('Type "override" to confirm.')
        if (confirm !== 'override') {
            alert('Canceled Override.')
            return;
        }
        if (!this.login()) {
            return
        }
        document.getElementById('saveLog').textContent = `Overriding...`; console.log(`Overriding...`)

        const d1 = JSON.stringify([this.marks, this.idtoteam])
        const d2 = JSON.stringify([this.rounds, this.rooms])
        await dbh.updateDatabase(d1, 'marks_idtoteam')
        await dbh.updateDatabase(d2, 'rounds_rooms')

        const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
        document.getElementById('saveLog').textContent = `Overridden (${time}).`; console.log(`Overridden (${time}).`)
        document.getElementById('saveButton').disabled = ''
        document.getElementById('overrideButton').disabled = 'disabled'
        document.getElementById('loadButton').disabled = 'disabled'
    }

    async loadProgress() {
        if (!this.login()) {
            return
        }
        const saveLog = document.getElementById('saveLog')
        saveLog.textContent = 'Loading...'; console.log('Loading...')
        try {
            const d1 = JSON.parse(await dbh.readDatabase('marks_idtoteam'))
            const d2 = JSON.parse(await dbh.readDatabase('rounds_rooms'))
            this.marks = d1[0]
            this.idtoteam = d1[1]
            this.rounds = d2[0]
            this.rooms = d2[1]
            this.regenerateTableCells()
            this.paintCells()
        } catch (e) {
            alert(e)
        }
        const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
        saveLog.textContent = `Loaded (${time}). Hi Mommy!`; console.log(`Loaded (${time}).`)

        document.getElementById('saveButton').disabled = ''
        document.getElementById('overrideButton').disabled = 'disabled'
        document.getElementById('loadButton').disabled = 'disabled'
    }

    async saveProgress() {
        if (dbh.sb === null) {
            if (!this.login()) {
                return
            }
        }
        const saveLog = document.getElementById('saveLog')
        saveLog.textContent = 'Saving...'; console.log('Saving...')

        const d1 = JSON.stringify([this.marks, this.idtoteam])
        const d2 = JSON.stringify([this.rounds, this.rooms])
        await dbh.updateDatabase(d1, 'marks_idtoteam')
        await dbh.updateDatabase(d2, 'rounds_rooms')

        const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
        saveLog.textContent = `Saved (${time}).`; console.log(`Saved (${time}).`)
    }
}

class DatabaseHandler {
    constructor() {
        this.sb = null

        this.tableName = 'main_table'
    }

    setSB(url, key) {
        this.sb = supabase.createClient(url, key);
    }

    async readDatabase(columnName) {
        try {
            const { data, error } = await this.sb
                .from(this.tableName)
                .select(columnName)
                .single();
            return data ? data[columnName] : null;
        } catch (error) {
            console.error('Error reading from database:', error.message);
            throw error;
        }
    }

    async updateDatabase(value, column) {
        try {
            const { data: updatedRow, updateError } = await this.sb
                .from(this.tableName)
                .update({ [column]: value })
                .eq('id', 1)
        } catch (error) {
            console.error('Error setting string in first row:', error.message);
            throw error;
        }
    }
}

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
        if (event.key === 'k') {
            document.getElementById('overrideButton').click()
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
    document.getElementById('settingsButton').onclick = () => {help()}
    document.getElementById('helpButton').onclick = () => {help()}
    document.getElementById('saveButton').onclick = () => {tdh.saveProgress()}
    document.getElementById('loadButton').onclick = () => {tdh.loadProgress()}
    document.getElementById('overrideButton').onclick = () => {tdh.override()}

    document.getElementById('wonButton').onclick = () => {tdh.selectedWonMatch()}
    document.getElementById('lostButton').onclick = () => {tdh.selectedLostMatch()}
    document.getElementById('clearButton').onclick = () => {tdh.selectedClearMatch()}

    window.addEventListener('beforeunload', () => {document.getElementById('saveButton').click()})
}

let tdh;
let dbh;
function main() {
    tdh = new TournamentDataHandler()
    dbh = new DatabaseHandler()
    tdh.updateFromRaw()
    tdh.generateMarks()
    tdh.paintCells()
    addListeners()
}

main()

// TODO: Raw Postings Input Page, Arrow Key Cell Nav, Auto Saving Setting
// Possible Additions: In-App Multi-Table Switching, Improved Server Functionality
