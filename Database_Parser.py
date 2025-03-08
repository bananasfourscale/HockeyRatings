from multiprocessing import Process, Queue
import requests
import json
import pandas
import datetime
import pytz

from User_Interface_Main import update_progress_bar, \
    update_progress_text
from Ice_Mapping import event_point_get_zone, determine_offensive_side

database_parser_input_queue = Queue()
database_parser_output_queue = Queue()


def parse_play_by_play_penalties(home_team : str="", away_team : str="",
    play : dict={}, game_stats : dict={}) -> dict:

    period = play["periodDescriptor"]["number"]
    time = play["timeInPeriod"]
    committed_by = None

    # commited penalties
    if "committedByPlayerId" in play["details"].keys():

        # home team penalty
        if (play["details"]["committedByPlayerId"] in
            game_stats[home_team]["player_stats"]):

            game_stats[home_team]["team_stats"]["penalty_minutes"] += \
                play["details"]["duration"]
            game_stats[home_team]["player_stats"]\
                [play["details"]["committedByPlayerId"]]\
                ["penalty_minutes"] += play["details"]["duration"]
            game_stats[away_team]["team_stats"]["power_play_chances"] += 1
            game_stats[home_team]["team_stats"]["short_handed_chances"] += 1
            committed_by = home_team

        # away team penalty
        elif (play["details"]["committedByPlayerId"] in
            game_stats[away_team]["player_stats"]):

            game_stats[away_team]["team_stats"]["penalty_minutes"] += \
                play["details"]["duration"]
            game_stats[away_team]["player_stats"]\
                [play["details"]["committedByPlayerId"]]\
                ["penalty_minutes"] += play["details"]["duration"]
            game_stats[home_team]["team_stats"]["power_play_chances"] += 1
            game_stats[away_team]["team_stats"]["short_handed_chances"] += 1
            committed_by = away_team
        else:
            print("Penalties Commited Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["committedByPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())

    # drawn penalties
    if "drawnByPlayerId" in play["details"].keys():

        # home team drawn penalty
        if (play["details"]["drawnByPlayerId"] in
            game_stats[home_team]["player_stats"]):

            game_stats[home_team]["team_stats"]["penalties_drawn"] += \
                play["details"]["duration"]
            game_stats[home_team]["player_stats"]\
                [play["details"]["drawnByPlayerId"]]\
                ["penalty_minutes_drawn"] += play["details"]["duration"]

        # away team drawn penalty
        elif (play["details"]["drawnByPlayerId"] in
            game_stats[away_team]["player_stats"]):

            game_stats[away_team]["team_stats"]["penalties_drawn"] += \
                play["details"]["duration"]
            game_stats[away_team]["player_stats"]\
                [play["details"]["drawnByPlayerId"]]\
                ["penalty_minutes_drawn"] += play["details"]["duration"]
        else:
            print("Penalties Drawn By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["drawnByPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())

    # get the zone where the penalty occured
    penalty_commited_zone = event_point_get_zone(play["details"]["xCoord"],
        play["details"]["yCoord"])
    # game_stats["zone_stats"]["penalties"].append({penalty_commited_zone : play})
    
    # if away team commited offensive penalty
    if (committed_by == away_team and
        determine_offensive_side(period, "away", penalty_commited_zone) == 
            "offensive"):

        game_stats[away_team]["player_stats"]\
            [play["details"]["committedByPlayerId"]]\
            ["penalty_minutes_drawn"] += (play["details"]["duration"] * 0.2)
    
    # if home team commited offensive penalty
    elif (committed_by == home_team and 
        determine_offensive_side(period, "home", penalty_commited_zone) == 
            "offensive"):

        game_stats[home_team]["player_stats"]\
            [play["details"]["committedByPlayerId"]]\
            ["penalty_minutes_drawn"] += (play["details"]["duration"] * 0.2)

    return game_stats


def parse_play_by_play_hits(home_team : str="", away_team : str="",
    play : dict={}, game_stats : dict={}) -> dict:

    # hits delivered
    # home hits
    if (play["details"]["hittingPlayerId"] in
        game_stats[home_team]["player_stats"]):

        game_stats[home_team]["team_stats"]["hits"] += 1
        game_stats[home_team]["player_stats"]\
            [play["details"]["hittingPlayerId"]]\
            ["hits"] += 1
        
    # away hits
    elif (play["details"]["hittingPlayerId"] in
        game_stats[away_team]["player_stats"]):

        game_stats[away_team]["team_stats"]["hits"] += 1
        game_stats[away_team]["player_stats"]\
            [play["details"]["hittingPlayerId"]]\
            ["hits"] += 1
    else:
        print("Hits Delivered By Player\n" + 
            "Player Id Not in Either Teams Roster:",
            play["details"]["hittingPlayerId"])
        print(game_stats[home_team]["player_stats"].keys())

    # hits taken
    # home hits taken
    if (play["details"]["hitteePlayerId"] in
        game_stats[home_team]["player_stats"]):

        game_stats[home_team]["team_stats"]["getting_hit"] += 1
        game_stats[home_team]["player_stats"]\
            [play["details"]["hitteePlayerId"]]\
            ["hits_taken"] += 1
        
    # away hits taken
    elif (play["details"]["hitteePlayerId"] in
        game_stats[away_team]["player_stats"]):

        game_stats[away_team]["team_stats"]["getting_hit"] += 1
        game_stats[away_team]["player_stats"]\
            [play["details"]["hitteePlayerId"]]\
            ["hits_taken"] += 1
    else:
        print("Hits Recieved By Player\n" + 
            "Player Id Not in Either Teams Roster:",
            play["details"]["hitteePlayerId"])
        print(game_stats[home_team]["player_stats"].keys())

    # get the zone where the hit occured
    hit_commited_zone = event_point_get_zone(play["details"]["xCoord"],
        play["details"]["yCoord"])
    # game_stats["zone_stats"]["hits"].append({hit_commited_zone : play})
    return game_stats


