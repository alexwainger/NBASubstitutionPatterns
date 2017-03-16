import sys
import csv
import urllib2
import requests
import re
from itertools import izip
from lxml import html, etree
from bs4 import BeautifulSoup
from bs4.element import Comment
from datetime import datetime
import time

class Player:

	def __init__(self, name, position):
		self.name = name;
		self.position = position;
		self.minutes_count = [0.0] * 48;
		self.games_count = 0;
		self.games_played = 0;
		self.games_started = 0;
		self.minutes_played = 0;

	def set_games_data(self, games_played, games_started, minutes_played):
		self.games_played = games_played;
		self.games_started = games_started;
		self.minutes_played = minutes_played;

	def add_minute_range(self, start_min, end_min):
		for i in range(start_min, end_min):
			if self.minutes_count[i] < self.games_count:
				self.minutes_count[i] += 1.0;

	def get_position_val(self):
		if "PG" in self.position:
			return 1;
		if "SG" in self.position:
			return 2;
		if "SF" in self.position:
			return 3;
		if "PF" in self.position:
			return 4;
		if "C" in self.position:
			return 5;

		print "Uh oh, no position for: " + self.name;
		return 0;

def generate_player_dictionary(team_page_link):
	player_dict = {};
	response = urllib2.urlopen("http://www.basketball-reference.com" + team_page_link).read();
	team_page = BeautifulSoup(response, 'lxml');
	roster_rows = team_page.find("table", {"id": "roster"}).find("tbody").findAll("tr");

	for player_row in roster_rows:
		player_name = player_row.find("td", {"data-stat": "player"}).find("a").text;
		if player_name == "Glenn Robinson III":
			player_name = "Glenn Robinson";
		elif player_name == "Nene":
			player_name = "Nene Hilario";
		elif player_name == "Taurean Prince":
			player_name = "Taurean Waller-Prince";
		elif player_name == "Kelly Oubre Jr.":
			player_name = "Kelly Oubre";

		position = player_row.find("td", {"data-stat": "pos"}).text;
		if player_name in player_dict:
			print 'Uh oh, we found a duplicate: ' + player_name +" on " + team_page_link;
		else:
			p = Player(player_name, position);
			player_dict[player_name] = p;

	comments = team_page.findAll(text=lambda text:isinstance(text, Comment))
	for comment in comments:
		comment_string = re.split("(?:<!--)|(?:-->)", comment)[0];
		comment_soup = BeautifulSoup(comment_string, "lxml");
		totals_table = comment_soup.find("table", {"id": "totals"});
		if totals_table:
			totals_rows = totals_table.find("tbody").findAll("tr");
			for totals_row in totals_rows:
				cols = totals_row.findAll("td");
				player_name = cols[0].find("a").text;

				if player_name not in player_dict:
					player_dict[player_name] = Player(player_name, "N/A");
					print "Adding ", player_name;

				p = player_dict[player_name];

				games_played = int(cols[2].find("a").text);
				games_started = int(cols[3].text);
				minutes_played = int(cols[4].text);

				p.set_games_data(games_played, games_started, minutes_played);

	return player_dict;

width_regex = re.compile("width:([0-9]+)px;");
def process_plus_minus(plus_minus_link, isHomeGame, num_overtimes, players):
	print plus_minus_link;
	try:
		response = urllib2.urlopen(urllib2.Request(plus_minus_link, headers={'User-Agent': 'Mozilla'})).read();
	except urllib2.HTTPError:
		return False
	pm_soup = BeautifulSoup(response, 'lxml');
	pm_div = pm_soup.find("div", {"class": "plusminus"});
	style_div =pm_div.find("div", recursive=False);

	total_width = int(width_regex.search(style_div['style']).group(1)) - 1;
	team_table = style_div.findAll("div", recursive=False)[isHomeGame];
	rows = team_table.findAll("div", recursive=False)[1:];

	total_minutes = 48.0 + (5.0 * num_overtimes);
	minute_width = total_width / total_minutes;
	for player_row, minutes_row in izip(*[iter(rows)] * 2):
		player_name = player_row.find('span').text;
		player_obj = players[player_name];
		player_obj.games_count += 1;
		curr_minute = 0.0;
		for bar in minutes_row.findAll('div'):
			if round(curr_minute) < 48:
				classes = bar.get('class');
				width = int(width_regex.search(bar.get('style')).group(1)) + 1;
				span_length = width / minute_width;

				if classes is not None and ("plus" in classes or "minus" in classes or "even" in classes):
					try:
						player_obj.add_minute_range(int(round(curr_minute)), int(round(curr_minute + span_length)));
					except IndexError:
						print player_name, curr_minute, span_length
						raise;

				curr_minute += span_length;

	return True

