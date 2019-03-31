# Unnamed Subway App
## A React frontend for finding a time-equidistant meeting place between two starting subway stops.

### Currently:
* Input your two starting stations, with autocomplete to ensure they're spelled perfectly
* Select how many meeting place suggestions you'd like to get
* Get results from my web API (https://github.com/daniel-burton/gtfs_graph_builder)
* Display suggested meeting places, with suggested subway routes as text.

### To Do:
* Display meeting places on a map
* Deploy the web API somewhere (heroku?)
* If you put in two stations that are somewhat close together, it sometimes suggests meeting places that are equally inconvenient for both users (because both users have the same travel time to that distant station)
  * Maybe if travel time is over a certain amount, retry with fuzzier equality?
* Clean up/pretty up CSS
