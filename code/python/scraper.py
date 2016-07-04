import csv
import urllib2
import requests
import re
from lxml import html
from bs4 import BeautifulSoup

class Player:

	def __init__(self, name, games_played, games_started, position):
		self.name = name;
		self.games_played = games_played;
		self.games_started = games_started;
		self.position = position;

	def get_position_val(self):
		val = 0.0;
		count = 0.0;
		if "Point Guard" in self.position:
			val += 1.0;
			count += 1.0;
		if "Shooting Guard" in self.position:
			val += 2.0;
			count += 1.0;
		if "Small Forward" in self.position:
			val += 3.0;
			count += 1.0;
		if "Power Forward" in self.position:
			val += 4.0;
			count += 1.0;
		if "Center" in self.position:
			val += 5.0;
			count += 1.0;

		return val / count;
	
	def get_starting_percentage(self):
		return self.games_started / self.games_played;


def generate_player_dictionary(team_page_link):
	player_dict = {};
	response = urllib2.urlopen("http://www.basketball-reference.com" + team_page_link).read();
	team_page = BeautifulSoup(response, 'lxml');
	total_table = team_page.find("table", {"id":"totals"});
	rows = total_table.find("tbody").findAll("tr", {"class":""});
	
	for player_row in rows:	
		cols = player_row.findAll("td");
		player_link = cols[1].find("a")["href"];
		
		player_page = urllib2.urlopen("http://www.basketball-reference.com" + player_link, 'lxml').read();
		
		# Get player position
		info_box = BeautifulSoup(player_page, 'lxml').find(id = 'info_box');
		player_info = info_box.find("p", {"class": "padding_bottom_half"});	
		position = player_info.contents[1].strip(u' \xa0\u25aa\xa0').encode('utf-8');

		# Get player name, # games started and played
		player_name = cols[1].find("a").contents[0];
		games_played = float(cols[3].find("a").contents[0]);
		games_started = float(cols[4].contents[0]);

		p = Player(player_name, games_played, games_started, position);
		
		if player_name in player_dict:
			print 'Uh oh, we found a duplicate: ' + player_name +" on " + team_page_link;
		else:
			player_dict[player_name] = p;

	return player_dict;

def main():

	years = ["2016"]#, "2015", "2014"];
	
	for year in years:
		season_summary = html.fromstring(requests.get("http://www.basketball-reference.com/leagues/NBA_" + year + ".html").content);
		for i in range(1, 31):
			abr_regex = re.compile("^\/teams\/(.*)\/.*\.html");
			team_page_link = season_summary.xpath('//*[@id="team"]/tbody/tr[' + str(i) + ']/td[2]/a/@href')[0];
			team_abr = abr_regex.search(team_page_link).group(1);

			players = generate_player_dictionary(team_page_link);
			print players;

			schedule_link = "http://www.basketball-reference.com/teams/" + team_abr + "/2016_games.html";
			schedule_page = html.fromstring(requests.get(schedule_link).content);

			## Loop through all the games the team played, parse the play-by-play
			for i in range(87):
				## Every 20 rows, there's a header row that we want to ignore
				if not (i % 21 == 0):
					link = schedule_page.xpath('//*[@id="teams_games"]/tbody/tr[' + str(i) + ']/td[5]/a/@href');
					gameID_regex = re.compile('^/boxscores/([^.]+).html');
					gameID = gameID_regex.search(link[0]).group(1);
					plus_minus_link = "http://www.basketball-reference.com/boxscores/plus-minus/" + gameID + ".html";


if __name__ == "__main__":
	main();
