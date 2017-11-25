#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Originally forked from John Freed's NHL-Scores - https://github.com/jtf323/NHL-Scores

from colorama import init, Fore, Style
from pytz import reference
import datetime
import json
import os
import platform
import sys
import time
import requests


REFRESH_TIME = 30  # Minimize delay by doubling the API refresh rate
API_URL = 'http://live.nhle.com/GameData/RegularSeasonScoreboardv3.jsonp'
TEST = False


def main():
    '''generates a scoreboard of current NHL games'''
    intermission_clock = 18.0
    games_today = False
    saw_period_end = True

    # Today's date
    t_object = datetime.datetime.now()
    today_date = "" + t_object.strftime("%A") + " " + "%s/%s" % (t_object.month, t_object.day)

    # Yesterday's date
    y_object = t_object - datetime.timedelta(days=1)
    yesterday_date = "" + y_object.strftime("%A") + " " + "%s/%s" % (y_object.month, y_object.day)

    # Current season
    season = str(t_object.year - 1) + str(t_object.year) + '/'

    while True:
        scraped_page = requests.get(API_URL)

        # Convert the scraped page to text and trim
        scraped_page = scraped_page.text.replace('loadScoreboard(', '')
        scraped_page = scraped_page[:-1]

        # Create JSON object
        data = json.loads(scraped_page)

        clear_screen()

        for key in data:
            if key == 'games':
                for game_info in data[key]:
                    game_id = str(game_info['id'])
                    game_clock = game_info['ts']
                    game_stage = game_info['tsc']
                    status = game_info['bs']

                    away_locale = fix_locale(game_info['atn'])
                    away_name = fix_name(game_info['atv']).title()
                    away_score = game_info['ats']
                    away_result = game_info['atc']

                    home_locale = fix_locale(game_info['htn'])
                    home_name = fix_name(game_info['htv']).title()
                    home_score = game_info['hts']
                    home_result = game_info['htc']

                    playoffs = False
                    series_game_number = game_id[-1:]

                    if game_id[4:6] == '03':
                        playoffs = True

                    # Show today's games
                    if today_date in game_clock.title() or 'TODAY' in game_clock or 'LIVE' in status:
                        games_today = True
                        header_text = away_locale + ' ' + away_name + \
                            ' @ ' + home_locale + ' ' + home_name

                        # Show the game number of current 7-game series,
                        # if it's playoff time
                        if playoffs:
                            header_text += ' -- Game ' + series_game_number

                        # Different displays for different states of game:
                        # Game from yesterday, ex: YESTERDAY (FINAL 2nd OT)
                        # Game from today finished, ex: TODAY (FINAL 2nd OT)
                        if 'FINAL' in status:
                            if yesterday_date in game_clock.title():
                                header_text += '\nYESTERDAY '
                            elif today_date in game_clock.title() or 'TODAY' in game_clock:
                                header_text += '\nTODAY '
                            else:
                                header_text += game_clock.title()
                            header_text += '(' + status + ')'

                        # Upcoming game, ex: TUESDAY 4/21, 7:00 PM MDT)
                        elif 'DAY' in game_clock and 'FINAL' not in status:
                            timezone = local_time()
                            header_text += Fore.YELLOW + \
                                '\n(' + game_clock + ', ' + status + \
                                ' ' + timezone + ')' + Fore.RESET

                        # Last 5 minutes of game and overtime, ex: (1:59 3rd
                        # PERIOD) *in red font*
                        elif 'LIVE' in status and 'critical' in game_stage:
                            saw_period_end = True
                            header_text += Fore.RED + \
                                '\n(' + game_clock + ' PERIOD)' + Fore.RESET
                            if 'END 3rd' in game_clock or 'OT' in game_clock:
                                intermission_clock = 15.0
                            print_intermission_clock(
                                header_text, intermission_clock)

                        # Any other time in game, ex: (10:34 1st PERIOD)
                        else:
                            header_text += Fore.YELLOW + \
                                '\n(' + game_clock + Style.RESET_ALL
                            if 'PRE GAME' not in game_clock:
                                saw_period_end = True
                                header_text += Fore.YELLOW + ' PERIOD'

                            # Display a countdown for 18 minutes of intermission (regular periods)
                            #     or 15 minutes of intermission (OVERTIME)
                            if 'END ' in game_clock and 'FINAL' not in status and saw_period_end:
                                if 'END 3rd' in game_clock or 'OT' in game_clock:
                                    intermission_clock = 15.0
                                print_intermission_clock(header_text, intermission_clock)

                            header_text += Fore.YELLOW + ')' + Style.RESET_ALL

                        print(header_text)

                        # Highlight the winner of finished games in blue, and games underway in green:
                        if away_result == 'winner':  # Away team wins
                            print(Style.BRIGHT + Fore.BLUE + away_name + ' ' + away_score + Style.RESET_ALL + ' - ' + home_score + ' ' + home_name)
                        elif home_result == 'winner':  # Home team wins
                            print(away_name + ' ' + away_score + ' - ' + Style.BRIGHT + Fore.BLUE + home_score + ' ' + home_name + Style.RESET_ALL)
                        elif 'progress' in game_stage or 'critical' in game_stage:  # Game still underway
                            print(Fore.GREEN + away_name + ' ' + away_score + ' - ' + home_score + ' ' + home_name + Fore.RESET)
                        # else:  # other
                        #     print(away_name + ' ' + away_score +
                        #           ' - ' + home_score + ' ' + home_name)
                        print('')
                    else:
                        print("\nThere are no NHL games scheduled for today.\n")
        # Perform the sleep if we're not currently testing
        if TEST is True:
            sys.exit(0)
        else:
            time.sleep(REFRESH_TIME)
            print("\n\n\n")


