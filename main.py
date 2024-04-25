import tournament_data
import atlarge_data


"""
Terminology:

Postings: The str postings of the given round 
Round: The round in the tournament
Matchup: A match between two teams hitting each other, i.e. (t1, t2)
Byeteam: The team that got the bye in the given round
"""


color_bool = False


def color_print(text):
    """
    Color print for displaying text.
    """
    global color_bool
    if color_bool:
        print('\033[91m' + text + '\033[0m')  # Red
    else:
        print('\033[94m' + text + '\033[0m')  # Blue
    color_bool = not color_bool


class TournamentDataHandler:
    def __init__(self, td):
        """
        td: The Tournament Data module.

        Handles teamids, matchups and the byelist.

        On __init__:
        setup_teams
        register_all_finished_rounds
        """
        self.td = td  # Tournament Data

        self.teamtoid = dict()  # { t1: id1, t2: id2, ... }
        self.idtoteam = dict()  # { id1: t1, id2: t2, ... }
        self.matchups = dict()  # { t1id: [t2id, t3id, ...], t2id: [t1id, None, ...], ... }
        self.byelist = []  # [t3id, t2id, ...]

        self.setup_teams()
        self.register_all_finished_rounds()

    def setup_teams(self):
        """
        Initialize empty lists in the matchups dict from postings of round1 & assign ids for all teams.

        Called in the __init__ method in TournamentData.
        """
        teamid = 0
        round1_postings = self.td.round1.strip().split('\n')
        if self.td.is_bye:
            team = round1_postings[1].strip()
            self.matchups[teamid] = list()
            self.teamtoid[team] = teamid; self.idtoteam[teamid] = team; teamid += 1
            round1_postings = round1_postings[2:]
        for i in range(self.td.rooms):
            #  [:-6] is to account for (Aff) / (Neg) after team listed on postings
            team1 = round1_postings[i * 3 + 1][:-6].strip()
            self.matchups[teamid] = list()
            self.teamtoid[team1] = teamid; self.idtoteam[teamid] = team1; teamid += 1

            team2 = round1_postings[i * 3 + 2][:-6].strip()
            self.matchups[teamid] = list()
            self.teamtoid[team2] = teamid; self.idtoteam[teamid] = team2; teamid += 1

    def register_matchup(self, matchup: tuple):
        """
        Register a given matchup in the format (t1id, t2id) to the tournament matchups.

        Appends each team to the other's list of matchups.
        """
        team1 = matchup[0]
        team2 = matchup[1]
        self.matchups[team1].append(team2)
        self.matchups[team2].append(team1)

    def register_bye(self, byeteamid: int):
        """
        Registers a given team to the tournament byelist.

        Appends the teamid to the end of the byelist.
        """
        self.byelist.append(byeteamid)
        self.matchups[byeteamid].append(None)

    def register_round(self, round_num: int):
        """
        Loads a given round from Tournament Data (td).

        Registers all matchups & the byeteam for the given round.
        """
        round_postings = list(map(lambda s: s.strip(), self.td.__getattribute__('round' + str(round_num)).strip().split('\n')))

        print('[')

        if self.td.is_bye:
            byeteam = round_postings[1].strip()

            print(f'"{byeteam}",')

            byeteamid = self.teamtoid[byeteam]
            round_postings = round_postings[2:]
            self.register_bye(byeteamid)

        for i in range(self.td.rooms):
            #  [:-6] is to account for (Aff) / (Neg) after team listed on postings
            team1 = round_postings[i * 3 + 1][:-6].strip()
            team1id = self.teamtoid[team1]

            team2 = round_postings[i * 3 + 2][:-6].strip()
            team2id = self.teamtoid[team2]

            matchup = (team1id, team2id)

            print(f'["{team1}", "{team2}"],')

            self.register_matchup(matchup)

        print('],')

    def register_all_finished_rounds(self):
        """
        Registers all finished rounds from Tournament Data (td).
        Called in the __init__ method in TournamentData.

        Number of finished rounds = `td.finished_rounds`

        See `TournamentDataHandler.register_round`.
        """
        for i in range(self.td.finished_rounds):
            round_num = i + 1
            self.register_round(round_num)


