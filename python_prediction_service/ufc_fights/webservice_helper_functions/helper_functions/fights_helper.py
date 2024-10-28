import pandas as pd

from ufc_fights.domain.Fight import Fight
from ufc_fights.webservice_helper_functions.helper_functions.prediction_helper import predict_fights, format_fights
from ufc_fights.webservice_helper_functions.managers.DataManager import dm
from ufc_fights.webservice_helper_functions.managers.DatabaseManager import dbm


def update_all_fights(all_past_fights, events):
    past_fights = []
    all_past_fights[['fighter1', 'fighter2']] = all_past_fights['BOUT'].str.split(' vs. ', expand=True)
    for _, fight in all_past_fights.iterrows():
        current_fight = dm.get_fight(fight)
        if current_fight is not None:
            new_past_fight = dm.create_past_fight(current_fight)
            past_fights.append(new_past_fight)
            dbm.delete_fight(current_fight)
        else:
            past_fight = dm.get_past_fight(fight)
            if past_fight is None:
                if 'predicted_outcome' not in fight and 'accuracy' not in fight:
                    # rename the EVENT col from events df to event
                    events.rename(columns={'EVENT': 'event'}, inplace=True)
                    # convert fight (Series) to pandas DataFrame
                    fight_df = pd.DataFrame([fight])
                    # in the EVENT col of fight_df remove the space at the end of the string
                    fight_df['EVENT'] = fight_df['EVENT'].str.rstrip()
                    # same for fighter1 and fighter2
                    fight_df['fighter1'] = fight_df['fighter1'].str.rstrip()
                    fight_df['fighter2'] = fight_df['fighter2'].str.rstrip()
                    merged_df = fight_df.merge(events, left_on='EVENT', right_on='event', how='inner')
                    formatted_df = merged_df[['EVENT', 'fighter1', 'fighter2']]
                    formatted_df.rename(columns={'EVENT': 'event', 'date': 'event_date', 'location': 'event_location'},
                                        inplace=True)
                    # only select the rows with a unique fighter1 and fighter2 combination
                    formatted_df = formatted_df.drop_duplicates(subset=['fighter1', 'fighter2'])
                    fight_predictions = predict_fights(formatted_df)
                    if fight_predictions is None:
                        continue
                    # add a column actual_outcome to fight_predictions from the fight df
                    fight_predictions['actual_outcome'] = fight['OUTCOME']

                    fight = fight_predictions
                    fight.rename(columns={'outcome_predicted': 'predicted_outcome', 'W/L':'accuracy' }, inplace=True)
                    # all the values in fight are saved as Series so we need the value
                    fight = fight.iloc[0]

                new_fight = dm.create_past_fight(fight)
                past_fights.append(new_fight)

    dbm.update_past_fights_to_db(past_fights)


def add_fights_to_db(predictions):
    new_fights = []
    for _, row in predictions.iterrows():
        event, fighter1, fighter2, prediction, accuracy, *actual_outcome = row
        if not dm.check_duplicate_fight(event, fighter1, fighter2):
            new_fight = Fight(event, fighter1, fighter2, prediction, accuracy)
        else:
            new_fight = Fight.query.filter_by(event=event, fighter1=fighter1, fighter2=fighter2).first()
            new_fight.prediction = prediction
            new_fight.accuracy = accuracy
        new_fights.append(new_fight)
    dbm.update_fights_to_db(new_fights)