def parse_play_by_play_takeaways_and_giveaways(home_team : str="", 
    away_team : str="", play : dict={}, game_stats : dict={}) -> dict:
    play_type = play["typeDescKey"]

    # takeaways
    if play_type == "takeaway":
        if (play["details"]["playerId"] in
            game_stats[home_team]["player_stats"]):

            game_stats[home_team]["team_stats"]["takeaways"] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["playerId"]]\
                ["takeaways"] += 1
        elif (play["details"]["playerId"] in
            game_stats[away_team]["player_stats"]):

            game_stats[away_team]["team_stats"]["takeaways"] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["playerId"]]\
                ["takeaways"] += 1
        else:
            print("Takeaway By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["playerId"])
            print(game_stats[home_team]["player_stats"].keys())

    # giveaways
    if play_type == "giveaway":
        if (play["details"]["playerId"] in
            game_stats[home_team]["player_stats"]):

            game_stats[home_team]["team_stats"]["giveaways"] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["playerId"]]\
                ["giveaways"] += 1
        elif (play["details"]["playerId"] in
            game_stats[away_team]["player_stats"]):

            game_stats[away_team]["team_stats"]["giveaways"] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["playerId"]]\
                ["giveaways"] += 1
        else:
            print("Giveawayw By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["playerId"])
            print(game_stats[home_team]["player_stats"].keys())

    # get the zone where the takeaways occured
    takeaways_commited_zone = event_point_get_zone(play["details"]["xCoord"],
        play["details"]["yCoord"])
    # game_stats["zone_stats"]["takeaways"].append(
    #     {takeaways_commited_zone : play})
    # game_stats["zone_stats"]["giveaways"].append(
    #     {takeaways_commited_zone : play})
    return game_stats


def parse_play_by_play_shots(home_team : str="", away_team : str="",
    play : dict={}, game_stats : dict={}) -> dict:
    play_type = play["typeDescKey"]

    # blocked shots
    if play_type == "blocked-shot":

        # shots blocked
        if "blockingPlayerId" in play["details"].keys():
            if (play["details"]["blockingPlayerId"] in
                game_stats[home_team]["player_stats"]):

                game_stats[home_team]["team_stats"]["blocks"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["blockingPlayerId"]]["blocks"] += 1
            elif (play["details"]["blockingPlayerId"] in
                game_stats[away_team]["player_stats"]):

                game_stats[away_team]["team_stats"]["blocks"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["blockingPlayerId"]]["blocks"] += 1
            else:
                print("Shot-Block By Player\n" + 
                    "Player Id Not in Either Teams Roster:",
                    play["details"]["blockingPlayerId"])
                print(game_stats[home_team]["player_stats"].keys())

        # own shots blocked
        if "shootingPlayerId" in play["details"].keys():
            if (play["details"]["shootingPlayerId"] in
                game_stats[home_team]["player_stats"]):

                game_stats[home_team]["team_stats"]["blocked_shots"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["shootingPlayerId"]]["blocked_shots"] += 1
            elif (play["details"]["shootingPlayerId"] in
                game_stats[away_team]["player_stats"]):

                game_stats[away_team]["team_stats"]["blocked_shots"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["shootingPlayerId"]]["blocked_shots"] += 1
            else:
                print("Own Shot Blocked By Player\n" + 
                    "Player Id Not in Either Teams Roster:",
                    play["details"]["shootingPlayerId"])
                print(game_stats[home_team]["player_stats"].keys())
    
    # missed shot
    if play_type == "missed-shot":
        if "shootingPlayerId" in play["details"].keys():
            if (play["details"]["shootingPlayerId"] in
                game_stats[home_team]["player_stats"]):
                game_stats[home_team]["player_stats"]\
                    [play["details"]["shootingPlayerId"]]\
                    ["missed_shots"] += 1
            elif (play["details"]["shootingPlayerId"] in
                game_stats[away_team]["player_stats"]):
                game_stats[away_team]["player_stats"]\
                    [play["details"]["shootingPlayerId"]]\
                    ["missed_shots"] += 1
            else:
                print("Missed Shot By Player\n" + 
                    "Player Id Not in Either Teams Roster:",
                    play["details"]["shootingPlayerId"])
                print(game_stats[home_team]["player_stats"].keys())
            
    # shots on goal
    if play_type == "shot-on-goal":
        if "shootingPlayerId" in play["details"].keys():
            if (play["details"]["shootingPlayerId"] in
                game_stats[home_team]["player_stats"]):

                game_stats[home_team]["team_stats"]["shots"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["shootingPlayerId"]]["shots_on_goal"] += 1
            elif (play["details"]["shootingPlayerId"] in
                game_stats[away_team]["player_stats"]):

                game_stats[away_team]["team_stats"]["shots"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["shootingPlayerId"]]["shots_on_goal"] += 1
            else:
                print("Shot By Player\n" + 
                    "Player Id Not in Either Teams Roster:",
                    play["details"]["shootingPlayerId"])
                print(game_stats[home_team]["player_stats"].keys())
    
    # get the zone where the shot occured
    shot_commited_zone = event_point_get_zone(play["details"]["xCoord"],
        play["details"]["yCoord"])
    # game_stats["zone_stats"]["shots"].append({shot_commited_zone : play})
    return game_stats


def parse_play_by_play_faceoffs(home_team : str="", away_team : str="",
    play : dict={}, game_stats : dict={}) -> dict:

    # losing player just gets an attempt
    # home player
    if (play["details"]["losingPlayerId"] in
        game_stats[home_team]["player_stats"]):

        game_stats[home_team]["team_stats"]["faceoff_attempts"] += 1
        game_stats[home_team]["player_stats"]\
            [play["details"]["losingPlayerId"]]["faceoff_attempts"] += 1
        
    # away player
    elif (play["details"]["losingPlayerId"] in
        game_stats[away_team]["player_stats"]):

        game_stats[away_team]["team_stats"]["faceoff_attempts"] += 1
        game_stats[away_team]["player_stats"]\
            [play["details"]["losingPlayerId"]]["faceoff_attempts"] += 1
    else:
        print("Faceoff Lost By Player\n" + 
            "Player Id Not in Either Teams Roster:",
            play["details"]["shootingPlayerId"])
        print(game_stats[home_team]["player_stats"].keys())
        
    # winning player gets a win and an attempts
    if (play["details"]["winningPlayerId"] in
        game_stats[home_team]["player_stats"]):

        game_stats[home_team]["team_stats"]["faceoff_attempts"] += 1
        game_stats[home_team]["team_stats"]["faceoff_wins"] += 1
        game_stats[home_team]["player_stats"]\
            [play["details"]["winningPlayerId"]]["faceoff_attempts"] += 1
        game_stats[home_team]["player_stats"]\
            [play["details"]["winningPlayerId"]]["faceoff_wins"] += 1
    elif (play["details"]["winningPlayerId"] in
            game_stats[away_team]["player_stats"]):
        
        game_stats[away_team]["team_stats"]["faceoff_attempts"] += 1
        game_stats[away_team]["team_stats"]["faceoff_wins"] += 1
        game_stats[away_team]["player_stats"]\
            [play["details"]["winningPlayerId"]]\
            ["faceoff_attempts"] += 1
        game_stats[away_team]["player_stats"]\
            [play["details"]["winningPlayerId"]]\
            ["faceoff_wins"] += 1
    else:
        print("Faceoff Lost By Player\n" + 
            "Player Id Not in Either Teams Roster:",
            play["details"]["shootingPlayerId"])
        print(game_stats[home_team]["player_stats"].keys())

    # get the zone where the faceoffs occured
    faceoffs_commited_zone = event_point_get_zone(play["details"]["xCoord"],
        play["details"]["yCoord"])
    # game_stats["zone_stats"]["faceoffs"].append({faceoffs_commited_zone : play})
    return game_stats


def parse_play_by_play_goal(home_team : str="", away_team : str="",
    play : dict={}, game_stats : dict={}) -> dict:

    home_goalie_in = bool(int(play["situationCode"][3]))
    away_goalie_in = bool(int(play["situationCode"][0]))
    home_strength = int(play["situationCode"][2])
    away_strength = int(play["situationCode"][1])
    period = play["periodDescriptor"]["number"]

    # which period is the goal in
    if period == 1:
        if (play["details"]["scoringPlayerId"] in
            game_stats[home_team]["player_stats"]):

            game_stats[home_team]["team_stats"]["first_period_goals"] += 1
        else:
            game_stats[away_team]["team_stats"]["first_period_goals"] += 1
    elif period == 2:
        if (play["details"]["scoringPlayerId"] in
            game_stats[home_team]["player_stats"]):

            game_stats[home_team]["team_stats"]["second_period_goals"] += 1
        else:
            game_stats[away_team]["team_stats"]["second_period_goals"] += 1
    elif period == 3:
        if (play["details"]["scoringPlayerId"] in
            game_stats[home_team]["player_stats"]):

            game_stats[home_team]["team_stats"]["third_period_goals"] += 1
        else:
            game_stats[away_team]["team_stats"]["third_period_goals"] += 1
    elif period == 4:
        if (play["details"]["scoringPlayerId"] in
            game_stats[home_team]["player_stats"]):

            game_stats[home_team]["team_stats"]["OT_goals"] += 1
        else:
            game_stats[away_team]["team_stats"]["OT_goals"] += 1
    else:
        if (play["details"]["scoringPlayerId"] in
            game_stats[home_team]["player_stats"]):

            game_stats[home_team]["team_stats"]["SO_goals"] += 1
        else:
            game_stats[away_team]["team_stats"]["SO_goals"] += 1

    # home shorthanded
    if (((home_goalie_in and away_goalie_in) and home_strength < away_strength)
        or ((not home_goalie_in) and home_strength <= away_strength)):

        # home team player
        if (play["details"]["scoringPlayerId"] in
            game_stats[home_team]["player_stats"]):

            # goal
            game_stats[home_team]["team_stats"]['short_handed_goals'] += 1
            game_stats[home_team]["team_stats"]['goals'] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["short_handed_goals"] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["goals"] += 1
            
            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["short_handed_assists_primary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["primary_assist"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["assists"] += 1
                
            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["short_handed_assists_secondary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["secondary_assist"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]["assists"] += 1
                
        # away team player
        elif (play["details"]["scoringPlayerId"] in
            game_stats[away_team]["player_stats"]):

            # goal
            game_stats[away_team]["team_stats"]['power_play_goals'] += 1
            game_stats[away_team]["team_stats"]['goals'] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["power_play_goals"] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["goals"] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["power_play_assists_primary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["primary_assist"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["power_play_assists_secondary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["secondary_assist"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]["assists"] += 1
        else:
            print("Shorthanded Goal By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["scoringPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())
    
    # away shorthanded
    elif (((home_goalie_in and away_goalie_in) and
        away_strength < home_strength)
        or 
        ((not away_goalie_in) and away_strength <= home_strength)):

        # away team player
        if (play["details"]["scoringPlayerId"] in
            game_stats[away_team]["player_stats"]):

            # goal
            game_stats[away_team]["team_stats"]['short_handed_goals'] += 1
            game_stats[away_team]["team_stats"]['goals'] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["short_handed_goals"] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["goals"] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["short_handed_assists_primary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["primary_assist"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["short_handed_assists_secondary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["secondary_assist"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]["assists"] += 1

        # home team player
        elif (play["details"]["scoringPlayerId"] in
            game_stats[home_team]["player_stats"]):

            # goal
            game_stats[home_team]["team_stats"]['power_play_goals'] += 1
            game_stats[home_team]["team_stats"]['goals'] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["power_play_goals"] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["goals"] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["power_play_assists_primary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["primary_assist"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["power_play_assists_secondary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["secondary_assist"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]["assists"] += 1
        else:
            print("Shorthanded Goal By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["scoringPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())

    # empty net goals
    elif (not home_goalie_in):

        # away team player
        if (play["details"]["scoringPlayerId"] in
            game_stats[away_team]["player_stats"]):

            # goal
            game_stats[away_team]["team_stats"]["empty_net_goals"] += 1
            game_stats[away_team]["team_stats"]['goals'] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["empty_net_goals"] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["goals"] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["empty_net_assists_primary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["primary_assist"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["empty_net_assists_secondary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["secondary_assist"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]["assists"] += 1
        else:
            pass
    elif (not away_goalie_in):

        # home team player
        if (play["details"]["scoringPlayerId"] in
            game_stats[home_team]["player_stats"]):

            # goal
            game_stats[home_team]["team_stats"]["empty_net_goals"] += 1
            game_stats[home_team]["team_stats"]['goals'] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["empty_net_goals"] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["goals"] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["empty_net_assists_primary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["primary_assist"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["empty_net_assists_secondary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["secondary_assist"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]["assists"] += 1
        else:
            pass

    # 4-on-4
    elif (home_strength == 4 and away_strength == 4):

        # home team player
        if (play["details"]["scoringPlayerId"] in
            game_stats[home_team]["player_stats"]):

            # goal
            game_stats[home_team]["team_stats"]["4-on-4_goals"] += 1
            game_stats[home_team]["team_stats"]['goals'] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["4-on-4_goals"] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["goals"] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["4-on-4_assists_primary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["primary_assist"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["4-on-4_assists_secondary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["secondary_assist"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]["assists"] += 1

        # away team player
        elif (play["details"]["scoringPlayerId"] in
            game_stats[away_team]["player_stats"]):

            # goal
            game_stats[away_team]["team_stats"]["4-on-4_goals"] += 1
            game_stats[away_team]["team_stats"]['goals'] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["4-on-4_goals"] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["goals"] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["4-on-4_assists_primary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["primary_assist"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["4-on-4_assists_secondary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["secondary_assist"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]["assists"] += 1
        else:
            print("4-on-4 Goal By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["scoringPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())

    # 3-on-3
    elif (home_strength == 3 and away_strength == 3):

        # home team player
        if (play["details"]["scoringPlayerId"] in
            game_stats[home_team]["player_stats"]):

            # goal
            game_stats[home_team]["team_stats"]["3-on-3_goals"] += 1
            game_stats[home_team]["team_stats"]['goals'] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["3-on-3_goals"] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["goals"] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["3-on-3_assists_primary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["primary_assist"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["3-on-3_assists_secondary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["secondary_assist"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]["assists"] += 1

        # away team player
        elif (play["details"]["scoringPlayerId"] in
            game_stats[away_team]["player_stats"]):

            # goal
            game_stats[away_team]["team_stats"]["3-on-3_goals"] += 1
            game_stats[away_team]["team_stats"]['goals'] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["3-on-3_goals"] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["goals"] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["3-on-3_assists_primary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["primary_assist"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["3-on-3_assists_secondary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["secondary_assist"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]["assists"] += 1
        else:
            print("3-on-3 Goal By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["scoringPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())

    # even strength
    else:

        # home team player
        if (play["details"]["scoringPlayerId"] in
            game_stats[home_team]["player_stats"]):

            # goal
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["even_goals"] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["goals"] += 1
            game_stats[home_team]["team_stats"]['goals'] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["even_assists_primary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["primary_assist"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["even_assists_secondary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["secondary_assist"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]["assists"] += 1

        # away team player
        elif (play["details"]["scoringPlayerId"] in
            game_stats[away_team]["player_stats"]):

            # goal
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["even_goals"] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]["goals"] += 1
            game_stats[away_team]["team_stats"]['goals'] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["even_assists_primary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["primary_assist"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["even_assists_secondary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["secondary_assist"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]["assists"] += 1
        else:
            print("Goal By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["scoringPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())

    # get the zone where the goals occured
    goals_commited_zone = event_point_get_zone(play["details"]["xCoord"],
        play["details"]["yCoord"])
    # game_stats["zone_stats"]["goals"].append({goals_commited_zone : play})


def parse_play_by_play_data(game_data : dict={}, game_stats : dict={}) -> dict:
    home_team = game_data["box_score"]["homeTeam"]["commonName"]["default"]
    away_team = game_data["box_score"]["awayTeam"]["commonName"]["default"]

    # loop through every play in the game
    # TODO eventually I might just use this for all data but for now I'm just
    # filling in a few extra gaps
    for play in game_data["play_by_play"]["plays"]:
        play_type = play["typeDescKey"]

        # penalties
        if play_type == "penalty":
            parse_play_by_play_penalties(home_team, away_team, play, game_stats)
                
        # hits
        if play_type == "hit":
            parse_play_by_play_hits(home_team, away_team, play, game_stats)
                
        # takeaways and giveaways
        if play_type == "takeaway" or \
            play_type == "giveaway":
            parse_play_by_play_takeaways_and_giveaways(home_team, away_team,
                play, game_stats)
                
        # blocked shots
        if play_type == "blocked-shot" or play_type ==  "missed-shot" or\
            play_type == "shot-on-goal": 
            parse_play_by_play_shots(home_team, away_team, play,
                game_stats)

        # Faceoffs
        if play["typeDescKey"] == "faceoff":
            parse_play_by_play_faceoffs(home_team, away_team, play, game_stats)

        # goals
        if play["typeDescKey"] == "goal":
            parse_play_by_play_goal(home_team, away_team, play, game_stats)
    return game_stats


def collect_game_stats(game : dict={}) -> dict:

    # Create the default data sets
    home_id = game["box_score"]["homeTeam"]["id"]
    home_team = game["box_score"]["homeTeam"]["commonName"]["default"]
    away_team = game["box_score"]["awayTeam"]["commonName"]["default"]
    # print(game["box_score"]["gameDate"], game["box_score"]["id"],
    #     "\t" + home_team, "\t" + away_team)
    
    # if the game hasn't been played then just fill out the minimum struct to be
    # able to gather past info for prediction engine to run
    if game["box_score"]["gameState"] != "OFF" or \
        game["box_score"]["gameType"] not in [2, 3]:
        game_stats = {
            "home_team" : home_team,
            "away_team" : away_team,
            "game_type" : game["box_score"]["gameType"],
            "game_state" : game["box_score"]["gameState"],
            # "zone_stats" : {
            #     "penalties" : [],
            #     "hits" : [],
            #     "takeaways" : [],
            #     "giveaways" : [],
            #     "shots" : [],
            #     "faceoffs" : [],
            #     "goals" : [],
            # },
            home_team : {
                "team_stats" : {},
                "player_stats" : {}
            },
            away_team : {
                "team_stats" : {},
                "player_stats" : {}
            }
        }
        return game_stats
    
    # if the game is finished create a table of all required data
    try: 
        game_stats = {
            "home_team" : home_team,
            "away_team" : away_team,
            "result" : game["box_score"]["periodDescriptor"]["periodType"],
            "game_type" : game["box_score"]["gameType"],
            "game_state" : game["box_score"]["gameState"],
            # "zone_stats" : {
            #     "penalties" : [],
            #     "hits" : [],
            #     "takeaways" : [],
            #     "giveaways" : [],
            #     "shots" : [],
            #     "faceoffs" : [],
            #     "goals" : [],
            # },
            home_team : {
                "team_stats" : {
                    "goals" : 0,
                    "empty_net_goals" : 0,
                    "4-on-4_goals" : 0,
                    "3-on-3_goals" : 0,
                    "first_period_goals" : 0,
                    "second_period_goals" : 0,
                    "third_period_goals" : 0,
                    "OT_goals" : 0,
                    "SO_goals" : 0,
                    "shots" : 0,
                    "power_play_goals" : 0,
                    "power_play_chances" : 0,
                    "short_handed_goals" : 0,
                    "short_handed_chances" : 0,
                    "penalty_minutes" : 0,
                    "penalties_drawn" : 0,
                    "hits" : 0,
                    "getting_hit" : 0,
                    "blocks" : 0,
                    "blocked_shots" : 0,
                    "giveaways" : 0,
                    "takeaways" : 0,
                    "faceoff_wins" : 0,
                    "faceoff_attempts" : 0,
                },
                "player_stats" : {}
            },
            away_team : {
                "team_stats" : {
                    "goals" : 0,
                    "empty_net_goals" : 0,
                    "4-on-4_goals" : 0,
                    "3-on-3_goals" : 0,
                    "first_period_goals" : 0,
                    "second_period_goals" : 0,
                    "third_period_goals" : 0,
                    "OT_goals" : 0,
                    "SO_goals" : 0,
                    "shots" : 0,
                    "power_play_goals" : 0,
                    "power_play_chances" : 0,
                    "short_handed_goals" : 0,
                    "short_handed_chances" : 0,
                    "penalty_minutes" : 0,
                    "penalties_drawn" : 0,
                    "hits" : 0,
                    "getting_hit" : 0,
                    "blocks" : 0,
                    "blocked_shots" : 0,
                    "giveaways" : 0,
                    "takeaways" : 0,
                    "faceoff_wins" : 0,
                    "faceoff_attempts" : 0,
                },
                "player_stats" : {}
            },
        }
    except KeyError as e:
        print(game["box_score"]["gameState"])
        print(game["box_score"]["id"])
        print(game["box_score"])
        raise e
    except IndexError as i:
        print(game["box_score"]["gameState"])
        print(game["box_score"]["id"])
        raise i

    # create a flat list of players by id so we can reference stats from
    # the boxscore when looping through play-by-play
    list_of_players = (
        game["box_score"]["playerByGameStats"]["awayTeam"]["forwards"] +
        game["box_score"]["playerByGameStats"]["awayTeam"]["defense"] +
        game["box_score"]["playerByGameStats"]["awayTeam"]["goalies"] +
        game["box_score"]["playerByGameStats"]["homeTeam"]["forwards"] +
        game["box_score"]["playerByGameStats"]["homeTeam"]["defense"] +
        game["box_score"]["playerByGameStats"]["homeTeam"]["goalies"]
    )
    players_by_id = {}
    for player in list_of_players:
        players_by_id[player["playerId"]] = player

    # loop through all players and create default data sets for them then add
    # to the default "player_stats" of the main dictionary
    for player in game["play_by_play"]["rosterSpots"]:
        player_id = player["playerId"]
        if player["teamId"] == home_id:

            # game_stats->home/away_team->player_stats->player_name->stats_dict
            if player["positionCode"] == "G":
                game_stats[home_team]["player_stats"][player_id] = {
                    "player_name" : player["firstName"]["default"] + " " +\
                        player["lastName"]["default"],
                    "player_position" : player["positionCode"],
                    "even_saves" :
                        int(players_by_id[player_id]
                            ["evenStrengthShotsAgainst"].split("/")[0]),
                    "even_shots" :
                        int(players_by_id[player_id]
                            ["evenStrengthShotsAgainst"].split("/")[1]),
                    "power_play_saves" :
                        int(players_by_id[player_id]
                            ["powerPlayShotsAgainst"].split("/")[0]),
                    "power_play_shots" :
                        int(players_by_id[player_id]
                            ["powerPlayShotsAgainst"].split("/")[1]),
                    "short_handed_saves" :
                        int(players_by_id[player_id]
                            ["shorthandedShotsAgainst"].split("/")[0]),
                    "short_handed_shots" :
                        int(players_by_id[player_id]
                            ["shorthandedShotsAgainst"].split("/")[1]),
                    "goals" : 0,
                    "even_goals" : 0,
                    "power_play_goals" : 0,
                    "short_handed_goals" : 0,
                    "empty_net_goals" : 0,
                    "4-on-4_goals" : 0,
                    "3-on-3_goals" : 0,
                    "assists" : 0,
                    "primary_assist" : 0,
                    "secondary_assist" : 0,
                    "even_assists_primary" : 0,
                    "power_play_assists_primary" : 0,
                    "short_handed_assists_primary" : 0,
                    "empty_net_assists_primary" : 0,
                    "4-on-4_assists_primary" : 0,
                    "3-on-3_assists_primary" : 0,
                    "even_assists_secondary" : 0,
                    "power_play_assists_secondary" : 0,
                    "short_handed_assists_secondary" : 0,
                    "empty_net_assists_secondary" : 0,
                    "4-on-4_assists_secondary" : 0,
                    "3-on-3_assists_secondary" : 0,
                    "plus_minus" : 0,
                    "penalty_minutes" : 0,
                    "penalty_minutes_drawn" : 0,
                    "hits" : 0,
                    "hits_taken" : 0,
                    "takeaways" : 0,
                    "giveaways" : 0,
                    "blocks" : 0,
                    "blocked_shots" : 0,
                    "missed_shots" : 0,
                    "shots_on_goal" : 0,
                    "faceoff_wins" : 0,
                    "faceoff_attempts" : 0,
                    "time_on_ice" : players_by_id[player_id]["toi"],
                }
            else:
                game_stats[home_team]["player_stats"][player_id] = {
                    "player_name" : player["firstName"]["default"] + " " +\
                        player["lastName"]["default"],
                    "player_position" : player["positionCode"],
                    "even_saves" : 0,
                    "even_shots" : 0,
                    "power_play_saves" : 0,
                    "power_play_shots" : 0,
                    "short_handed_saves" : 0,
                    "short_handed_shots" : 0,
                    "goals" : 0,
                    "even_goals" : 0,
                    "power_play_goals" : 0,
                    "short_handed_goals" : 0,
                    "empty_net_goals" : 0,
                    "4-on-4_goals" : 0,
                    "3-on-3_goals" : 0,
                    "assists" : 0,
                    "primary_assist" : 0,
                    "secondary_assist" : 0,
                    "even_assists_primary" : 0,
                    "power_play_assists_primary" : 0,
                    "short_handed_assists_primary" : 0,
                    "empty_net_assists_primary" : 0,
                    "4-on-4_assists_primary" : 0,
                    "3-on-3_assists_primary" : 0,
                    "even_assists_secondary" : 0,
                    "power_play_assists_secondary" : 0,
                    "short_handed_assists_secondary" : 0,
                    "empty_net_assists_secondary" : 0,
                    "4-on-4_assists_secondary" : 0,
                    "3-on-3_assists_secondary" : 0,
                    "plus_minus" : int(players_by_id[player_id]["plusMinus"]),
                    "penalty_minutes" : 0,
                    "penalty_minutes_drawn" : 0,
                    "hits" : 0,
                    "hits_taken" : 0,
                    "takeaways" : 0,
                    "giveaways" : 0,
                    "blocks" : 0,
                    "blocked_shots" : 0,
                    "missed_shots" : 0,
                    "shots_on_goal" : 0,
                    "faceoff_wins" : 0,
                    "faceoff_attempts" : 0,
                    "time_on_ice" : players_by_id[player_id]["toi"],
                }
        else:
            if player["positionCode"] == "G":
                game_stats[away_team]["player_stats"][player_id] = {
                    "player_name" : player["firstName"]["default"] + " " +\
                        player["lastName"]["default"],
                    "player_position" : player["positionCode"],
                    "even_saves" :
                        int(players_by_id[player_id]
                            ["evenStrengthShotsAgainst"].split("/")[0]),
                    "even_shots" :
                        int(players_by_id[player_id]
                            ["evenStrengthShotsAgainst"].split("/")[1]),
                    "power_play_saves" :
                        int(players_by_id[player_id]
                            ["powerPlayShotsAgainst"].split("/")[0]),
                    "power_play_shots" :
                        int(players_by_id[player_id]
                            ["powerPlayShotsAgainst"].split("/")[1]),
                    "short_handed_saves" :
                        int(players_by_id[player_id]
                            ["shorthandedShotsAgainst"].split("/")[0]),
                    "short_handed_shots" :
                        int(players_by_id[player_id]
                            ["shorthandedShotsAgainst"].split("/")[1]),
                    "goals" : 0,
                    "even_goals" : 0,
                    "power_play_goals" : 0,
                    "short_handed_goals" : 0,
                    "empty_net_goals" : 0,
                    "4-on-4_goals" : 0,
                    "3-on-3_goals" : 0,
                    "assists" : 0,
                    "primary_assist" : 0,
                    "secondary_assist" : 0,
                    "even_assists_primary" : 0,
                    "power_play_assists_primary" : 0,
                    "short_handed_assists_primary" : 0,
                    "empty_net_assists_primary" : 0,
                    "4-on-4_assists_primary" : 0,
                    "3-on-3_assists_primary" : 0,
                    "even_assists_secondary" : 0,
                    "power_play_assists_secondary" : 0,
                    "short_handed_assists_secondary" : 0,
                    "empty_net_assists_secondary" : 0,
                    "4-on-4_assists_secondary" : 0,
                    "3-on-3_assists_secondary" : 0,
                    "plus_minus" : 0,
                    "penalty_minutes" : 0,
                    "penalty_minutes_drawn" : 0,
                    "hits" : 0,
                    "hits_taken" : 0,
                    "takeaways" : 0,
                    "giveaways" : 0,
                    "blocks" : 0,
                    "blocked_shots" : 0,
                    "missed_shots" : 0,
                    "shots_on_goal" : 0,
                    "faceoff_wins" : 0,
                    "faceoff_attempts" : 0,
                    "time_on_ice" : players_by_id[player_id]["toi"],
                }
            else:
                game_stats[away_team]["player_stats"][player_id] = {
                    "player_name" : player["firstName"]["default"] + " " +\
                        player["lastName"]["default"],
                    "player_position" : player["positionCode"],
                    "even_saves" : 0,
                    "even_shots" : 0,
                    "power_play_saves" : 0,
                    "power_play_shots" : 0,
                    "short_handed_saves" : 0,
                    "short_handed_shots" : 0,
                    "goals" : 0,
                    "even_goals" : 0,
                    "power_play_goals" : 0,
                    "short_handed_goals" : 0,
                    "empty_net_goals" : 0,
                    "4-on-4_goals" : 0,
                    "3-on-3_goals" : 0,
                    "assists" : 0,
                    "primary_assist" : 0,
                    "secondary_assist" : 0,
                    "even_assists_primary" : 0,
                    "power_play_assists_primary" : 0,
                    "short_handed_assists_primary" : 0,
                    "empty_net_assists_primary" : 0,
                    "4-on-4_assists_primary" : 0,
                    "3-on-3_assists_primary" : 0,
                    "even_assists_secondary" : 0,
                    "power_play_assists_secondary" : 0,
                    "short_handed_assists_secondary" : 0,
                    "empty_net_assists_secondary" : 0,
                    "4-on-4_assists_secondary" : 0,
                    "3-on-3_assists_secondary" : 0,
                    "plus_minus" : int(players_by_id[player_id]["plusMinus"]),
                    "penalty_minutes" : 0,
                    "penalty_minutes_drawn" : 0,
                    "hits" : 0,
                    "hits_taken" : 0,
                    "takeaways" : 0,
                    "giveaways" : 0,
                    "blocks" : 0,
                    "blocked_shots" : 0,
                    "missed_shots" : 0,
                    "shots_on_goal" : 0,
                    "faceoff_wins" : 0,
                    "faceoff_attempts" : 0,
                    "time_on_ice" : players_by_id[player_id]["toi"],
                }

    # now we go through each play in the play-by-play data and get other stats
    game_stats = parse_play_by_play_data(game, game_stats)

    # now go through all the plays of the game and get the accumulated stats
    return game_stats


def parse_web_match_data(game_date : str="") -> list:
    game_ids = []
    game_data = []

    # get a list of all games for the date to get the ids
    game_list = \
        "https://api-web.nhle.com/v1/score/" + game_date
    game_list_web_data = requests.get(game_list)
    game_list_parsed_data = json.loads(game_list_web_data.content)
    for game in game_list_parsed_data["games"]:
        game_ids.append(game["id"])

    # now that we have the id list, we can get the play-by-play data
    raw_game_stats = []
    for id in game_ids:
        play_by_play_list = "https://api-web.nhle.com/v1/gamecenter/" + \
            str(id) + "/play-by-play"
        try:
            play_by_play_list_web_data = requests.get(play_by_play_list)
        except Exception:
            play_by_play_list_web_data = requests.get(play_by_play_list)
        play_by_play_list_parsed_data = json.loads(
            play_by_play_list_web_data.content)
        box_score_list = "https://api-web.nhle.com/v1/gamecenter/" + \
            str(id) + "/boxscore"
        try:
            box_score_list_web_data = requests.get(box_score_list)
        except Exception:
            box_score_list_web_data = requests.get(box_score_list)
        box_score_list_parsed_data = json.loads(
            box_score_list_web_data.content)
        raw_game_stats.append({
            "play_by_play" : play_by_play_list_parsed_data,
            "box_score" : box_score_list_parsed_data
        })
        
    # now we have all the games as play-by-play data. run through each game and
    # create a dict of all used data
    for game in raw_game_stats:
        game_stats = collect_game_stats(game)
        game_stats['date'] = game_date
        game_data.append({"date" : game_date, "game_stats" : game_stats})
    return game_data


def worker_node(input_queue : Queue=None, output_queue : Queue=None) -> None:
    i = 0
    for func, arg_list in iter(input_queue.get, 'STOP'):
        output_queue.put(func(*arg_list))
        i += 1
    output_queue.put('STOP')


def get_game_records(season_year_id : str="") -> None:
    regular_season_matches = {}
    playoff_matches = {}
    upcoming_matches = {}
    upcoming_playoff_matches = {}

    # parse the start year from the season id
    start_year = int(str(season_year_id)[0:4])
    current_date = datetime.datetime.now(pytz.timezone('US/Pacific')).date()
    start_date = datetime.datetime(start_year,10,1,0,0,0).date()
    end_date = datetime.datetime(start_year+1,6,1,0,0,0).date()

    # indicates we are past the regular season so move the end date to June
    # just as a catch all to make sure we get all postseason games
    if end_date < current_date:
        end_date = datetime.datetime(current_date.year, 6, 1, 12, 0, 0, 0,
            pytz.timezone('US/Pacific')).date()
    else:
        end_date = current_date + datetime.timedelta(days=7)

    # create a list of all dates between now and season end
    dates = pandas.date_range(start_date, end_date).to_pydatetime().tolist()
    # dates = dates[0:30]
    i = 0
    for date in dates:
        dates[i] = date.strftime("%Y-%m-%d")
        i += 1
    match_parser_process_list = []
    subprocess_count = 32
    for i in range(subprocess_count):
        match_parser_process_list.append(Process(target=worker_node,
            args=(database_parser_input_queue, database_parser_output_queue))
        )
    for process in match_parser_process_list:
        process.start()

    # matches are orginized by date they take place
    total_dates = len(dates)
    parsed_dates = 0
    for date in dates:

        # for each game on a specific date loop through
        database_parser_input_queue.put((parse_web_match_data, ([date])))
    for i in range(subprocess_count):
        database_parser_input_queue.put('STOP')
    for i in range(subprocess_count):
        for output_list in iter(database_parser_output_queue.get, 'STOP'):

            # if the date had no games skip to the next date
            if not(len(output_list) > 0):
                continue

            # get the date from the game content as the metadata is removed
            # in parsing from the top level
            parsed_date = output_list[0]['date'].split("-")
            parsed_date = datetime.date(int(parsed_date[0]),
                int(parsed_date[1]), int(parsed_date[2]))

            # cycle through all games on this date
            # print(output_list[0]['date'])
            total_games = len(output_list)
            removed_games = 0
            counted_games = 0
            game_index = 0
            while (counted_games + removed_games) < total_games:
                game = output_list[game_index]

                # if the game is preseason or show match remove
                if (game['game_stats']['game_type'] != 2 and
                    game['game_stats']['game_type'] != 3):
                    output_list.remove(game)
                    removed_games += 1

                # if the game is regular season and already played
                elif ((parsed_date < current_date) and
                    (game['game_stats']['game_type'] == 2) and
                    (game['game_stats']['game_state'] == 'OFF')):
                    regular_season_matches[output_list[0]['date']] = \
                            output_list
                    counted_games += 1
                    game_index += 1

                # if the game is regular seaason upcoming
                elif ((parsed_date >= current_date) and
                    (game['game_stats']['game_type'] == 2) and
                    (game['game_stats']['game_state'] == 'FUT')):
                    upcoming_matches[output_list[0]['date']] = output_list
                    counted_games += 1
                    game_index += 1

                # if the game is postseason already played
                elif ((parsed_date < current_date) and
                    (game['game_stats']['game_type'] == 3) and
                    (game['game_stats']['game_state'] == 'OFF')):
                    playoff_matches[output_list[0]['date']] = output_list
                    counted_games += 1
                    game_index += 1

                # if the game is an upcoming playoff match
                elif ((parsed_date >= current_date) and
                    (game['game_stats']['game_type'] == 3) and
                    (game['game_stats']['game_state'] == 'FUT')):
                    upcoming_playoff_matches[output_list[0]['date']] = \
                        output_list
                    counted_games += 1
                    game_index += 1

                else:
                    print(game['game_stats']['game_type'])
                    print(game['game_stats']['game_state'])
                    output_list.remove(game)
                    removed_games += 1
            parsed_dates += 1
            update_progress_text(
                "Gathering All Match Data: {}/{}".format(
                    parsed_dates, total_dates)
            )
            update_progress_bar((parsed_dates / total_dates)*100)

    # we are done with all the data so just set the progress to 100 in case of
    # small rounding mismatch
    update_progress_bar(100)

    # close all parser processes
    for process in match_parser_process_list:
        process.join()

    return (regular_season_matches, upcoming_matches, playoff_matches,
        upcoming_playoff_matches)
