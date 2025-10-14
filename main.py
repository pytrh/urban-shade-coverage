import networkx as nx
import osmnx as ox

# [out:json][timeout:25];

# // 1) Fetch Université de Bordeaux object
# nwr["amenity"="university"]["name"~"Université de Bordeaux"]->.univ;

# // 2) Turn it into an Area
# (.univ;)->.univArea;

# // Show the university outline
# .univ out geom;

# // 3) Buildings INSIDE the university area
# (
#   way["building"](area.univArea);
#   relation["building"](area.univArea);
# );
# out geom;

# // 4) Walkable areas INSIDE the university area
# (
#   way["highway"="footway"](area.univArea);
#   way["footway"="sidewalk"](area.univArea);
#   way["highway"="path"](area.univArea);
#   way["highway"="pedestrian"](area.univArea);
#   way["highway"="steps"](area.univArea);
#   relation["highway"="pedestrian"](area.univArea);
# );
# out geom;t
