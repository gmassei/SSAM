import os
import operator


def chartData(field):
    pass

def BuilHTMLGraph(data,dimension):

	currentDIR = os.path.abspath( os.path.dirname(__file__))

	HTMLfile=open(os.path.join(currentDIR,"barGraph.html"),"w")

	HTMLfile.write("""<!DOCTYPE html>
	<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<title>Sustainability box</title>
		<meta name="keywords" content="">
		<meta name="description" content="" />
		<link href="http://fonts.googleapis.com/css?family=Open+Sans:400,300,600,700|Archivo+Narrow:400,700" rel="stylesheet" type="text/css">
		<link href="default.css" rel="stylesheet" type="text/css" media="all" />
		<script type="text/javascript" src="https://www.google.com/jsapi"></script>
		<script type="text/javascript">
			google.load("visualization", "1", {packages:["corechart"]});
			google.setOnLoadCallback(drawChart);
			function drawChart() {
				var dataBar = google.visualization.arrayToDataTable([\n""")
                                                         
	HTMLfile.write(str(dimension)+",\n")
	for r in range(len(data)):
		HTMLfile.write(str(data[r])+",\n") #last doesn't printed
	HTMLfile.write("\n]);\n")
    
	HTMLfile.write("""	var optionsBarStack = {
			title: 'bars of sustainability',
			isStacked: 'true',
			legend:{position:'in'},
            colors: ['#ff3300', '#33bbe5','#337719'],
			};""")
	HTMLfile.write("""	var optionsBarHor = {
			legend:{position:'in'},
            colors: ['#ff3300', '#33bbe5','#337719'],
			};""")
			
	HTMLfile.write("""	var optionsBubble = {
			title: 'environment',
			colorAxis: {colors: ['red', 'green']},
			hAxis: {title: 'economic'},
			vAxis: {title: 'social'},
			};
			var chartBar = new google.visualization.ColumnChart(document.getElementById('barS_div'));
			chartBar.draw(dataBar, optionsBarStack);
			var chartBar = new google.visualization.ColumnChart(document.getElementById('barH_div'));
			chartBar.draw(dataBar, optionsBarHor);
			var chartBubble = new google.visualization.BubbleChart(document.getElementById('bubble_div'));
			chartBubble.draw(dataBar, optionsBubble)
		  }
		</script>""")
	HTMLfile.write("""
	  </head>
	  <body>
	  <div id="logo" class="container"><h1>Charts of sustainability</h1>
		<br></br>
		<div id="barH_div" style="width: 1350px; height: 750px;"  border='0'></div>
		<br><hr>
		<div id="barS_div" style="width: 1350px; height: 750px;"  border='0'></div>
		<br><hr>
		<div id="bubble_div" style="width: 1350px; height: 750px;"  border='0'></div>
		<br><hr>
		<hr>
	  </body>
	</html>""")
	HTMLfile.close()
