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

# --- CRS projection to EPSG:3035 (ETRS89 / LAEA Europe) ---
uni_gdf = uni_gdf.to_crs("EPSG:3035")
buildings = buildings.to_crs("EPSG:3035")

# usable area calculation
usable_areas = uni_gdf.copy()
bpoly = buildings[buildings.geom_type.isin(["Polygon","MultiPolygon"])].union_all()
mask_gdf = gpd.GeoDataFrame(geometry=[bpoly], crs="EPSG:3035")
usable_areas = uni_gdf.overlay(mask_gdf, how="difference")
# random_trees = usable_areas.sample_points(200)

# --- iterative sampling until coverage ---
remaining = usable_areas.copy()
random_trees_list = []  # collect shapely Points here

max_iters = 200        # safety cap
min_residual_area = 1.0   # m² threshold to stop (tweak as you like)

radius_tree = 30
i = 0
while not remaining.empty and i < max_iters:
    # sample 1 tree from what's still uncovered
    samp = remaining.sample_points(1)
    if len(samp) == 0:
        break
    pt = samp.iloc[0]                 # shapely Point
    random_trees_list.append(pt)

    # buffer this tree by diamater_tree m (EPSG:3035 is meters)
    buf_gdf = gpd.GeoDataFrame(geometry=[pt.buffer(radius_tree)], crs=usable_areas.crs)

    # subtract buffer from what's left to cover
    remaining = remaining.overlay(buf_gdf, how="difference")

    # optional convergence check by area
    if remaining.geometry.area.sum() <= min_residual_area:
        break

    i += 1

# convert collected points to a GeoDataFrame for plotting/saving
random_trees_gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries(random_trees_list), crs=usable_areas.crs)
tree_buffers_gdf = gpd.GeoDataFrame(geometry=random_trees_gdf.buffer(radius_tree), crs=usable_areas.crs)

# random_trees['geometry'] = random_trees.buffer(10)


# --- plotting ---
fig, ax = plt.subplots(figsize=(10,10))

uni_gdf.plot(ax=ax, facecolor="none", edgecolor="crimson", linewidth=2, label="Campus")
if not usable_areas.empty:
    usable_areas.plot(ax=ax, color="limegreen", alpha=0.35, label="Usable areas")

# convert to a GeoDataFrame if needed (works whether random_trees is a GeoSeries or not)
# random_trees_gdf = gpd.GeoDataFrame(geometry=random_trees, crs=usable_areas.crs)

# tree_buffers = random_trees_gdf.buffer(10)  # 10 m since EPSG:3035 is in meters
# tree_buffers_gdf = gpd.GeoDataFrame(geometry=tree_buffers, crs=usable_areas.crs)

# plot buffers first so points are visible on top
tree_buffers_gdf.plot(ax=ax, facecolor="none", edgecolor="darkgreen", linewidth=1, alpha=0.7, label=f"Tree buffer ({radius_tree} m)")
# plot the trees as points on top
random_trees_gdf.plot(ax=ax, markersize=8, color="darkgreen", alpha=0.9, label="Trees")

ax.set_title("Université de Bordeaux — Usable areas (projected to EPSG:3035)")
ax.set_axis_off()
ax.legend()
plt.show()

print(f"Finished after {i} iterations")
print(f"Total trees placed: {len(random_trees_gdf)}")
print(f"Remaining uncovered area: {remaining.geometry.area.sum():.2f} m²")