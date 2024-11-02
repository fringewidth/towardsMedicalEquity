# %%
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull, Delaunay
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.ndimage import label
import random


# %%
# india borders
NORTH = 37.1
SOUTH = 8.07
WEST = 68.12
EAST = 97.42

STEP = 0.01
NUM_LAT_STEPS = int((NORTH - SOUTH) / STEP)
NUM_LON_STEPS = int((EAST - WEST) / STEP)

RADIUS_FACTOR = 0.1

def get_idx(lat, lon):
    return (int((NORTH - lat) / STEP), int((lon - WEST) / STEP))

def get_lat_lon(idx):
    return (NORTH - idx[0] * STEP, WEST + idx[1] * STEP)



# %%
def exponential_decay(distance_squared):
    return np.exp(-6 * distance_squared)

def get_influence_map(hospitals, lat_col, lon_col):
    influence_map = np.zeros((NUM_LAT_STEPS, NUM_LON_STEPS))
    for i in range(len(hospitals)):
        lat, lon = hospitals.loc[i, lat_col], hospitals.loc[i, lon_col]
        idx, jdx = get_idx(lat, lon)
        r = hospitals.loc[i, 'Radius of Influence']
        r_steps = int(r / STEP)

        # Define the bounding box for influence radius
        start_i = max(0, idx - r_steps)
        end_i = min(NUM_LAT_STEPS, idx + r_steps + 1)
        start_j = max(0, jdx - r_steps)
        end_j = min(NUM_LON_STEPS, jdx + r_steps + 1)

        # Generate grid of indices within the bounding box
        x_coords, y_coords = np.meshgrid(np.arange(start_i, end_i), np.arange(start_j, end_j), indexing='ij')
        distance_squared = ((x_coords - idx) ** 2 + (y_coords - jdx) ** 2) * STEP**2

        # Apply influence decay only to points within the radius
        mask = distance_squared <= r**2
        influence_map[x_coords[mask], y_coords[mask]] += exponential_decay(distance_squared[mask])

    return influence_map

def plot_map(map, title, xlabel, ylabel, filename, cmap="GnBu", colorbar=True):
    plt.imshow(map, cmap=cmap, interpolation='nearest')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if colorbar:
        plt.colorbar()
    plt.savefig(filename)
    plt.show()

def plot_hist(map, title, xlabel, ylabel, filename, bins=40):
    plt.hist(map.flatten(), bins=bins, color="darkorange")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.ylim(0, 13)
    plt.savefig(filename)
    plt.show()

def cluster(influence_map, cutoff):
    clustering_cutoff = np.percentile(influence_map[influence_map > 0], cutoff)
    binary_map = (influence_map > clustering_cutoff).astype(int)
    clusters, num_clusters = label(binary_map)
    cluster_densities = [influence_map[clusters == cluster_id].sum() for cluster_id in range(1, num_clusters + 1)]
    return clusters, num_clusters, cluster_densities, binary_map

def plot_clusters(clusters, num_clusters, title, xlabel, ylabel, filename):
    num_colors = num_clusters + 1
    colors = list(mcolors.CSS4_COLORS.values())
    random.shuffle(colors)
    colors = ['white'] + colors[:num_colors - 1]
    random_cmap = mcolors.ListedColormap(colors[:num_colors])
    plot_map(clusters, title, xlabel, ylabel, filename, random_cmap, False)



# %%
def precompute_cluster_properties(clusters):
    cluster_properties = {}
    
    unique_clusters = np.unique(clusters)
    
    for cluster_id in unique_clusters:
        if cluster_id == 0: 
            continue
            
        cluster_coords = np.array(np.where(clusters == cluster_id)).T
        
        if len(cluster_coords) < 3:
            continue
            
        centroid = cluster_coords.mean(axis=0)
        hull = ConvexHull(cluster_coords)
        hull_points = cluster_coords[hull.vertices]
        
        distances = np.linalg.norm(hull_points - centroid, axis=1)
        min_radius = distances.min()
        
        cluster_properties[cluster_id] = {
            "centroid": centroid,
            "hull": hull,
            "hull_points": hull_points,
            "min_radius": min_radius,
            "delaunay_region": Delaunay(hull_points)
        }
    
    return cluster_properties