def clear_screen():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


def print_help():
    ''' response to the --help flag'''
    print 'By default games from yesterday and today will be displayed.'
    print ''


def parse_game_info(game_info):
    ''' assign more meaningful names'''
    parsed_list = {
        game_id:     str(game_info['id']),
        game_clock:  game_info['ts'],
        game_stage:  game_info['tsc'],
        status:      game_info['bs'],
        away_locale: game_info['atn'],
        away_name:   game_info['atv'].title(),
        away_score:  game_info['ats'],
        away_result: game_info['atc'],
        home_locale: game_info['htn'],
        home_name:   game_info['htv'].title(),
        home_score:  game_info['hts'],
        home_result: game_info['htc'],
    }
    return parsed_list


def get_address(game_id, season):
    prefix = 'http://live.nhle.com/GameData/'
    suffix = '/gc/gcsb.jsonp'
    game_url = prefix + season + str(game_id) + suffix

    return game_url


def fix_locale(team_locale):
    # NHL API forces team name in locale for both New York teams, i.e. locale
    # + name == "NY Islanders islanders"
    if 'NY ' in team_locale:
        return 'New York'
    #
    if 'Montr' in team_locale:
        return u'Montréal'

    return team_locale


def print_intermission_clock(header_text, intermission_clock):
    header_text += Fore.YELLOW + ', ' + \
        str(intermission_clock) + ' minutes remaining in the intermission'
    intermission_clock -= (REFRESH_TIME / 60.0)
    if intermission_clock < 0:
        if 'END 3rd' in game_clock or 'OT' in game_clock:
            intermission_clock = 15.0
        else:
            intermission_clock = 18.0
    return header_text


def fix_name(team_name):
    # Change "redwings" to "Red Wings"
    if 'wings' in team_name:
        return 'Red Wings'

    # Change "bluejackets" to "Blue Jackets"
    elif 'jackets' in team_name:
        return 'Blue Jackets'

    # Change "mapleleafs" to "Maple Leafs"
    elif 'leafs' in team_name:
        return 'Maple Leafs'

    # Change "goldenknights" to "Maple Leafs"
    elif 'knights' in team_name:
        return 'Golden Knights'

    return team_name


def print_schedule():
    for games in next_two_weeks:
        print away_locale + ' ' + away_name + ' @ ' + home_locale + ' ' + home_name
        print Fore.YELLOW + '(' + game_clock + ', ' + status + ' EDT)' + Fore.RESET
        print away_name + ' ' + away_score
        print home_name + ': ' + home_score
        print "\n"


def local_time():
    '''figure out local timezone'''
    today = datetime.datetime.now()
    localtime = reference.LocalTimezone()
    return localtime.tzname(today)


def parse_arguments(arguments):
    '''process the arguments provided at runtime'''
    for index in range(1, len(arguments)):
        argument = arguments[index]

        if argument == '--help' or argument == '-h':
            print_help()
            sys.exit(0)
        if argument == '--test' or argument == '-t':
            print "\nRunning in TEST mode.\n\n"
            global TEST
            TEST = True


if __name__ == '__main__':
    # Initialize Colorama
    init()

    # Parse any arguments provided
    parse_arguments(sys.argv)

    # Start the main loop
    main()

# The MIT License (MIT)

# Copyright (c) 2015 John Freed, Stevie Howard

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
