from enum import Enum

streak_info = {}

total_streak_rating = {}

longest_streak_rating = {}

last_10_info = {}

last_10_rating = {}

last_20_info = {}

last_20_rating = {}

last_40_info = {}

last_40_rating = {}

recent_form_rating = {}

recent_form_trends = {}


class recent_form_weights(Enum):
    LAST_10 = 0.35
    LAST_20 = 0.25
    LAST_40 = 0.15
    TOTAL_STREAK = 0.15
    LONGEST_STREAK = 0.10


def recent_form_get_dict() -> dict:
    return recent_form_rating


def recent_form_get_streak_dict() -> dict:
    return total_streak_rating


def recent_form_get_longest_streak_dict() -> dict:
    return longest_streak_rating


def recent_form_get_last_10_dict() -> dict:
    return last_10_rating


def recent_form_get_last_20_dict() -> dict:
    return last_20_rating


def recent_form_get_last_40_dict() -> dict:
    return last_40_rating


def recent_form_get_trend_dict() -> dict:
    return recent_form_trends


def recent_form_reset() -> None:
    streak_info.clear()
    total_streak_rating.clear()
    last_10_info.clear()
    last_10_rating.clear()
    last_20_info.clear()
    last_20_rating.clear()
    last_40_info.clear()
    last_40_rating.clear()
    recent_form_rating.clear()
    recent_form_trends.clear()


def recent_form_get_data_set(match_data : dict={}) -> list:
    game_result = {}
    game_value = {}

    home_team = match_data['game_stats']['home_team']
    home_team_stats = match_data['game_stats'][home_team]["team_stats"]
    away_team = match_data['game_stats']['away_team']
    away_team_stats = match_data['game_stats'][away_team]["team_stats"]
    home_score_final = home_team_stats["first_period_goals"] + \
        home_team_stats["second_period_goals"] + \
        home_team_stats["third_period_goals"]
    away_score_final = away_team_stats["first_period_goals"] + \
        away_team_stats["second_period_goals"] + \
        away_team_stats["third_period_goals"]
    final_game_state = match_data['game_stats']['result']

    # determin the winner and loser from game score
    # determine who won and lost the game
    if home_score_final > away_score_final:
        winner = home_team
        loser = away_team
    else:
        winner = away_team
        loser = home_team

    # if the home team wins
    game_result[winner] = "W"
    game_value[winner] = 1.0
    if final_game_state == "REG":
        game_result[loser] = "L"
        game_value[loser] = 0.0
    else:
        game_result[loser] = "OT"
        game_value[loser] = (-1.0 / 3.0)
    return {'game result' : game_result, 'game value' : game_value}


def recent_form_add_match_to_streak(streak : dict={}) -> None:
    for team in streak.keys():

        # if the team already is in the list of team streaks
        if team in streak_info.keys():

            # if the streak is changed, update the number of different streaks
            # in the season, and reset the current streak count
            if streak[team] != streak_info[team]["current_streak_ordinal"]:
                streak_info[team]["current_streak_count"] = 1
                streak_info[team]["current_streak_ordinal"] = streak[team]
                streak_info[team]["number_streaks"] += 1

            # if the streak continues, update the count for it and check against
            # the teams longest streak
            else:
                streak_info[team]["current_streak_count"] += 1
                if (streak_info[team]["current_streak_count"] > 
                    streak_info[team]["longest_streak_count"]):
                    streak_info[team]["longest_streak_count"] = \
                        streak_info[team]["current_streak_count"]
                    streak_info[team]["longest_streak_ordinal"] = streak[team]
            
            # now determine how to adjust the total streak score based on the
            # result type
            if streak[team] == "W":
                streak_info[team]["total_streak_score"] += 1
            if streak[team] == "L":
                streak_info[team]["total_streak_score"] -= 1
            else:
                streak_info[team]["total_streak_score"] += (-1.0 / 3.0)

        # otherwise if we have to add the team to the streak list
        else:
            if streak[team] == "W":
                streak_score = 1
            if streak[team] == "L":
                streak_score = -1
            else:
                streak_score = (-1.0 / 3.0)
            streak_info[team] = {
                "current_streak_ordinal" : streak[team],
                "current_streak_count" : 1,
                "longest_streak_ordinal" : streak[team],
                "longest_streak_count" : 1,
                "total_streak_score" : streak_score,
                "number_streaks" : 1,
            }


def recent_form_add_match_to_recent_lists(match_score : dict={}) -> None:
    for team in match_score.keys():

        # if the last ten list is already full pop the first item off
        if team in last_10_info.keys():
            if len(last_10_info[team]) >= 10:
                last_10_info[team].pop(0)    
            last_10_info[team].append(match_score[team])
        else:
            last_10_info[team] = [match_score[team]]

        # do the same but for the last twenty list
        # if the last ten list is already full pop the first item off
        if team in last_20_info.keys():
            if len(last_20_info[team]) >= 20:
                last_20_info[team].pop(0)    
            last_20_info[team].append(match_score[team])
        else:
            last_20_info[team] = [match_score[team]]

        # now finally do the same for last fourty
        if team in last_40_info.keys():
            if len(last_40_info[team]) >= 40:
                last_40_info[team].pop(0)    
            last_40_info[team].append(match_score[team])
        else:
            last_40_info[team] = [match_score[team]]


def recent_form_add_match_data(recent_form_data : dict={}) -> None:
    recent_form_add_match_to_streak(recent_form_data['game result'])
    recent_form_add_match_to_recent_lists(recent_form_data['game value'])


def recent_form_calculate_all() -> None:
    for team in streak_info.keys():
        total_streak_rating[team] = (
            streak_info[team]["total_streak_score"] /
            streak_info[team]["number_streaks"]
        )
        if streak_info[team]['longest_streak_ordinal'] == "W":
            longest_streak_rating[team] = (
                streak_info[team]['longest_streak_count']
            )
        elif streak_info[team]['longest_streak_ordinal'] == "L":
            longest_streak_rating[team] = (
                streak_info[team]['longest_streak_count'] * -1
            )
        else:
            longest_streak_rating[team] = (
                streak_info[team]['longest_streak_count'] * (-1.0 / 3.0)
            )
        last_10_rating[team] = sum(last_10_info[team])
        last_20_rating[team] = sum(last_20_info[team])
        last_40_rating[team] = sum(last_40_info[team])


def recent_form_combine_metrics() -> None:
    for team in streak_info.keys():
        recent_form_rating[team] = (
            (total_streak_rating[team] *
                recent_form_weights.TOTAL_STREAK.value) +
            (longest_streak_rating[team] *
                recent_form_weights.LONGEST_STREAK.value) +
            (last_10_rating[team] *
                recent_form_weights.LAST_10.value) +
            (last_20_rating[team] *
                recent_form_weights.LAST_20.value) +
            (last_40_rating[team] *
                recent_form_weights.LAST_40.value)
        )


def recent_form_update_trends(date : str="") -> None:
    recent_form_trends[date] = {}
    for team in recent_form_rating.keys():
        recent_form_trends[date][team] = recent_form_rating[team]
