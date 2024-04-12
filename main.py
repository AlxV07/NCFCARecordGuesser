import postings as p

def print_blue(text):
    """Print text in blue color."""
    COLOR_BLUE = '\033[94m'
    COLOR_RESET = '\033[0m'  # Reset to default color
    print(COLOR_BLUE + text + COLOR_RESET)

def print_red(text):
    """Print text in red color."""
    COLOR_RED = '\033[91m'
    COLOR_RESET = '\033[0m'  # Reset to default color
    print(COLOR_RED + text + COLOR_RESET)


class TournamentData:
    def __init__(self):
        self.team_hitlists = dict()
        self.bye_list = []
        self.print_color = True

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

def parse_round_postings_into_bye_matchups(rooms: int, postings: str, is_bye: bool):
    postings = list(map(lambda s: s.strip(), postings.strip().split('\n')))
    bye_team = None
    if is_bye:
        bye_team = postings[1]
        postings = postings[2:]
    teams = []
    for i in range(rooms):
        #  [:-6] is to account for (Aff) / (Neg) after team listed on postings
        teams.append((postings[i * 3 + 1][:-6], postings[i * 3 + 2][:-6]))
    return bye_team, teams

def parse_round_postings_into_teams(rooms: int, postings: str, is_bye: bool):
    postings = postings.strip().split('\n')
    teams = []
    if is_bye:
        teams.append(postings[1])
        postings = postings[2:]
    for i in range(rooms):
        #  [:-6] is to account for (Aff) / (Neg) after team listed on postings
        teams.append(postings[i * 3 + 1][:-6])
        teams.append(postings[i * 3 + 2][:-6])
    return teams


if __name__ == '__main__':
    tournament_data = TournamentData()
    for team in parse_round_postings_into_teams(p.rooms, p.round1, True):
        tournament_data.create_new_team_hitlist(team)

    _is_bye = True

    for i in range(p.finished_rounds):
        round = 'round' + str(i + 1)
        bye, matchups = parse_round_postings_into_bye_matchups(p.rooms, p.__getattribute__(round), _is_bye)
        tournament_data.load_bye(bye)
        for matchup in matchups:
            tournament_data.load_matchup(matchup)

    for team in tournament_data.team_hitlists.keys():
        tournament_data.print_team(team)

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
        except:
            print(f'Invalid team: "{inp}"')