def main():

	today = datetime.now().date();
	years = ["2017"];

	for year in years:
		print "DOING YEAR " + year;
		link = "http://www.basketball-reference.com/leagues/NBA_" + year + ".html";
		response = urllib2.urlopen(urllib2.Request(link, headers={'User-Agent': 'Mozilla'})).read();
		season_summary = BeautifulSoup(response, 'lxml');
		comments = season_summary.findAll(text=lambda text:isinstance(text, Comment))
		for comment in comments:
			comment_string = re.split("(?:<!--)|(?:-->)", comment)[0];
			comment_soup = BeautifulSoup(comment_string, "lxml");
			team_stats = comment_soup.find("table", {"id": "team-stats-per_game"});
			if team_stats:
				team_names = team_stats.find("tbody").findAll("td", {"data-stat": "team_name"});
				for team_name in team_names:
					team_page_link = team_name.find("a")['href'];
					abr_regex = re.compile("^\/teams\/(.*)\/.*\.html");
					team_abr = abr_regex.search(team_page_link).group(1);

					players = generate_player_dictionary(team_page_link);
					schedule_link = "http://www.basketball-reference.com/teams/" + team_abr + "/" + year + "_games.html";
					response = urllib2.urlopen(urllib2.Request(schedule_link, headers={'User-Agent': 'Mozilla'})).read();
					schedule_soup = BeautifulSoup(response, 'lxml');
					game_rows = schedule_soup.find("table", {"id": "games"}).find("tbody").findAll("tr", {"class": None});
					print "Working on " + team_abr;
					gamesPlayed = 0.0;
					for game_row in game_rows:
						gameDate = datetime.strptime(game_row.find("td", {"data-stat": "date_game"})['csk'], "%Y-%m-%d").date();
						if gameDate >= today:
							print "Breaking due to date"
							break;
						else:
							game_link = game_row.find("td", {"data-stat": "box_score_text"}).find("a")['href'];
							gameID_regex = re.compile('^/boxscores/([^.]+).html');
							gameID = gameID_regex.search(game_link).group(1);

							isHomeGame = not game_row.find("td", {"data-stat": "game_location"}).text == "@"

							overtime_string = game_row.find("td", {"data-stat": "overtimes"}).text;
							num_overtimes = 0;
							if overtime_string:
								if overtime_string == "OT":
									num_overtimes = 1;
								else:
									num_overtimes = int(overtime_string[0]);
							plus_minus_link = "http://www.basketball-reference.com/boxscores/plus-minus/" + gameID + ".html";

							if not process_plus_minus(plus_minus_link, isHomeGame, num_overtimes, players):
								print "Breaking due to 404"
								break;

							gamesPlayed += 1.0;

					player_list = players.values();
					players_by_starts = sorted(player_list, key=lambda p: p.games_started, reverse=True);
					starters = sorted(players_by_starts[0:5], key=lambda p: p.get_position_val());
					bench = sorted(players_by_starts[5:], key=lambda p: p.minutes_played, reverse=True);

					with open("data/" + year + "/" + team_abr + ".csv", "wb") as f:
						writer = csv.writer(f);
						writer.writerow(["Name", "GamesPlayed", "MinutesPlayed"] + [str(x) for x in range(1,49)]);
						for player in starters + bench:
							writer.writerow([player.name, player.games_played, player.minutes_played] + [x / gamesPlayed for x in player.minutes_count] );


	original = [];
	with open("README.md", "rb") as readme_read: original = readme_read.readlines()[1:];
	with open("README.md", "wb") as readme_write: readme_write.write("".join(["_Last Data Update: " + ("{d:%B} {d.day}, {d.year}_\n").format(d = today)] + original))
	with open("data/last_update.txt", "wb") as last_update: last_update.write(("{d:%B} {d.day}, {d.year}\n").format(d = today));

if __name__ == "__main__":
	start_time = time.time();
	main()
	print("--- %s seconds ---" % (time.time() - start_time))
