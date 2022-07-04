import argparse
import numbers
from pathlib import Path

import pandas as pd

import utils
from enums import Arg, LogCol, StatsCol

pd.set_option('display.max_rows', 100000)
DEFAULT_LOGS_DIR = Path.cwd() / 'game_logs'


# def parse_args():
#     arg_parser = argparse.ArgumentParser()
#     arg_parser.add_argument(
#         '-d',
#         '--logs-dir',
#         default=str(DEFAULT_LOGS_DIR),
#         dest=Arg.LOGS_DIR.value
#     )
#     arg_parser.add_argument(
#         '-o',
#         '--output-file',
#         default=str(Path.cwd() / 'season_stats.csv'),
#         dest=Arg.OUTPUT.value
#     )
#     return arg_parser.parse_args()


def split_match_log_by_map(lines: [str]) -> []:
    # Each line has been split into a list of comma-sep values, hence the second [0]
    map = lines[0][0]
    map_start_idx = 2  # First 2 lines are map, players
    lines_iter = iter(range(map_start_idx, len(lines)))
    map_logs = []
    for line_num in lines_iter:
        if lines[line_num][0] == map:
            map_logs.append(lines[map_start_idx:line_num])
            map_start_idx = next(lines_iter, None) + 1  # Skip next line (players) as well

    # end of last map
    map_logs.append(lines[map_start_idx:len(lines)])

    return map_logs


def get_map_logs(lines: [str]) -> [pd.DataFrame]:
    map_logs = split_match_log_by_map(lines)
    df_logs = []
    for log in map_logs:
        df = pd.DataFrame(data=log, columns=[col.value for col in LogCol])

        # TODO Getting ValueError b/c some float values are showing up as '****' in the log files.
        # Can replace with a generic function that does this check for all numeric columns.
        df = df.drop(df[df[LogCol.DMG].str.contains('\*')].index)
        df = df.drop(df[df[LogCol.DMG_BLOCKED].str.contains('\*')].index)
        df = df.drop(df[df[LogCol.SECONDS].str.contains('\*')].index)
        df = df.drop(df[df[LogCol.HEALING].str.contains('\*')].index)

        df = utils.update_log_col_types(df)
        df_logs.append(df)

    return df_logs


def load_match_log(log_path: Path) -> [pd.DataFrame]:
    # UTF-8 cuz GrigmaMale is a ho, respectfully
    with open(log_path, 'r', encoding='utf8') as log_file:
        lines = log_file.readlines()
    lines = utils.format_lines(lines)

    return get_map_logs(lines)


def get_map_logs_per_player(df: pd.DataFrame) -> {pd.DataFrame}:
    players = df[LogCol.PLAYER].drop_duplicates()
    player_logs = {}
    for player in players:
        player_logs[player] = df[df[LogCol.PLAYER] == player].reset_index(drop=True)

    return player_logs


def calculate_stat_diff(hero_start_row, hero_swap_row):
    stats_diff = {
        StatsCol.TIME: hero_swap_row[LogCol.SECONDS] - hero_start_row[LogCol.SECONDS],
        StatsCol.ELIMS: hero_swap_row[LogCol.ELIMS] - hero_start_row[LogCol.ELIMS],
        StatsCol.FB: hero_swap_row[LogCol.FB] - hero_start_row[LogCol.FB],
        StatsCol.DMG: hero_swap_row[LogCol.DMG] - hero_start_row[LogCol.DMG],
        StatsCol.DEATHS: hero_swap_row[LogCol.DEATHS] - hero_start_row[LogCol.DEATHS],
        StatsCol.HEALING: hero_swap_row[LogCol.HEALING] - hero_start_row[LogCol.HEALING],
        StatsCol.DMG_BLOCKED: hero_swap_row[LogCol.DMG_BLOCKED] - hero_start_row[LogCol.DMG_BLOCKED],
    }

    return stats_diff


def update_player_stats(player_stats, stats_diff, curr_hero) -> None:
    if curr_hero in player_stats:
        hero_stats = player_stats[curr_hero]
        hero_stats = {stat: hero_stats[stat] + stats_diff[stat] for stat in hero_stats.keys()}
        player_stats[curr_hero] = hero_stats
    else:
        player_stats[curr_hero] = stats_diff


def stats_all_zero(stat_row: dict):
    """
    Check if players stats (dmg, healing, elims, etc.) are all 0.

    This does NOT include seconds played on purpose.
    """

    # Columns that get reset when a person disconnects
    columns = set(col for col in LogCol) - set([LogCol.SECONDS, LogCol.PLAYER, LogCol.HERO])

    return sum(stat_row[col] for col in columns) == 0


def hero_selected(log_row: dict) -> bool:
    return bool(log_row[LogCol.HERO])


def start_df_at_hero_select(df: pd.DataFrame) -> pd.DataFrame:
    heroes = df[LogCol.HERO]
    for index, hero in heroes.iteritems():
        if hero:
            hero_selected_idx = index
            break

    df = df.drop(index=[n for n in range(0, hero_selected_idx)]).reset_index(drop=True)
    hero_select_row = df.loc[hero_selected_idx].to_dict()

    return hero_select_row, df


