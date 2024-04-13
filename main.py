import postings
import atlarge


def print_blue(text):
    print('\033[94m' + text + '\033[0m')


def print_red(text):
    print('\033[91m' + text + '\033[0m')


class TournamentData:
    def __init__(self, postings_obj):
        self.postings_obj = postings_obj
        self.team_hitlists = dict()
        self.is_bye = False
        self.bye_list = []
        self.print_color = True

    def enable_bye(self):
        self.is_bye = True

    def disable_bye(self):
        self.is_bye = False

    def create_new_team_hitlist(self, team):
        self.team_hitlists[team] = []

    def load_matchup(self, matchup):
        team1 = matchup[0]
        team2 = matchup[1]
        self.team_hitlists[team1].append(team2)
        self.team_hitlists[team2].append(team1)

    def load_bye(self, team):
        self.team_hitlists[team].append(None)
        self.bye_list.append(team)

    def print_team(self, team):
        print_func = print_blue if self.print_color else print_red
        self.print_color = not self.print_color
        team_hitlist = _tournament_data.team_hitlists[team]
        print_func('===' + str(team) + '===')
        for idx, t in enumerate(team_hitlist):
            print_func(str(idx + 1) + '. ' + str(t))
        print()

    def print_bye_list(self):
        print_func = print_blue if self.print_color else print_red
        self.print_color = not self.print_color
        for idx, t in enumerate(self.bye_list):
            print_func(str(idx + 1) + '. ' + str(t))
        print()

    def _parse_round_postings_into_bye_matchups(self, p: str):
        p = list(map(lambda s: s.strip(), p.strip().split('\n')))
        bye_team = None
        if self.is_bye:
            bye_team = p[1]
            p = p[2:]
        teams = []
        for i in range(self.postings_obj.rooms):
            #  [:-6] is to account for (Aff) / (Neg) after team listed on postings
            teams.append((p[i * 3 + 1][:-6], p[i * 3 + 2][:-6]))
        return bye_team, teams

    def _parse_round_postings_into_teams(self, p: str):
        p = p.strip().split('\n')
        teams = []
        if self.is_bye:
            teams.append(p[1])
            p = p[2:]
        for i in range(self.postings_obj.rooms):
            #  [:-6] is to account for (Aff) / (Neg) after team listed on postings
            teams.append(p[i * 3 + 1][:-6])
            teams.append(p[i * 3 + 2][:-6])
        return teams

    def load_round(self, round_num: int):
        round_var = 'round' + str(round_num)
        bye, matchups = self._parse_round_postings_into_bye_matchups(self.postings_obj.__getattribute__(round_var))
        self.load_bye(bye)
        for matchup in matchups:
            self.load_matchup(matchup)

    def create_all_teams(self):
        for team in self._parse_round_postings_into_teams(self.postings_obj.round1):
            self.create_new_team_hitlist(team)

    def load_all_finished_rounds(self):
        for i in range(self.postings_obj.finished_rounds):
            _round_num = i + 1
            self.load_round(_round_num)


class AtlargeData:
    def __init__(self, atlarge_obj):
        self.pre_qual_teams = set()
        self.team_rankings = dict()
        self.atlarge_obj = atlarge_obj
        self._parse_atlarge_data(atlarge_obj)

    def _parse_atlarge_data(self, atlarge_obj):
        for team in atlarge_obj.pre_quals.strip().split('\n'):
            self.pre_qual_teams.add(team.strip())
        for idx, team in enumerate(atlarge_obj.atlarge_rankings.strip().split('\n')):
            self.team_rankings[team.strip()] = idx


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
        return f'{s}-{nof_rounds-s}'


class Predictor:
    def __init__(self, tournament_data, atlarge_data):
        """
        tournament_data: a completed tournament data
        """
        self.tournament_data = tournament_data
        self.atlarge_data = atlarge_data
        self.team_records = {team: Record() for team in tournament_data.team_hitlists.keys()}

    def predict(self):
        # Notes:
        # Markers: 0=loss, 1=win

        # Not accounting corner cases yet
        # VERY MESSY: VERY TEMPORARY

        # Total num wins = total num losses
        # It's possible that nobody is completely_defeated i.e. 0-6
        # IMPORTANT: Assuming no cross-matching so far; just pure power matching

        #
        # =====First bye calculations=====
        round1bye_team = self.tournament_data.bye_list[0]

        # Team that hits round1.bye in round2 won round1
        hit_round1bye_team_in_round2 = self.tournament_data.team_hitlists[round1bye_team][1]
        self.team_records[round1bye_team].round1 = 1  # Bye round1
        self.team_records[hit_round1bye_team_in_round2].round1 = 1  # Won round1

        #
        # =====Second bye calculations=====
        round2bye_team = self.tournament_data.bye_list[1]
        self.team_records[round2bye_team].round1 = 0  # round2.bye lost round1

        # Team that hit round2.bye in round1 beat round2.bye
        hit_round2bye_team_in_round1 = self.tournament_data.team_hitlists[round2bye_team][0]
        self.team_records[hit_round2bye_team_in_round1].round1 = 1

        # Team that hit round2.bye in round2 also lost round1
        hit_round2bye_team_in_round2 = self.tournament_data.team_hitlists[round2bye_team][1]
        self.team_records[hit_round2bye_team_in_round2].round1 = 0
        # Team that hit team that hit round2.bye in round2 won round1
        hit_team_that_hit_round2bye_team_in_round2 = self.tournament_data.team_hitlists[hit_round2bye_team_in_round2][0]
        self.team_records[hit_team_that_hit_round2bye_team_in_round2].round1 = 1

        # Team that hit team that hit team that hit round2.bye in round2 also won round1
        hit_hit_team_that_hit_round2bye_team_in_round2 = self.tournament_data.team_hitlists[hit_round2bye_team_in_round2][0]
        self.team_records[hit_hit_team_that_hit_round2bye_team_in_round2].round1 = 1
        # Team that lost to the above team
        temp_team = self.tournament_data.team_hitlists[hit_hit_team_that_hit_round2bye_team_in_round2][0]
        self.team_records[temp_team].round1 = 0

        # Team that hit this team in round2 also lost round1

        #
        # =====Third bye calculations=====

        # Has worst record in tourney
        # Could be: 0-2, 1-1
        round3bye_team = self.tournament_data.bye_list[2]

        pass


if __name__ == '__main__':
    _tournament_data = TournamentData(postings)
    _tournament_data.enable_bye()
    _tournament_data.create_all_teams()
    _tournament_data.load_all_finished_rounds()

    _atlarge_data = AtlargeData(atlarge)
    _sorted_ranking = [(team, _atlarge_data.team_rankings[team]) for team in _atlarge_data.team_rankings.keys()]
    _sorted_ranking.sort(key=lambda pair: pair[1])
    for _i in _sorted_ranking:
        print(_i)
    print()

    for _team in _tournament_data.team_hitlists.keys():
        _tournament_data.print_team(_team)
    while True:
        inp = input('Team: >>>').strip()
        if inp == 'exit' or len(inp) == 0:
            print('Exiting...')
            break
        if inp == 'byes':
            _tournament_data.print_bye_list()
            continue
        try:
            _tournament_data.print_team(inp)
        except KeyError:
            print(f'Invalid team: "{inp}"')
