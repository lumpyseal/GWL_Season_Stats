from __future__ import annotations
if '__TYPING__':
    import pandas as pd

from typing import Union
from pathlib import Path

from enums import LogCol, StatsCol

"""Miscellaneous utils that aren't important enough to put in main."""


def format_lines(l: [str]) -> [str]:
    """
    ...

    :param l: List of lines from a log file
    :return: Lines formatted for ingest into DataFrame
    """
    end_of_timestamp = 10  # 10 char timestamp
    # Remove timestamp from all lines
    lines = [line[end_of_timestamp:].strip() for line in l]
    line_values = [line.split(',') for line in lines]

    return line_values


def get_log_paths(_dir: Union[str, Path]) -> [Path]:
    logs_dir = Path(_dir)

    return list(logs_dir.glob('*.txt'))


def update_log_col_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cast columns to their appropriate values
    """
    conversion_dict = {
        LogCol.SECONDS: float,
        LogCol.ELIMS: int,
        LogCol.FB: int,
        LogCol.DMG: float,
        LogCol.DEATHS: int,
        LogCol.HEALING: float,
        LogCol.DMG_BLOCKED: float
    }

    return df.astype(conversion_dict)


def fix_hero_names(df: pd.DataFrame) -> None:
    """
    Fix hero names in-place
    """
    hero_name_fix = {'Lúcio': 'Lucio', 'Torbjörn': 'Torbjorn'}
    df[StatsCol.HERO] = df[StatsCol.HERO].replace(to_replace=hero_name_fix)


def prettify_columns(season_stats_df) -> pd.DataFrame:
    """
    Take the floor of all float columns.
    """

    conversion_dict = {
        StatsCol.TIME: int,
        StatsCol.DMG: int,
        StatsCol.HEALING: int,
        StatsCol.DMG_BLOCKED: int
    }

    return season_stats_df.astype(conversion_dict)
