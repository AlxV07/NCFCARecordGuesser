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
        team_hitlist = tournament_data.team_hitlists[team]
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

    def _parse_round_postings_into_bye_matchups(self, postings: str):
        postings = list(map(lambda s: s.strip(), postings.strip().split('\n')))
        bye_team = None
        if self.is_bye:
            bye_team = postings[1]
            postings = postings[2:]
        teams = []
        for i in range(self.postings_obj.rooms):
            #  [:-6] is to account for (Aff) / (Neg) after team listed on postings
            teams.append((postings[i * 3 + 1][:-6], postings[i * 3 + 2][:-6]))
        return bye_team, teams

    def _parse_round_postings_into_teams(self, postings: str):
        postings = postings.strip().split('\n')
        teams = []
        if self.is_bye:
            teams.append(postings[1])
            postings = postings[2:]
        for i in range(self.postings_obj.rooms):
            #  [:-6] is to account for (Aff) / (Neg) after team listed on postings
            teams.append(postings[i * 3 + 1][:-6])
            teams.append(postings[i * 3 + 2][:-6])
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


class Predictor:
    def __init__(self, tournament_data):
        pass


if __name__ == '__main__':
    tournament_data = TournamentData(postings)
    tournament_data.enable_bye()
    tournament_data.create_all_teams()
    tournament_data.load_all_finished_rounds()

    atlarge_data = AtlargeData(atlarge)
    sorted_ranking = [(team, atlarge_data.team_rankings[team]) for team in atlarge_data.team_rankings.keys()]
    sorted_ranking.sort(key=lambda pair: pair[1])
    for i in sorted_ranking:
        print(i)
    print()

    for _team in tournament_data.team_hitlists.keys():
        tournament_data.print_team(_team)
    while True:
        inp = input('Team: >>>').strip()
        if inp == 'exit' or len(inp) == 0:
            print('Exiting...')
            break
        if inp == 'byes':
            tournament_data.print_bye_list()
            continue
        try:
            tournament_data.print_team(inp)
        except KeyError:
            print(f'Invalid team: "{inp}"')
