import os
import operator

    
def HTMLCharts(data,dimension):

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
    
    HTMLfile.write("""    var optionsBarStack = {
            title: 'bars of sustainability',
            isStacked: 'true',
            legend:{position:'in'},
            colors: ['#ff3300', '#33bbe5','#337719'],
            };""")
    HTMLfile.write("""	var optionsBarHor = {
            legend:{position:'in'},
            colors: ['#ff3300', '#33bbe5','#337719'],
            };""")
    if (len(dimension[1:])==3):
        HTMLfile.write("""    var optionsBubble = {
                title:'%s',
                colorAxis: {colors: ['red', 'green']},
                hAxis: {title: '%s'},
                vAxis: {title: '%s'},
                };
                var chartBar = new google.visualization.ColumnChart(document.getElementById('barS_div'));
                chartBar.draw(dataBar, optionsBarStack);
                var chartBar = new google.visualization.ColumnChart(document.getElementById('barH_div'));
                chartBar.draw(dataBar, optionsBarHor);
                var chartBubble = new google.visualization.BubbleChart(document.getElementById('bubble_div'));
                chartBubble.draw(dataBar, optionsBubble)
              }
            </script>""" % (str(dimension[3]),str(dimension[1]),str(dimension[2])))
            
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
    
    
def plotlyCharts(data,dimension):
    try:
        import pandas as pd
        import plotly.express as px
        from plotly.subplots import make_subplots
        df=pd.DataFrame(data, columns=dimension)
        print(df)
        fig = make_subplots(rows=1, cols=2, )
        # Here we use a column with categorical data
        #fig=px.scatter_ternary(df, a=dimension[1], b=dimension[2], c=dimension[3], color=dimension[1], size=dimension[1], hover_name=dimension[0],size_max=15, color_discrete_map = {dimension[1]: "blue", dimension[2]: "green", dimension[3]:"red"})
        #fig.add_trace(px.scatter_ternary(df, a=dimension[1], b=dimension[2], c=dimension[3], color=dimension[1], size=dimension[1], hover_name=dimension[0],size_max=15, color_discrete_map = {dimension[1]: "blue", dimension[2]: "green", dimension[3]:"red"}))                                                                                                                                    
        fig = px.bar_polar(df, r=dimension[1], theta=dimension[0], color=dimension[1], template="plotly_dark",
            color_discrete_sequence= px.colors.sequential.Plasma_r)
        fig.update_layout(height=600, width=800, title_text="Side By Side Subplots")
        fig.show()
    except ImportError as e:
        pass  # module doesn't exist, deal with it.