class AtlargeDataHandler:
    def __init__(self, ad):
        """
        ad: The Atlarge Data module

        Handles Atlarge Data (ad): prequals, rankings, sorted_rankings.
        """
        self.ad = ad
        self.prequals = set()
        self.rankings = dict()
        self.sorted_rankings = list()
        self.register_ad()

    def register_ad(self):
        """
        Registers all Atlarge Data (ad).

        Loads prequal teams & rankings from the ad module.
        """
        for team in self.ad.prequals.strip().split('\n'):
            team = team.strip()
            self.prequals.add(team)

        for idx, team in enumerate(self.ad.rankings.strip().split('\n')):
            team = team.strip()
            self.rankings[team] = idx

        self.sorted_rankings = [(team, self.rankings[team]) for team in self.rankings.keys()]
        self.sorted_rankings.sort(key=lambda pair: pair[1])


class Record:
    def __init__(self, teamid):
        """
        A team's record.
        0=loss, 1=win
        """
        self.teamid = teamid
        self.round = [None, None, None, None, None, None]  # 0-based

    def win_round(self, rd):
        """
        Sets round `rd` to a win.
        `rd`: 0-based debate round
        """
        self.round[rd] = 1

    def lose_round(self, rd):
        """
        Sets round `rd` to a loss.
        `rd`: 0-based debate round
        """
        self.round[rd] = 0

    def safe_win_round(self, rd):
        """
        Runs win_round only if the round is not already set and not conflicting.
        If round is already set and the round is marked as a loss (0), raises a conflict error.
        Returns true if win_round was run, otherwise False.
        rd: 0-based debate round
        """
        if self.round_set(rd):
            if not self.round_won(rd):
                raise Exception('Conflicting record:', str(self), rd)
            return False
        else:
            self.win_round(rd)
            return True

    def safe_lose_round(self, rd):
        """
        Runs lose_round only if the round is not already set and not conflicting.
        If round is already set and the round is marked as a win (1), raises a conflict error.
        Returns true if lose_round was run, otherwise False.
        rd: 0-based debate round
        """
        if self.round_set(rd):
            if self.round_won(rd):
                raise Exception('Conflicting record:', str(self), rd)
            return False
        else:
            self.lose_round(rd)
            return True

    def round_set(self, rd):
        """
        Returns False if round[rd] is None, True otherwise
        rd: 0-based debate round
        """
        return self.round[rd] is not None

    def round_won(self, rd):
        """
        Returns True if round==1 (won), False if round==0 (loss), else None
        rd: 0-based debate round
        """
        if self.round[rd] == 1:
            return True
        elif self.round[rd] == 0:
            return False
        else:
            return None

    def get_record(self):
        """
        Returns the record of the team in the tuple (won, lost).
        """
        nof_rounds = 6 - self.round.count(None)
        s = 0
        for r in self.round:
            if r is not None:
                s += r
        return s, nof_rounds - s

    def __str__(self):
        w, l = self.get_record()
        return f'({w}-{l})|{self.round}'


