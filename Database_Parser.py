from multiprocessing import Process, Queue, freeze_support
import requests
import json
import pandas
import datetime
import pytz


database_parser_input_queue = Queue()
database_parser_output_queue = Queue()


def parse_play_by_play_penalties(home_team : str="", away_team : str="",
    play : dict={}, game_stats : dict={}) -> dict:

    # commited penalties
    if "committedByPlayerId" in play["details"].keys():
        if play["details"]["committedByPlayerId"] in \
            game_stats[home_team]["player_stats"]:
            game_stats[home_team]["player_stats"]\
                [play["details"]["committedByPlayerId"]]\
                ["penalty_minutes"] += play["details"]["duration"]
        elif play["details"]["committedByPlayerId"] in \
            game_stats[away_team]["player_stats"]:
            game_stats[away_team]["player_stats"]\
                [play["details"]["committedByPlayerId"]]\
                ["penalty_minutes"] += play["details"]["duration"]
        else:
            print("Penalties Commited Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["committedByPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())

    # drawn penalties
    if "drawnByPlayerId" in play["details"].keys():
        if play["details"]["drawnByPlayerId"] in \
            game_stats[home_team]["player_stats"]:
            game_stats[home_team]["player_stats"]\
                [play["details"]["drawnByPlayerId"]]\
                ["penalty_minutes_drawn"] += play["details"]["duration"]

        elif play["details"]["drawnByPlayerId"] in \
            game_stats[away_team]["player_stats"]:
            game_stats[away_team]["player_stats"]\
                [play["details"]["drawnByPlayerId"]]\
                ["penalty_minutes_drawn"] += play["details"]["duration"]
        
        else:
            print("Penalties Drawn By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["drawnByPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())
    return game_stats


def parse_play_by_play_hits(home_team : str="", away_team : str="",
    play : dict={}, game_stats : dict={}) -> dict:

    # hits delivered
    if play["details"]["hittingPlayerId"] in \
        game_stats[home_team]["player_stats"]:
        game_stats[home_team]["player_stats"]\
            [play["details"]["hittingPlayerId"]]\
            ["hits"] += 1
    elif play["details"]["hittingPlayerId"] in \
        game_stats[away_team]["player_stats"]:
        game_stats[away_team]["player_stats"]\
            [play["details"]["hittingPlayerId"]]\
            ["hits"] += 1
    else:
        print("Hits Delivered By Player\n" + 
            "Player Id Not in Either Teams Roster:",
            play["details"]["hittingPlayerId"])
        print(game_stats[home_team]["player_stats"].keys())

    # hits taken
    if play["details"]["hitteePlayerId"] in \
        game_stats[home_team]["player_stats"]:
        game_stats[home_team]["player_stats"]\
            [play["details"]["hitteePlayerId"]]\
            ["hits_taken"] += 1
    elif play["details"]["hitteePlayerId"] in \
        game_stats[away_team]["player_stats"]:
        game_stats[away_team]["player_stats"]\
            [play["details"]["hitteePlayerId"]]\
            ["hits_taken"] += 1
    else:
        print("Hits Recieved By Player\n" + 
            "Player Id Not in Either Teams Roster:",
            play["details"]["hitteePlayerId"])
        print(game_stats[home_team]["player_stats"].keys())
    return game_stats


