import re


def clean_player_name(name):
    cleaned_name = re.sub(r'\[.*?]|\(.*?\)|\s', '', name).strip()
    return cleaned_name


def add_space_before_uppercase(s):
    return re.sub(r'([A-Z])', r' \1', s).strip()


def clean_player_stats_names(df):
    df['cleaned_player'] = df['player'].apply(clean_player_name)
    return df
