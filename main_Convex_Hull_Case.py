from CanopyExtraction import extracting_tree_crown_points
from TreeCrownCreation import func_TreeCrownCreation
import time
import os

# Define the location of files
script_dir = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(script_dir, "Input")
las_file = [f for f in os.listdir(input_path) if f.endswith("synthesized.las")]
initial_laz_path = os.path.join(input_path, las_file[0])

# Create the outputs
os.makedirs("Output_Summer", exist_ok=True)
output_path = os.path.join(script_dir, "Output_Summer")
out_low_las = os.path.join(output_path, "Cropped_low.las")
tree_crown_las = os.path.join(output_path, "Tree_crown.las")
os.makedirs("Output_Summer/labelled_las", exist_ok=True)
os.makedirs("Output_Summer/rings", exist_ok=True)
folder_path_separated_las_files = os.path.join(output_path, "labelled_las")
folder_path_rings = os.path.join(output_path, "rings")

# Define parameters
dbscan_eps = 0.8
dbscan_min_samples = 3
inner_radius = 1.5
outer_radius = 2.0
height = 0.8
spacing = 1.0

tree_crown_las_path = os.path.join(output_path, "Tree_crown.las")
tree_crown_ply_path = os.path.join(output_path, "Tree_crown.ply")
output_high_points_obj = os.path.join(output_path, "Tree_Crown_convex_hull.obj")

start_time = time.time()
extracting_tree_crown_points(initial_laz_path, tree_crown_las, out_low_las, folder_path_separated_las_files, folder_path_rings, dbscan_eps, dbscan_min_samples, inner_radius, outer_radius, height, spacing)
func_TreeCrownCreation(tree_crown_las_path, tree_crown_ply_path, output_high_points_obj)
end_time = time.time()
print("Elapsed time: {:.2f} seconds".format(end_time - start_time))