def skip_inaction(log: pd.DataFrame):
    """
    Returns the first row (start of current hero) and skips to where the
    action starts int he dataframe (player starts damaging, healing, etc.)
    """

    df = log.reset_index(drop=True)
    first_row = df.head(1).to_dict('records')[0]
    if not hero_selected(first_row):
        first_row, df = start_df_at_hero_select(df)

    for row in df.itertuples():
        row = row._asdict()
        if not stats_all_zero(row):
            action_start_idx = row['Index']
            break  # We've found where the action has started

    df = df.drop(index=[n for n in range(0, action_start_idx)])
    df = df.reset_index(drop=True)  # Reset index for future indexing operations

    return first_row, df


def calculate_player_stats(log: [pd.DataFrame]) -> {str: {}}:
    """
    Get stats for a single player from a that player's match log.

    :param player_log: (pandas.DataFrame) DataFrame containing a match log for a single
        player
    :return: A players stats as a dict with keys=heros played, values=dict of stats on
        that hero
    """

    player_stats = {}
    # player_log = log.copy()
    # curr_hero_start = player_log.head(1).to_dict('records')[0]  # First row as dict
    curr_hero_start, player_log = skip_inaction(log)
    curr_hero = curr_hero_start[LogCol.HERO]  # Starting hero
    prev_row = None  # Track prev row in case of player disconnect
    for row in player_log.itertuples():
        row = row._asdict()
        if stats_all_zero(row):  # Player disconnected
            if prev_row:
                # Calculate the stats accumulated on the hero prior to disconnect
                stats_diff = calculate_stat_diff(curr_hero_start, prev_row)
                update_player_stats(player_stats, stats_diff, curr_hero)

            post_dc_log = player_log.drop(index=[n for n in range(0, row['Index'])])
            post_dc_player_stats = calculate_player_stats(post_dc_log)
            for hero in post_dc_player_stats:
                stats_diff = post_dc_player_stats[hero]
                update_player_stats(player_stats, stats_diff, hero)

            # rest of stats already processed through recursive call
            return player_stats

        # Hero swap
        if row[LogCol.HERO] != curr_hero_start[LogCol.HERO]:
            # Calculate the stats accumulated on hero they swapped off of
            stats_diff = calculate_stat_diff(curr_hero_start, row)
            update_player_stats(player_stats, stats_diff, curr_hero)
            # Update our trackers
            curr_hero_start = row
            curr_hero = curr_hero_start[LogCol.HERO]

        prev_row = row

    # Game ended
    last_row = player_log.tail(1).to_dict('records')[0]  # Last row as dict
    stats_diff = calculate_stat_diff(curr_hero_start, last_row)
    update_player_stats(player_stats, stats_diff, curr_hero)

    return player_stats


def update_match_stats(match_stats: {}, map_stats: {}) -> None:
    """Update match stats with stats from single map"""
    for player in map_stats:
        if player not in match_stats:  # No match stats yet for player
            match_stats[player] = map_stats[player]
            continue

        for hero in map_stats[player]:  # Update player's existing match stats
            update_player_stats(match_stats[player], map_stats[player][hero], hero)


def get_match_stats(match_log: [pd.DataFrame]):
    match_stats = {}
    for map_log in match_log:
        players_map_logs = get_map_logs_per_player(map_log)
        map_stats = {}
        for player in players_map_logs:
            map_stats[player] = calculate_player_stats(players_map_logs[player])

        update_match_stats(match_stats, map_stats)

    return match_stats


def update_season_stats(season_stats: dict, match_stats: dict) -> None:
    for player in match_stats:
        if player in season_stats:  # Existing player stats for this season
            for hero in match_stats[player]:
                update_player_stats(season_stats[player], match_stats[player][hero], hero)
        else:  # No stats for player yet in current season
            season_stats[player] = match_stats[player]


def get_player_season_stats(log_paths: [Path]) -> dict:
    season_stats = {}
    for log_path in log_paths:
        match_log = load_match_log(log_path)
        match_stats = get_match_stats(match_log)

        update_season_stats(season_stats, match_stats)

    return season_stats


def reduce_to_df(season_stats: dict) -> pd.DataFrame:
    stats_records = []
    for player in season_stats:
        for hero in season_stats[player]:
            record = {StatsCol.PLAYER: player, StatsCol.HERO: hero, **season_stats[player][hero]}
            stats_records.append(record)

    return pd.DataFrame.from_records(stats_records, columns=[col.value for col in StatsCol])


if __name__ == '__main__':
    # ARGS = parse_args().__dict__

    log_paths = utils.get_log_paths(DEFAULT_LOGS_DIR)

    season_stats = get_player_season_stats(log_paths)
    season_stats_df = reduce_to_df(season_stats)
    utils.fix_hero_names(season_stats_df)
    season_stats_df = utils.prettify_columns(season_stats_df)

    print(season_stats_df)
    season_stats_df.to_csv('season_stats.csv', index=False)