class Predictor:
    def __init__(self, tdh: TournamentDataHandler, adh: AtlargeDataHandler):
        """
        Predict records from Tournament Data (td) and Atlarge Data (ad).
        """
        self.tdh = tdh
        self.adh = adh
        self.teamidtorecord = {teamid: Record(teamid) for teamid in tdh.matchups.keys()}

    def predict_round(self):
        #  Assume: no_cross_pairing, is_bye, pure powermatching

        bye1teamid = self.tdh.byelist[0]  # bye1
        self.teamidtorecord[bye1teamid].win_round(0)

        bye2teamid = self.tdh.byelist[1]  # bye2
        self.teamidtorecord[bye2teamid].lose_round(0)
        self.teamidtorecord[bye2teamid].win_round(1)

        bye3teamid = self.tdh.byelist[2]  # bye3
        # Assume no wonky stuff: bye3.record post-rd2 = 0-2
        self.teamidtorecord[bye3teamid].lose_round(0)
        self.teamidtorecord[bye3teamid].lose_round(1)
        self.teamidtorecord[bye3teamid].win_round(2)

        # Run flood calculation
        team_q = [bye1teamid, bye2teamid, bye3teamid]
        while len(team_q) > 0:
            cur_teamid = team_q.pop(0)
            cur_record = self.teamidtorecord[cur_teamid]
            cur_matchups = self.tdh.matchups[cur_teamid]

            for rd in range(6):
                round_won = cur_record.round_won(rd)
                if round_won is None:  # Not predicted yet
                    continue

                hit_teamid = cur_matchups[rd]
                if hit_teamid is not None:  # Not bye
                    hit_record = self.teamidtorecord[hit_teamid]
                    if not round_won:
                        if hit_record.safe_win_round(rd):  # Update hit_team.r to win round
                            team_q.append(hit_teamid)  # Add to queue
                    elif round_won:
                        if hit_record.safe_lose_round(rd):  # Update hit_team.r to lose round
                            team_q.append(hit_teamid)  # Add to queue

                # Round-specific calculations
                if rd == 0:
                    nexthit_teamid = cur_matchups[1]
                    if nexthit_teamid is not None:  # Not bye
                        nexthit_record = self.teamidtorecord[nexthit_teamid]
                        if not round_won:
                            if nexthit_record.safe_lose_round(0):
                                team_q.append(nexthit_teamid)
                        elif round_won:
                            if nexthit_record.safe_win_round(0):
                                team_q.append(nexthit_teamid)
                elif rd == 1:
                    pass

                # Round3bye: 0-2:  hit_rd1.r.postrd1 = 1-0 (beat cur),  hit_rd1.r.postrd2 = 1-1 (beat cur)

        for teamid in self.teamidtorecord.keys():
            color_print(str(self.tdh.idtoteam[teamid].ljust(35)) + ' ' + str(teamid).ljust(2) + ' ' + str(self.teamidtorecord[teamid]))


if __name__ == '__main__':
    _tdh = TournamentDataHandler(tournament_data)
    _adh = AtlargeDataHandler(atlarge_data)

    predictor = Predictor(_tdh, _adh)
    predictor.predict_round()

    def print_al_sorted_rankings():
        print('===AL Sorted Rankings:===')
        for _i in _adh.sorted_rankings:
            print(_i)
        print('===End of AL Sorted Rankings===')
    # print_al_sorted_rankings()

    def print_team(teamid, is_id=True):
        if not is_id:
            teamid = _tdh.teamtoid[teamid]

        matchup = _tdh.matchups[teamid]
        t = '===' + _tdh.idtoteam[teamid] + '===\n'
        for idx, i in enumerate(matchup):
            if matchup[idx] is None:
                t += f'{idx+1}. None\n'
            else:
                t += f'{idx + 1}. {matchup[idx]} : {_tdh.idtoteam[matchup[idx]]}\n'
        color_print(t)

    def print_all_teams():
        for _team in _tdh.matchups.keys():
            print_team(_team)
    # print_all_teams()

    def start_console():
        while True:
            inp = input('Team: >>>').strip()
            if inp == 'exit' or len(inp) == 0:
                print('Exiting...')
                break
            if inp == 'byes':
                _t = '===Byes===\n'
                for _idx, _i in enumerate(_tdh.byelist):
                    _t += f'{_idx+1}. {_tdh.byelist[_idx]} : {_tdh.idtoteam[_tdh.byelist[_idx]]} \n'
                color_print(_t)
                continue
            try:
                if inp.startswith('team'):
                    _teamid = int(inp.split(' ')[1])
                    color_print(f'{_teamid}: "{_tdh.idtoteam[_teamid]}"\n')
                    continue
                if inp.startswith('id'):
                    _teamarg = inp.split(' ', maxsplit=1)[1].strip()
                    color_print(f'"{_teamarg}": {_tdh.teamtoid[_teamarg]}\n')
                    continue
                else:
                    print_team(inp, is_id=False)
            except KeyError:
                print(f'Invalid: "{inp}"')
    start_console()