def parse_play_by_play_takeaways_and_giveaways(home_team : str="", 
    away_team : str="", play : dict={}, game_stats : dict={}) -> dict:
    play_type = play["typeDescKey"]

    # takeaways
    if play_type == "takeaway":
        if play["details"]["playerId"] in \
            game_stats[home_team]["player_stats"]:
            game_stats[home_team]["player_stats"]\
                [play["details"]["playerId"]]\
                ["takeaways"] += 1
        elif play["details"]["playerId"] in \
            game_stats[away_team]["player_stats"]:
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
        if play["details"]["playerId"] in \
            game_stats[home_team]["player_stats"]:
            game_stats[home_team]["player_stats"]\
                [play["details"]["playerId"]]\
                ["giveaways"] += 1
        elif play["details"]["playerId"] in \
            game_stats[away_team]["player_stats"]:
            game_stats[away_team]["player_stats"]\
                [play["details"]["playerId"]]\
                ["giveaways"] += 1
        else:
            print("Giveawayw By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["playerId"])
            print(game_stats[home_team]["player_stats"].keys())
    return game_stats


def parse_play_by_play_shots(home_team : str="", away_team : str="",
    play : dict={}, game_stats : dict={}) -> dict:
    play_type = play["typeDescKey"]

    # blocked shots
    if play_type == "blocked-shot":

        # shots blocked
        if "blockingPlayerId" in play["details"].keys():
            if play["details"]["blockingPlayerId"] in \
                game_stats[home_team]["player_stats"]:
                game_stats[home_team]["player_stats"]\
                    [play["details"]["blockingPlayerId"]]\
                    ["blocks"] += 1
            elif play["details"]["blockingPlayerId"] in \
                game_stats[away_team]["player_stats"]:
                game_stats[away_team]["player_stats"]\
                    [play["details"]["blockingPlayerId"]]\
                    ["blocks"] += 1
            else:
                print("Shot-Block By Player\n" + 
                    "Player Id Not in Either Teams Roster:",
                    play["details"]["blockingPlayerId"])
                print(game_stats[home_team]["player_stats"].keys())

        # own shots blocked
        if "shootingPlayerId" in play["details"].keys():
            if play["details"]["shootingPlayerId"] in \
                game_stats[home_team]["player_stats"]:
                game_stats[home_team]["player_stats"]\
                    [play["details"]["shootingPlayerId"]]\
                    ["blocked_shots"] += 1
            elif play["details"]["shootingPlayerId"] in \
                game_stats[away_team]["player_stats"]:
                game_stats[away_team]["player_stats"]\
                    [play["details"]["shootingPlayerId"]]\
                    ["blocked_shots"] += 1
            else:
                print("Own Shot Blocked By Player\n" + 
                    "Player Id Not in Either Teams Roster:",
                    play["details"]["shootingPlayerId"])
                print(game_stats[home_team]["player_stats"].keys())
    
    # missed shot
    if play_type == "missed-shot":
        if "shootingPlayerId" in play["details"].keys():
            if play["details"]["shootingPlayerId"] in \
                game_stats[home_team]["player_stats"]:
                game_stats[home_team]["player_stats"]\
                    [play["details"]["shootingPlayerId"]]\
                    ["missed_shots"] += 1
            elif play["details"]["shootingPlayerId"] in \
                game_stats[away_team]["player_stats"]:
                game_stats[away_team]["player_stats"]\
                    [play["details"]["shootingPlayerId"]]\
                    ["missed_shots"] += 1
            else:
                print("Missed Shot By Player\n" + 
                    "Player Id Not in Either Teams Roster:",
                    play["details"]["shootingPlayerId"])
                print(game_stats[home_team]["player_stats"].keys())
            
    if play_type == "shot-on-goal":
        if "shootingPlayerId" in play["details"].keys():
            if play["details"]["shootingPlayerId"] in \
                game_stats[home_team]["player_stats"]:
                game_stats[home_team]["player_stats"]\
                    [play["details"]["shootingPlayerId"]]\
                    ["shots_on_goal"] += 1
            elif play["details"]["shootingPlayerId"] in \
                game_stats[away_team]["player_stats"]:
                game_stats[away_team]["player_stats"]\
                    [play["details"]["shootingPlayerId"]]\
                    ["shots_on_goal"] += 1
            else:
                print("Shot By Player\n" + 
                    "Player Id Not in Either Teams Roster:",
                    play["details"]["shootingPlayerId"])
                print(game_stats[home_team]["player_stats"].keys())
    return game_stats


def parse_play_by_play_faceoffs(home_team : str="", away_team : str="",
    play : dict={}, game_stats : dict={}) -> dict:

    # losing player just gets an attempts
    if play["details"]["losingPlayerId"] in \
        game_stats[home_team]["player_stats"]:
        game_stats[home_team]["player_stats"]\
            [play["details"]["losingPlayerId"]]\
            ["faceoff_attempts"] += 1
    elif play["details"]["losingPlayerId"] in \
            game_stats[away_team]["player_stats"]:
        game_stats[away_team]["player_stats"]\
            [play["details"]["losingPlayerId"]]\
            ["faceoff_attempts"] += 1
    else:
        print("Faceoff Lost By Player\n" + 
            "Player Id Not in Either Teams Roster:",
            play["details"]["shootingPlayerId"])
        print(game_stats[home_team]["player_stats"].keys())
        
    # winning player gets a win and an attempts
    if play["details"]["winningPlayerId"] in \
        game_stats[home_team]["player_stats"]:
        game_stats[home_team]["player_stats"]\
            [play["details"]["winningPlayerId"]]\
            ["faceoff_attempts"] += 1
        game_stats[home_team]["player_stats"]\
            [play["details"]["winningPlayerId"]]\
            ["faceoff_wins"] += 1
    elif play["details"]["winningPlayerId"] in \
            game_stats[away_team]["player_stats"]:
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
    return game_stats


def parse_play_by_play_goal(home_team : str="", away_team : str="",
    play : dict={}, game_stats : dict={}) -> dict:

    home_goalie_in = bool(int(play["situationCode"][0]))
    away_goalie_in = bool(int(play["situationCode"][3]))
    home_strength = int(play["situationCode"][1])
    away_strength = int(play["situationCode"][2])

    # home shorthanded
    if ((home_goalie_in and away_goalie_in) and home_strength < away_strength) \
        or ((not home_goalie_in) and home_strength <= away_strength):

        # home team player
        if play["details"]["scoringPlayerId"] in \
            game_stats[home_team]["player_stats"]:

            # goal
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["short_handed_goals"] += 1
            game_stats[home_team]["team_stats"]['short_handed_goals'] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["goals"] += 1
            game_stats[home_team]["team_stats"]['goals'] += 1
            
            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["short_handed_assists_primary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1
                
            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["short_handed_assists_secondary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1
                
        # away team player
        elif play["details"]["scoringPlayerId"] in \
            game_stats[away_team]["player_stats"]:

            # goal
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["power_play_goals"] += 1
            game_stats[home_team]["team_stats"]['power_play_goals'] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["goals"] += 1
            game_stats[away_team]["team_stats"]['goals'] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["power_play_assists_primary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["power_play_assists_secondary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1
        else:
            print("Shorthanded Goal By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["scoringPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())
    
    # away shorthanded
    elif ((home_goalie_in and away_goalie_in) and away_strength < home_strength) \
        or ((not away_goalie_in) and away_strength <= home_strength):

        # away team player
        if play["details"]["scoringPlayerId"] in \
            game_stats[away_team]["player_stats"]:

            # goal
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["short_handed_goals"] += 1
            game_stats[away_team]["team_stats"]['short_handed_goals'] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["goals"] += 1
            game_stats[away_team]["team_stats"]['goals'] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["short_handed_assists_primary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["short_handed_assists_secondary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1

        # home team player
        elif play["details"]["scoringPlayerId"] in \
            game_stats[home_team]["player_stats"]:

            # goal
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["power_play_goals"] += 1
            game_stats[home_team]["team_stats"]['power_play_goals'] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["goals"] += 1
            game_stats[home_team]["team_stats"]['goals'] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["power_play_assists_primary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["power_play_assists_secondary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1
        else:
            print("Shorthanded Goal By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["scoringPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())

    # empty net goals
    elif (not home_goalie_in):

        # away team player
        if play["details"]["scoringPlayerId"] in \
            game_stats[away_team]["player_stats"]:

            # goal
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["empty_net_goals"] += 1
            game_stats[away_team]["team_stats"]["empty_net_goals"] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["goals"] += 1
            game_stats[away_team]["team_stats"]['goals'] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["empty_net_assists_primary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["empty_net_assists_secondary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1
        else:
            pass
    elif (not away_goalie_in):

        # home team player
        if play["details"]["scoringPlayerId"] in \
            game_stats[home_team]["player_stats"]:

            # goal
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["empty_net_goals"] += 1
            game_stats[home_team]["team_stats"]["empty_net_goals"] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["goals"] += 1
            game_stats[home_team]["team_stats"]['goals'] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["empty_net_assists_primary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["empty_net_assists_secondary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1
        else:
            pass

    # 4-on-4
    elif (home_strength == 4 and away_strength == 4):

        # home team player
        if play["details"]["scoringPlayerId"] in \
            game_stats[home_team]["player_stats"]:

            # goal
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["4-on-4_goals"] += 1
            game_stats[home_team]["team_stats"]["4-on-4_goals"] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["goals"] += 1
            game_stats[home_team]["team_stats"]['goals'] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["4-on-4_assists_primary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["4-on-4_assists_secondary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1

        # away team player
        elif play["details"]["scoringPlayerId"] in \
            game_stats[away_team]["player_stats"]:

            # goal
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["4-on-4_goals"] += 1
            game_stats[away_team]["team_stats"]["4-on-4_goals"] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["goals"] += 1
            game_stats[away_team]["team_stats"]['goals'] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["4-on-4_assists_primary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["4-on-4_assists_secondary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1
        else:
            print("4-on-4 Goal By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["scoringPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())

    # 3-on-3
    elif (home_strength == 3 and away_strength == 3):

        # home team player
        if play["details"]["scoringPlayerId"] in \
            game_stats[home_team]["player_stats"]:

            # goal
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["3-on-3_goals"] += 1
            game_stats[home_team]["team_stats"]["3-on-3_goals"] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["goals"] += 1
            game_stats[home_team]["team_stats"]['goals'] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["3-on-3_assists_primary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["3-on-3_assists_secondary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1

        # away team player
        elif play["details"]["scoringPlayerId"] in \
            game_stats[away_team]["player_stats"]:

            # goal
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["3-on-3_goals"] += 1
            game_stats[away_team]["team_stats"]["3-on-3_goals"] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["goals"] += 1
            game_stats[away_team]["team_stats"]['goals'] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["3-on-3_assists_primary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["3-on-3_assists_secondary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1
        else:
            print("3-on-3 Goal By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["scoringPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())

    # even strength
    else:

        # home team player
        if play["details"]["scoringPlayerId"] in \
            game_stats[home_team]["player_stats"]:

            # goal
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["even_goals"] += 1
            game_stats[home_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["goals"] += 1
            game_stats[home_team]["team_stats"]['goals'] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["even_assists_primary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[home_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["even_assists_secondary"] += 1
                game_stats[home_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1

        # away team player
        elif play["details"]["scoringPlayerId"] in \
            game_stats[away_team]["player_stats"]:

            # goal
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["even_goals"] += 1
            game_stats[away_team]["player_stats"]\
                [play["details"]["scoringPlayerId"]]\
                ["goals"] += 1
            game_stats[away_team]["team_stats"]['goals'] += 1

            # assist1
            if "assist1PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist1PlayerId"]]\
                    ["even_assists_primary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1

            # assist2
            if "assist2PlayerId" in play["details"].keys():
                game_stats[away_team]["player_stats"]\
                    [play["details"]["assist2PlayerId"]]\
                    ["even_assists_secondary"] += 1
                game_stats[away_team]["player_stats"]\
                    [play["details"]["scoringPlayerId"]]\
                    ["assists"] += 1
        else:
            print("Goal By Player\n" + 
                "Player Id Not in Either Teams Roster:",
                play["details"]["scoringPlayerId"])
            print(game_stats[home_team]["player_stats"].keys())


def parse_play_by_play_data(game_data : dict={}, game_stats : dict={}) -> dict:
    home_team = game_data["box_score"]["homeTeam"]["name"]["default"]
    away_team = game_data["box_score"]["awayTeam"]["name"]["default"]

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
    home_team = game["box_score"]["homeTeam"]["name"]["default"]
    away_team = game["box_score"]["awayTeam"]["name"]["default"]
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
            home_team : {
                "team_stats" : {
                    "goals" : 0,
                    "empty_net_goals" : 0,
                    "4-on-4_goals" : 0,
                    "3-on-3_goals" : 0,
                    "first_period_goals" :
                        int(game["box_score"]["summary"]["linescore"]
                            ["byPeriod"][0]["home"]),
                    "second_period_goals" :
                        int(game["box_score"]["summary"]["linescore"]
                            ["byPeriod"][1]["home"]),
                    "third_period_goals" :
                        int(game["box_score"]["summary"]["linescore"]
                            ["byPeriod"][2]["home"]),
                    "OT_goals" : 0,
                    "SO_goals" : 0,
                    "shots" : int(game["box_score"]["homeTeam"]["sog"]),
                    "power_play_goals" :
                        int(game["box_score"]["summary"]["teamGameStats"][2][
                            "homeValue"].split("/")[0]),
                    "power_play_chances" : 
                        int(game["box_score"]["summary"]["teamGameStats"][2][
                            "homeValue"].split("/")[1]),
                    "short_handed_goals" : 0,
                    "short_handed_chances" : 
                        int(game["box_score"]["summary"]["teamGameStats"][2][
                            "awayValue"].split("/")[1]),
                    "penalty_minutes" : int(game["box_score"]["summary"][
                        "teamGameStats"][4]["homeValue"]),
                    "penalties_drawn" : int(game["box_score"]["summary"][
                        "teamGameStats"][4]["awayValue"]),
                    "hits" : int(game["box_score"]["summary"][
                        "teamGameStats"][5]["homeValue"]),
                    "getting_hit" : int(game["box_score"]["summary"][
                        "teamGameStats"][5]["awayValue"]),
                    "blocks" : int(game["box_score"]["summary"][
                        "teamGameStats"][6]["homeValue"]),
                    "blocked_shots" : int(game["box_score"]["summary"][
                        "teamGameStats"][6]["awayValue"]),
                },
                "player_stats" : {}
            },
            away_team : {
                "team_stats" : {
                    "goals" : 0,
                    "empty_net_goals" : 0,
                    "4-on-4_goals" : 0,
                    "3-on-3_goals" : 0,
                    "first_period_goals" :
                        int(game["box_score"]["summary"]["linescore"]
                            ["byPeriod"][0]["away"]),
                    "second_period_goals" :
                        int(game["box_score"]["summary"]["linescore"]
                            ["byPeriod"][1]["away"]),
                    "third_period_goals" :
                        int(game["box_score"]["summary"]["linescore"]
                            ["byPeriod"][2]["away"]),
                    "OT_goals" : 0,
                    "SO_goals" : 0,
                    "shots" : int(game["box_score"]["awayTeam"]["sog"]),
                    "power_play_goals" :
                        int(game["box_score"]["summary"]["teamGameStats"][2][
                            "awayValue"].split("/")[0]),
                    "power_play_chances" : 
                        int(game["box_score"]["summary"]["teamGameStats"][2][
                            "awayValue"].split("/")[1]),
                    "short_handed_goals" : 0,
                    "short_handed_chances" : 
                        int(game["box_score"]["summary"]["teamGameStats"][2][
                            "homeValue"].split("/")[1]),
                    "penalty_minutes" : int(game["box_score"]["summary"][
                        "teamGameStats"][4]["awayValue"]),
                    "penalties_drawn" : int(game["box_score"]["summary"][
                        "teamGameStats"][4]["homeValue"]),
                    "hits" : int(game["box_score"]["summary"][
                        "teamGameStats"][5]["awayValue"]),
                    "getting_hit" : int(game["box_score"]["summary"][
                        "teamGameStats"][5]["homeValue"]),
                    "blocks" : int(game["box_score"]["summary"][
                        "teamGameStats"][6]["awayValue"]),
                    "blocked_shots" : int(game["box_score"]["summary"][
                        "teamGameStats"][6]["homeValue"]),
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
    if game_stats["result"] in ["OT", "SO"]:
        game_stats[home_team]["OT_goals"] = \
            int(game["box_score"]["summary"]["linescore"]
                            ["byPeriod"][3]["home"])
        game_stats[away_team]["OT_goals"] = \
            int(game["box_score"]["summary"]["linescore"]
                            ["byPeriod"][3]["away"])
    if game_stats["result"] == "SO":
        game_stats[home_team]["SO_goals"] = \
            int(game["box_score"]["summary"]["linescore"]
                            ["byPeriod"][4]["home"])
        game_stats[away_team]["SO_goals"] = \
            int(game["box_score"]["summary"]["linescore"]
                            ["byPeriod"][4]["away"])

    # create a flat list of players by id so we can reference stats from
    # the boxscore when looping through play-by-play
    list_of_players = \
        game["box_score"]["playerByGameStats"]["awayTeam"] \
            ["forwards"] + \
        game["box_score"]["playerByGameStats"]["awayTeam"] \
            ["defense"] + \
        game["box_score"]["playerByGameStats"]["awayTeam"] \
            ["goalies"] + \
        game["box_score"]["playerByGameStats"]["homeTeam"] \
            ["forwards"] + \
        game["box_score"]["playerByGameStats"]["homeTeam"] \
            ["defense"] + \
        game["box_score"]["playerByGameStats"]["homeTeam"] \
            ["goalies"]
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
                    "goals" : 0,
                    "even_goals" : 0,
                    "power_play_goals" : 0,
                    "short_handed_goals" : 0,
                    "empty_net_goals" : 0,
                    "4-on-4_goals" : 0,
                    "3-on-3_goals" : 0,
                    "assists" : 0,
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
                    "goals" : 0,
                    "even_goals" : 0,
                    "power_play_goals" : 0,
                    "short_handed_goals" : 0,
                    "empty_net_goals" : 0,
                    "4-on-4_goals" : 0,
                    "3-on-3_goals" : 0,
                    "assists" : 0,
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
        play_by_play_list_web_data = requests.get(play_by_play_list)
        play_by_play_list_parsed_data = json.loads(
            play_by_play_list_web_data.content)
        box_score_list = "https://api-web.nhle.com/v1/gamecenter/" + \
            str(id) + "/boxscore"
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

    # first get the list of all seasons to get the start and end date
    seasons = "https://api.nhle.com/stats/rest/en/season"
    seasons_web_data = requests.get(seasons)
    seasons_parsed_data = json.loads(seasons_web_data.content)

    # now we have to use the seasons list to get the specific dates of interest
    for season in seasons_parsed_data["data"]:
        if season["id"] == season_year_id:
            start_date = datetime.datetime.fromisoformat(
                    (season["startDate"] + ".00")[:-1]
                ).astimezone(datetime.timezone.utc).date()
            end_date = datetime.datetime.fromisoformat(
                    (season["regularSeasonEndDate"] + ".00")[:-1]
                ).astimezone(datetime.timezone.utc).date()
            break
    # TODO: we will have to find a way to update the end date to get the dates
    # for the post season too. If the season is over it has endDate, but if we
    # are parsing the currents season then it doesn't have that info

    # create a list of all dates between now and season end
    dates = pandas.date_range(start_date, end_date).to_pydatetime().tolist()
    # dates = dates[0:10]
    i = 0
    for date in dates:
        dates[i] = date.strftime("%Y-%m-%d")
        i += 1
    current_date = datetime.datetime.now(pytz.timezone('US/Pacific')).date()
    match_parser_process_list = []
    subprocess_count = 16
    for i in range(subprocess_count):
        match_parser_process_list.append(Process(target=worker_node,
            args=(database_parser_input_queue, database_parser_output_queue))
        )
    for process in match_parser_process_list:
        process.start()

    # matches are orginized by date they take place
    for date in dates:

        # for each game on a specific date loop through
        database_parser_input_queue.put((parse_web_match_data, ([date])))
    for i in range(subprocess_count):
        database_parser_input_queue.put('STOP')
    for i in range(subprocess_count):
        for output_list in iter(database_parser_output_queue.get, 'STOP'):
            if (output_list is not None) and (len(output_list) > 0):
                parsed_date = output_list[0]['date'].split("-")
                parsed_date = datetime.date(int(parsed_date[0]),
                    int(parsed_date[1]), int(parsed_date[2]))

                # if the date has already passed, then do post processing
                if output_list[0]['game_stats']["game_state"] == "OFF" and\
                    parsed_date < current_date:

                    # if regular season then put into that list of dates
                    if output_list[0]['game_stats']['game_type'] == 2:
                        if output_list[0]['game_stats']["game_state"] == "LIVE":
                            print("HOW THE FUCK IS THIS IN HERE")
                        regular_season_matches[output_list[0]['date']] = \
                            output_list

                    # otherwise put the date and all games into the playoff
                    # list of matches
                    elif output_list[0]['game_stats']['game_type'] == 3:
                        playoff_matches[output_list[0]['date']] = output_list

                # otherwise slate it for the prediction engine
                elif output_list[0]['game_stats']["game_state"] == "FUT":
                    if output_list[0]['game_stats']['game_type'] == 2:
                        upcoming_matches[output_list[0]['date']] = output_list
                    else:
                        upcoming_playoff_matches[output_list[0]['date']] = \
                            output_list

    # close all parser processes
    for process in match_parser_process_list:
        process.join()

    return (regular_season_matches, playoff_matches, upcoming_matches,
        upcoming_playoff_matches)
