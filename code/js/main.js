$(document).ready(function() {
	var margin = { top: 20, right: 0, bottom: 0, left: 145 },
		width = 1200 - margin.left - margin.right,
		height = 800 - margin.top - margin.bottom,
		gridWidth = Math.floor(width / 48),
		gridHeight = gridWidth + 4,
		legendElementWidth = gridWidth*3,
		colors = [],
		times = ["Q1", "Q2", "Q3", "Q4"],
		bins = [.1, .2, .3, .4, .5, .6, .7, .8, .9];

	for (var i = .05; i < 1; i += .1) {
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
		.attr("class", "time_label")
		.style("text-anchor", "middle")
		.attr("transform", "translate(" + gridWidth / 2 + ", -6)");

	var colorScale = d3.scaleThreshold()
		.domain(bins)
		.range(colors);
	
	$("#team").on("change", drawHeatMap);
	$("#year").on("change", drawHeatMap);

	drawHeatMap();

	var legend = d3.select(".legend").append("g");
	legend.selectAll("rect").data(colors).enter().append("rect")
		.attr("x", function(d, i) { return legendElementWidth * i; })
		.attr("y", 20)
		.attr("class", "legend_rect")
		.attr("width", legendElementWidth)
		.attr("height", gridHeight)
		.style("fill", function(d) { return d; });
	var legend_labels = [0].concat(bins);
	legend.selectAll("text").data(legend_labels).enter().append("text")
		.attr("class", "legend_label")
		.text(function(d) { return parseInt(d * 100) + "%-" + parseInt((d + .1) * 100) + "%"; })
		.attr("x", function(d, i) { return (legendElementWidth * i) + 5; })
		.attr("y", 15);

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

			var player_labels = svg.selectAll("text.player_label").data(players);

			player_labels.enter().append("text")
				.attr("x", 0)
				.attr("class", "player_label")
				.style("text-anchor", "end")
				.merge(player_labels)
				.text(function (d) {return d;})
				.attr("y", function (d, i) { return i * gridHeight; })
				.attr("transform", "translate(-2," + gridHeight / 1.5 + ")")

			player_labels.exit().remove();

			var minute_rects = svg.selectAll("rect.minute")
				.data(minute_values);
		
			minute_rects.exit().remove();
			minute_rects.enter().append("rect")
				.attr("rx", 4)
				.attr("ry", 4)
				.attr("width", gridWidth)
				.attr("height", gridHeight)
				.attr("class", "bordered minute")
				.style("fill", colors[0])
				.merge(minute_rects)
				.attr("x", function(d, i) { return (i % 48) * gridWidth; })
				.attr("y", function(d, i) { return Math.floor(i / 48) * gridHeight; })
			
			d3.selectAll("rect.minute").transition().duration(500)
				.style("fill", function(d) { return colorScale(d); });
		});
	}
});
