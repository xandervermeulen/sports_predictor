import os

import pandas as pd

from config.db_config import db

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
csv_file = os.path.join(root_dir, os.getenv('DATA_DIR'), os.getenv('PROCESSED_DATA_DIR'), os.getenv('FIGHTER_DETAILS_AND_IMAGES_FILE'))
image_data = pd.read_csv(csv_file, index_col=0)

DEFAULT_URL = os.getenv('DEFAULT_UFC_IMAGE_URL')


class Fighter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fighter = db.Column(db.String(100), primary_key=False)
    avg_kd = db.Column(db.Float, nullable=False)
    avg_sub_att = db.Column(db.Float, nullable=False)
    avg_td_perc = db.Column(db.Float, nullable=False)
    avg_sig_str_perc = db.Column(db.Float, nullable=False)
    avg_tot_str = db.Column(db.Float, nullable=False)
    avg_round = db.Column(db.Float, nullable=False)
    avg_ctrl_sec = db.Column(db.Float, nullable=False)
    wins = db.Column(db.Integer, nullable=False)
    losses = db.Column(db.Integer, nullable=False)
    draws = db.Column(db.Integer, nullable=False)
    win_perc = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    reach = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    img_url = db.Column(db.String(100), nullable=True)

    def __init__(self, fighter_id, fighter, avg_kd, avg_sub_att, avg_td_perc, avg_sig_str_perc, avg_tot_str, avg_round,
                 avg_ctrl_sec, wins,
                 losses, draws, win_perc, height, reach, weight, img_url=None):
        self.id = fighter_id
        self.fighter = fighter
        self.avg_kd = avg_kd
        self.avg_sub_att = avg_sub_att
        self.avg_td_perc = avg_td_perc
        self.avg_sig_str_perc = avg_sig_str_perc
        self.avg_tot_str = avg_tot_str
        self.avg_round = avg_round
        self.avg_ctrl_sec = avg_ctrl_sec
        self.wins = wins
        self.losses = losses
        self.draws = draws
        self.win_perc = win_perc
        self.height = height
        self.reach = reach
        self.weight = weight
        self.img_url = img_url

    def to_json(self):
        return {
            'fighter': self.fighter,
            'avg_kd': self.avg_kd,
            'avg_sub_att': self.avg_sub_att,
            'avg_td_perc': self.avg_td_perc,
            'avg_sig_str_perc': self.avg_sig_str_perc,
            'avg_tot_str': self.avg_tot_str,
            'avg_round': self.avg_round,
            'avg_ctrl_sec': self.avg_ctrl_sec,
            'wins': self.wins,
            'losses': self.losses,
            'draws': self.draws,
            'height': self.height,
            'reach': self.reach,
            'weight': self.weight,
            'img_url': self.img_url
        }

    def add_image(self):
        fighter_data = image_data[image_data['FIGHTER'] == self.fighter]
        if not fighter_data.empty:
            image_url = str(fighter_data.iloc[0]['image_url'])
            self.img_url = DEFAULT_URL if not image_url.endswith('.png') else image_url
