$(document).ready(function() {
	var margin = { top: 20, right: 0, bottom: 0, left: 135 },
		width = 1200 - margin.left - margin.right,
		height = 550 - margin.top - margin.bottom,
		gridWidth = Math.floor(width / 48),
		gridHeight = gridWidth + 4,
		legendElementWidth = gridWidth*2,
		buckets = 5,
		colors = [];
		times = ["Q1", "Q2", "Q3", "Q4"],
		bins = [.1, .2, .3, .4, .5, .6, .7, .8, .9],
		datasets = ["data.tsv", "data2.tsv"];

	for (var i = .05; i < 1; i += .1) {
		console.log(i);
		colors.push(d3.interpolateYlOrRd(i));
	}

	var svg = d3.select("#heatmap").append("svg")
		.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.top + margin.bottom)
		.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
		
	var timeLabels = svg.selectAll(".timeLabel")
		.data(times)
		.enter().append("text")
		.text(function(d) { return d; })
		.attr("x", function(d, i) { return 12 * i * gridWidth; })
		.attr("y", 0)
		.style("text-anchor", "middle")
		.attr("transform", "translate(" + gridWidth / 2 + ", -6)");
		
	var colorScale = d3.scaleThreshold()
		.domain(bins)
		.range(colors);
	
	$("#go").click(drawHeatMap());

	function drawHeatMap() {
		team_abr = $("#team")[0].value;
		year = $("#year")[0].value;
		d3.csv("../data/" + year + "/" + team_abr + ".csv", function(d) {
			var toReturn = { name: d.Name, minutes: []};
			for (var i = 1; i < 49; i++) {
				toReturn.minutes.push(d[i]);
			}
			return toReturn;
		}, function(data) {
			var players = [];
			var minute_values = [];
			for (var i = 0; i < data.length; i++) {
				players.push(data[i].name);
				for (var j = 0; j < 48; j++) {
					minute_values.push(+data[i].minutes[j]);
				}
			}



			svg.selectAll(".playerLabel")
				.data(players)
				.enter().append("text")
				.text(function (d) { return d; })
				.attr("x", 0)
				.attr("y", function (d, i) { return i * gridHeight; })
				.style("text-anchor", "end")
				.attr("transform", "translate(-2," + gridHeight / 1.5 + ")");
	
	
			var cards = svg.selectAll(".minute")
				.data(minute_values);
	
			cards.append("title");
	
			cards.enter().append("rect")
				.attr("x", function(d, i) { return (i % 48) * gridWidth; })
				.attr("y", function(d, i) { return Math.floor(i / 48) * gridHeight; })
				.attr("rx", 4)
				.attr("ry", 4)
				.attr("width", gridWidth)
				.attr("height", gridHeight)
				.attr("class", "bordered")
				.style("fill", function(d) { return colorScale(d);});
			/*
			cards.transition().duration(1000)
			.style("fill", function(d) { console.log(colorScale(d)); return colorScale(d); });

			cards.select("title").text(function(d) { return d; });

			cards.exit().remove();
			*/
			var legend = svg.selectAll(".legend").append("g")
				.attr("class", "legend");
	
			legend.data(colors).enter().append("rect")
				.attr("x", function(d, i) { return legendElementWidth * i; })
				.attr("y", (players.length + 2) * gridHeight)
				.attr("width", legendElementWidth)
				.attr("height", gridHeight)
				.style("fill", function(d) { return d; });

			legend.append("text")
				.text(function(d) { return "≥ " + d; })
				.attr("x", function(d, i) { return legendElementWidth * i; })
				.attr("y", height + gridHeight);
		});
	}
});
