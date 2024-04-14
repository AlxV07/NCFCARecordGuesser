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

        if self.td.is_bye:
            byeteam = round_postings[1].strip()
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
            self.register_matchup(matchup)

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
    def __init__(self):
        # 0=loss, 1=win
        self.round1 = None
        self.round2 = None
        self.round3 = None
        self.round4 = None
        self.round5 = None
        self.round6 = None

    def get_record(self):
        nof_rounds = 1
        s = self.round1
        if self.round2 is not None:
            s += self.round2
            nof_rounds += 1
        if self.round3 is not None:
            s += self.round3
            nof_rounds += 1
        if self.round4 is not None:
            s += self.round4
            nof_rounds += 1
        if self.round5 is not None:
            s += self.round5
            nof_rounds += 1
        if self.round6 is not None:
            s += self.round6
            nof_rounds += 1
        return s, nof_rounds - s

    def __str__(self):
        nof_rounds = 1
        s = self.round1
        if self.round2 is not None:
            s += self.round2
            nof_rounds += 1
        if self.round3 is not None:
            s += self.round3
            nof_rounds += 1
        if self.round4 is not None:
            s += self.round4
            nof_rounds += 1
        if self.round5 is not None:
            s += self.round5
            nof_rounds += 1
        if self.round6 is not None:
            s += self.round6
            nof_rounds += 1
        return f'{s}-{nof_rounds - s}'


class Predictor:
    def __init__(self, td, ad):
        """
        Predict records from Tournament Data (td) and Atlarge Data (ad)
        """
        self.td = td
        self.al_d = ad
        self.team_records = {team: Record() for team in td.matchups.keys()}

    def predict(self):
        # Notes:
        # Markers: 0=loss, 1=win

        # Observations:
        # Each round & in total num wins = total num losses

        # Corner Cases:
        # It's possible that nobody is completely_defeated i.e. 0-6
        # Cross-matching so far

        #
        # =====First bye calculations=====
        rd1bye = self.td.byelist[0]
        self.team_records[rd1bye].round1 = 1

        # Team that hits rd1bye in rd2 won rd1
        hit_rd1bye_in_rd2 = self.td.matchups[rd1bye][1]
        self.team_records[hit_rd1bye_in_rd2].round1 = 1
        matching_lost_team = self.td.matchups[hit_rd1bye_in_rd2][0]
        self.team_records[matching_lost_team].round1 = 0

        """
        This becomes a flooding problem.
        
        Problem:
        Given a team which one one, keep spreading losses / wins you can decipher 
        based off connecting teams from byeteam
        """

        #
        # =====Second bye calculations=====
        round2bye_team = self.td.byelist[1]
        self.team_records[round2bye_team].round1 = 0  # round2.bye lost round1

        # Team that hit round2.bye in round1 beat round2.bye
        hit_round2bye_team_in_round1 = self.td.matchups[round2bye_team][0]
        self.team_records[hit_round2bye_team_in_round1].round1 = 1

        # Team that hit round2.bye in round2 also lost round1
        hit_round2bye_team_in_round2 = self.td.matchups[round2bye_team][1]
        self.team_records[hit_round2bye_team_in_round2].round1 = 0
        # Team that hit team that hit round2.bye in round2 won round1
        hit_team_that_hit_round2bye_team_in_round2 = self.td.matchups[hit_round2bye_team_in_round2][0]
        self.team_records[hit_team_that_hit_round2bye_team_in_round2].round1 = 1

        # Team that hit team that hit team that hit round2.bye in round2 also won round1
        hit_hit_team_that_hit_round2bye_team_in_round2 = self.td.matchups[hit_round2bye_team_in_round2][0]
        self.team_records[hit_hit_team_that_hit_round2bye_team_in_round2].round1 = 1
        # Team that lost to the above team
        temp_team = self.td.matchups[hit_hit_team_that_hit_round2bye_team_in_round2][0]
        self.team_records[temp_team].round1 = 0

        # Team that hit this team in round2 also lost round1

        #
        # =====Third bye calculations=====

        # Has worst record in tourney
        # Could be: 0-2, 1-1
        round3bye_team = self.td.byelist[2]

        pass


if __name__ == '__main__':
    tdh = TournamentDataHandler(tournament_data)
    adh = AtlargeDataHandler(atlarge_data)

    print('===AL Sorted Rankings:===')
    for _i in adh.sorted_rankings:
        print(_i)
    print('===End of AL Sorted Rankings===')

    def print_team(teamid, is_id=True):
        if not is_id:
            teamid = tdh.teamtoid[teamid]

        matchup = tdh.matchups[teamid]
        t = '===' + tdh.idtoteam[teamid] + '===\n'
        for idx, i in enumerate(matchup):
            if matchup[idx] is None:
                t += f'{idx+1}. {matchup[idx]}\n'
            else:
                t += f'{idx + 1}. {tdh.idtoteam[matchup[idx]]}\n'
        color_print(t)

    for _team in tdh.matchups.keys():
        print_team(_team)

    while True:
        inp = input('Team: >>>').strip()
        if inp == 'exit' or len(inp) == 0:
            print('Exiting...')
            break
        if inp == 'byes':
            _t = '===Byes===\n'
            for _idx, _i in enumerate(tdh.byelist):
                _t += f'{_idx+1}. {tdh.byelist[_idx]}\n'
            color_print(_t)
            continue
        try:
            print_team(inp, is_id=False)
        except KeyError:
            print(f'Invalid team: "{inp}"')