def add_clustered_noise(lat, lon, clusters, cluster_properties):
    idx, jdx = get_idx(lat, lon)
    
    cluster_id = clusters[idx, jdx]
    if cluster_id not in cluster_properties:
        return lat, lon  
    
    properties = cluster_properties[cluster_id]
    centroid = properties["centroid"]
    min_radius = properties["min_radius"]
    delaunay_region = properties["delaunay_region"]
    
    for _ in range(256):
        noise_direction = np.random.randn(2)  #random direction
        noise_direction /= np.linalg.norm(noise_direction)  
        noise_magnitude = np.random.uniform(0, min_radius)
        noise = noise_magnitude * noise_direction
        
        new_coords = np.array([idx, jdx]) + noise
        new_lat, new_lon = get_lat_lon(new_coords)
        
        if delaunay_region.find_simplex(new_coords) >= 0:
            return new_lat, new_lon  
    
    return lat, lon

def add_naive_noise(lat, lon, std, mean):
    std = std * STEP
    mean = mean * STEP
    return lat + np.random.normal(mean, std), lon + np.random.normal(mean, std)



# %%
hospitals = pd.read_csv('../data/main/4-hospitals_cleaned.csv')
hospitals['Radius of Influence'] = hospitals['Effective Rating'] * RADIUS_FACTOR

influence_map = get_influence_map(hospitals, 'Latitude', 'Longitude')
plot_map(influence_map, "A Map of Hospital Influence", "Longitude", "Latitude", "../fig/influence-map.svg")
clusters, num_clusters, cluster_densities, binary_map = cluster(influence_map, 50)
plot_clusters(clusters, num_clusters, "Clusters at 50th Percentile", "Longitude", "Latitude", "../fig/clusters.svg")

plot_hist(np.log(cluster_densities), "Histogram of Cluster Densities", "Logarithm of Cluster Density", "Frequency", "../fig/cluster-densities.svg")


# %%
hospitals_clustered = hospitals.copy()
cluster_properties = precompute_cluster_properties(clusters)
clustered_influence_map = get_influence_map(hospitals_clustered, 'Latitude', 'Longitude')
clusters, num_clusters, cluster_densities, binary_map = cluster(influence_map, 50)

for i in range(len(hospitals_clustered)):
    lat, lon = hospitals_clustered.loc[i, 'Latitude'], hospitals_clustered.loc[i, 'Longitude']
    new_lat, new_lon = add_clustered_noise(lat, lon, clusters, cluster_properties)
    hospitals_clustered.loc[i, 'Latitude'] = new_lat
    hospitals_clustered.loc[i, 'Longitude'] = new_lon

clustered_influence_map = get_influence_map(hospitals_clustered, 'Latitude', 'Longitude')
clusters, num_clusters, cluster_densities, binary_map = cluster(clustered_influence_map, 50)

plot_clusters(clusters, num_clusters, "Cluster Anonymised Clusters at 50th Percentile", "Longitude", "Latitude", "../fig/clustered-clusters.svg")
plot_hist(np.log(cluster_densities), "Histogram of Cluster Densities (Clustered Anonymised)", "Logarithm of Cluster Density", "Frequency", "../fig/clustered-cluster-densities.svg")


# %%
# find mean and std for naive noise
min_radii = []

for cluster_id, properties in cluster_properties.items():
    min_radii.append(properties['min_radius'])

min_radius = min(min_radii)
max_radius = max(min_radii)
median_radius = np.median(min_radii)
std = np.std(min_radii)
mean = np.mean(min_radii)

hospitals_naive = hospitals.copy()

for i in range(len(hospitals_naive)):
    lat, lon = hospitals_naive.loc[i, 'Latitude'], hospitals_naive.loc[i, 'Longitude']
    new_lat, new_lon = add_naive_noise(lat, lon, std, mean)
    hospitals_naive.loc[i, 'Latitude'] = new_lat
    hospitals_naive.loc[i, 'Longitude'] = new_lon

naive_influence_map = get_influence_map(hospitals_naive, 'Latitude', 'Longitude')
clusters, num_clusters, cluster_densities, binary_map = cluster(naive_influence_map, 50)
plot_clusters(clusters, num_clusters, "Anonymised Clusters at 50th Percentile after Random Noise Addition", "Longitude", "Latitude", "../fig/naive-clusters.svg")
plot_hist(np.log(cluster_densities), "Histogram of Cluster Densities (Naively Anonymised)", "Logarithm of Cluster Density", "Frequency", "../fig/naive-cluster-densities.svg")




