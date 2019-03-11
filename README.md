# gtfs_graph_builder
Parse NYC MTA GTFS (General Transit Feed Specification) data to create an idealized graph of the NYC Subway.

The graph is *idealized*: all travel times are averaged, I only examined weekday daytime non-rush-hour schedules, and I deleted odd trains that aren't always running. The GTFS transfer file only indicated travel time between platforms, so I added 500 seconds of wait time to represent a rough average of how often trains come. Probably a little optimistic!

The route finder currently works and I've created a command line python program with fuzzy matching of user input to station names. My next step is a web app that pings my REST server.
