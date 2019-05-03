# gtfs_graph_builder
Parse NYC MTA GTFS (General Transit Feed Specification) data to create an idealized graph of the NYC Subway.

The graph is *idealized*: all travel times are averaged, I only examined weekday daytime non-rush-hour schedules, and I deleted odd trains that aren't always running. The GTFS transfer file only indicated travel time between platforms, so I added 500 seconds of wait time to represent a rough average of how often trains come. Probably a little optimistic!

The current graph builder works for the 21 December 2018 NYC Subway GTFS, as downloaded from https://transitfeeds.com/p/mta/79.

The site is now *deployed* to DigitalOcean! It's at https://www.danielburton.dev. Running on Gunicorn with NGINX as a reverse proxy server.

The bash script get_gtfs.sh will create a 'data' folder, download and extract the appropriate data, then process the data into a graph in the new folder 'graph'.

The flask app in /server will start an API that responds to route or meeting place queries with a route JSON.

The python interface, interface.py, is a command line front end with fuzzy matching of user input to station names. meeting_interface.py is a work in progress that will do the same.


Next steps: 
  - solve some bugs having to do with walking-- it's telling the user to walk in odd places.
  - find a better workflow for using Jupyter Notebooks with git, as well as transferring code between notebooks and python scripts.
  - improve the CSS for the web app.
  - create a simple visualization of the routes / found meeting places for the web app. 
  - improve narration of subway routes.
  - work on the autocomplete for the React app... it's skipping certain stations.
