import pandas as pd
import numpy as np
import json
import math


class NpEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle NumPy and standard Python types that are
    not serializable by default, such as infinity and NaN.
    """

    def default(self, obj):
        # Handle all numpy integer types
        if isinstance(obj, np.integer):
            return int(obj)
        # Handle all numpy float types
        if isinstance(obj, np.floating):
            # Use np.isnan and np.isinf for numpy types
            if np.isnan(obj) or np.isinf(obj):
                return None
            return float(obj)
        # Handle standard python float types (for the float('inf') cases)
        if isinstance(obj, float):
            # Use math.isnan and math.isinf for python types
            if math.isnan(obj) or math.isinf(obj):
                return None
            return obj
        # Handle numpy arrays
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        # Let the base class default method raise the TypeError
        return super(NpEncoder, self).default(obj)


#Data Loading and Preprocessing

matches_df = pd.read_csv('ipl_matches.csv')
balls_df = pd.read_csv('ipl_ball.csv')
ball_with_match_df = pd.merge(balls_df, matches_df, on='ID', how='inner')
ball_with_match_df['BowlingTeam'] = ball_with_match_df.apply(
    lambda row: row['Team2'] if row['BattingTeam'] == row['Team1'] else row['Team1'],
    axis=1
)
ALL_TEAMS = set(matches_df['Team1'].unique()) | set(matches_df['Team2'].unique())


#Team Level Functions

def get_team_record(team, matches_data):
    team_matches = matches_data[(matches_data['Team1'] == team) | (matches_data['Team2'] == team)]
    matches_played = len(team_matches)
    won = len(team_matches[team_matches['WinningTeam'] == team])
    no_result = len(team_matches[team_matches['WinningTeam'].isnull()])
    lost = matches_played - won - no_result
    titles_won = len(team_matches[(team_matches['MatchNumber'] == 'Final') & (team_matches['WinningTeam'] == team)])
    return {'matches_played': matches_played, 'won': won, 'lost': lost, 'no_result': no_result,
            'titles_won': titles_won}


def teamVteamAPI(team1, team2):
    if team1 not in ALL_TEAMS or team2 not in ALL_TEAMS:
        return {'message': 'Invalid team name provided.'}
    head_to_head_matches = matches_df[((matches_df['Team1'] == team1) & (matches_df['Team2'] == team2)) | (
                (matches_df['Team1'] == team2) & (matches_df['Team2'] == team1))]
    total_matches = len(head_to_head_matches)
    win_counts = head_to_head_matches['WinningTeam'].value_counts()
    team1_wins = win_counts.get(team1, 0)
    team2_wins = win_counts.get(team2, 0)
    no_result = total_matches - (team1_wins + team2_wins)

    return {
        'total_matches': int(total_matches),
        f'{team1}_wins': int(team1_wins),
        f'{team2}_wins': int(team2_wins),
        'no_result': int(no_result)
    }


def teamAPI(team):
    if team not in ALL_TEAMS:
        return json.dumps({'message': f"Team '{team}' not found."})
    overall_record = get_team_record(team, matches_df)
    opponents = sorted(list(ALL_TEAMS - {team}))
    against_records = {opponent: teamVteamAPI(team, opponent) for opponent in opponents}
    data = {team: {'overall_record': overall_record, 'head_to_head': against_records}}
    return json.dumps(data, cls=NpEncoder)


#Batsman Level Functions

def batsmanRecord(batsman, df):
    batsman_df = df[df['batter'] == batsman]
    if batsman_df.empty:
        return {}
    innings = batsman_df['ID'].nunique()
    runs = batsman_df['batsman_run'].sum()
    balls_faced = batsman_df[~batsman_df['extra_type'].isin(['wides'])].shape[0]
    outs = df[df['player_out'] == batsman].shape[0]
    strike_rate = (runs / balls_faced * 100) if balls_faced > 0 else 0
    average = (runs / outs) if outs > 0 else float('inf')
    fours = batsman_df[(batsman_df['batsman_run'] == 4) & (batsman_df['non_boundary'] == 0)].shape[0]
    sixes = batsman_df[(batsman_df['batsman_run'] == 6) & (batsman_df['non_boundary'] == 0)].shape[0]
    runs_per_match = batsman_df.groupby('ID')['batsman_run'].sum()
    fifties = runs_per_match[(runs_per_match >= 50) & (runs_per_match < 100)].shape[0]
    hundreds = runs_per_match[runs_per_match >= 100].shape[0]
    highest_score = runs_per_match.max() if not runs_per_match.empty else 0
    not_out = innings - outs
    mom = df[df['Player_of_Match'] == batsman].drop_duplicates('ID').shape[0]
    return {'innings': innings, 'runs': runs, 'average': average, 'strike_rate': strike_rate,
            'balls_faced': balls_faced, 'fours': fours, 'sixes': sixes, 'fifties': fifties, 'hundreds': hundreds,
            'highest_score': highest_score, 'not_outs': not_out, 'man_of_match': mom, 'dismissals': outs}


def batsmanVsTeam(batsman, team, df):
    opponent_df = df[df['BowlingTeam'] == team]
    return batsmanRecord(batsman, opponent_df)


def batsmanAPI(batsman):
    main_innings_df = ball_with_match_df[ball_with_match_df['innings'].isin([1, 2])]
    if batsman not in main_innings_df['batter'].unique():
        return json.dumps({'message': f"Batsman '{batsman}' not found in records."})
    overall_record = batsmanRecord(batsman, main_innings_df)
    opponents = sorted(list(ALL_TEAMS))
    against_records = {team: batsmanVsTeam(batsman, team, main_innings_df) for team in opponents}
    data = {batsman: {'overall': overall_record, 'against': against_records}}
    return json.dumps(data, cls=NpEncoder, indent=4)


#Bowler Level Functions

def bowlerRecord(bowler, df):
    bowler_df = df[df['bowler'] == bowler].copy()
    if bowler_df.empty:
        return {}
    bowler_df['bowler_run'] = bowler_df.apply(
        lambda row: 0 if row['extra_type'] in ['byes', 'legbyes', 'penalty'] else row['total_run'], axis=1)
    wicket_types = ['caught', 'caught and bowled', 'bowled', 'stumped', 'lbw', 'hit wicket']
    bowler_df['is_bowler_wicket'] = bowler_df.apply(
        lambda row: 1 if row['kind'] in wicket_types and row['isWicketDelivery'] == 1 else 0, axis=1)
    innings = bowler_df['ID'].nunique()
    runs_conceded = bowler_df['bowler_run'].sum()
    wickets = bowler_df['is_bowler_wicket'].sum()
    balls_bowled = bowler_df[~bowler_df['extra_type'].isin(['wides', 'noballs'])].shape[0]
    economy = (runs_conceded / balls_bowled * 6) if balls_bowled > 0 else 0
    average = (runs_conceded / wickets) if wickets > 0 else float('inf')
    strike_rate = (balls_bowled / wickets) if wickets > 0 else float('inf')
    fours = bowler_df[(bowler_df['batsman_run'] == 4) & (bowler_df['non_boundary'] == 0)].shape[0]
    sixes = bowler_df[(bowler_df['batsman_run'] == 6) & (bowler_df['non_boundary'] == 0)].shape[0]
    wickets_per_match = bowler_df.groupby('ID').agg({'is_bowler_wicket': 'sum', 'bowler_run': 'sum'})
    three_wickets_haul = wickets_per_match[wickets_per_match['is_bowler_wicket'] >= 3].shape[0]
    best_figures_sorted = wickets_per_match.sort_values(by=['is_bowler_wicket', 'bowler_run'], ascending=[False, True])
    best_figure = "0/0"
    if not best_figures_sorted.empty:
        best = best_figures_sorted.iloc[0]
        best_figure = f"{int(best['is_bowler_wicket'])}/{int(best['bowler_run'])}"
    mom = df[df['Player_of_Match'] == bowler].drop_duplicates('ID').shape[0]
    return {'innings': innings, 'wickets': wickets, 'runs_conceded': runs_conceded, 'economy': economy,
            'average': average, 'strike_rate': strike_rate, 'balls_bowled': balls_bowled, 'fours_conceded': fours,
            'sixes_conceded': sixes, 'three_wickets_plus': three_wickets_haul, 'best_figure': best_figure,
            'man_of_match': mom}


def bowlerVsTeam(bowler, team, df):
    opponent_df = df[df['BattingTeam'] == team]
    return bowlerRecord(bowler, df)


def bowlerAPI(bowler):
    main_innings_df = ball_with_match_df[ball_with_match_df['innings'].isin([1, 2])]
    if bowler not in main_innings_df['bowler'].unique():
        return json.dumps({'message': f"Bowler '{bowler}' not found in records."})
    overall_record = bowlerRecord(bowler, main_innings_df)
    opponents = sorted(list(ALL_TEAMS))
    against_records = {team: bowlerVsTeam(bowler, team, main_innings_df) for team in opponents}
    data = {bowler: {'overall': overall_record, 'against': against_records}}
    return json.dumps(data, cls=NpEncoder, indent=4)
