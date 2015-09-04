# Ticker [![Join the chat at https://gitter.im/stvhwrd/Ticker](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/stvhwrd/Ticker?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)  [![Build Status](https://travis-ci.org/stvhwrd/Ticker.svg?branch=master)](https://travis-ci.org/stvhwrd/Ticker)


A web scraper built with Python to display the score of current and recently finished NHL games.  The score is scraped directly from the NHL website every 30 seconds.  During intermissions (between periods), a countdown clock is displayed.

![Exhibit A](https://github.com/stvhwrd/Ticker/blob/master/Screenshots/IntermissionClock.png?raw=true)

## Requirements

* Python 2.7
    * `python --version`
* Requests
    * `pip install requests`
* Colorama
    * `pip install colorama`

## Usage
Once you've ensured that your system meets the requirements, open a terminal window and execute
`python /your/path/to/ticker.py`
<br>
<br>

Fly me a message on Gitter if you have any questions.

[![Join the chat at https://gitter.im/stvhwrd/Ticker](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/stvhwrd/Ticker?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

## Tested on

* OS X 10.10.3 with Python 2.7.9
* Windows 8.1 x64 with Python 2.7.9
* Ubuntu 14.04.2 LTS x64 with Python 2.7.6

## Goal
I hope to extend this ticker-type functionality to other sports leagues.  I plan to make the main script generic and then pull in header files for whichever specific league the user chooses at runtime.  Next league I'll implement will probably be MLB since their 162 games * 30 teams allows for a lot of live testing.

MLB livescore JSON at http://gd2.mlb.com/components/game/mlb/year_2015/month_08/day_02/master_scoreboard.json
NHL livescore JSON at http://live.nhle.com/GameData/RegularSeasonScoreboardv3.jsonp

## License

[MIT License](http://opensource.org/licenses/MIT)
