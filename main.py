import osmnx as ox
import matplotlib.pyplot as plt
import geopandas as gpd

ox.settings.log_console = True
ox.settings.use_cache = True

place = "Université de Bordeaux"
uni_gdf = ox.geocoder.geocode_to_gdf(place)
uni_poly = uni_gdf.geometry.iloc[0]

tags_buildings = {"building": True}
buildings = ox.features.features_from_polygon(uni_poly, tags_buildings)

usable_areas = uni_gdf.copy()
bpoly = buildings[buildings.geom_type.isin(["Polygon","MultiPolygon"])].to_crs(uni_gdf.crs).union_all()
mask_gdf = gpd.GeoDataFrame(geometry=[bpoly], crs=uni_gdf.crs)
usable_areas = uni_gdf.overlay(mask_gdf, how="difference")

# --- plot usable areas inside the campus ---

# project both to a metric CRS so they overlay perfectly
uni_proj = ox.projection.project_gdf(uni_gdf)
usable_proj = ox.projection.project_gdf(usable_areas)

fig, ax = plt.subplots(figsize=(10,10))

# campus boundary
uni_proj.plot(ax=ax, facecolor="none", edgecolor="crimson", linewidth=2, label="Campus")

# usable areas (fill)
if not usable_proj.empty:
    usable_proj.plot(ax=ax, color="limegreen", alpha=0.35, label="Usable areas")

ax.set_title("Université de Bordeaux — Usable areas (campus minus buildings)")
ax.set_axis_off()
ax.legend()
plt.show()