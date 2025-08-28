from CanopyExtraction import extracting_tree_crown_points
from RemoveIndices import func_remove_indices
from TreeCrownCreation import func_TreeCrownCreation
import time
import ast
import os

# Define the location of files
script_dir = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(script_dir, "Input_Convex_Hull_Case")
las_file = [f for f in os.listdir(input_path) if f.endswith(".las")]
base_name, _ = os.path.splitext(las_file[0])
initial_las_path = os.path.join(input_path, las_file[0])

# Create the outputs
os.makedirs("Output_Convex_Hull_Case", exist_ok=True)
output_path = os.path.join(script_dir, "Output_Convex_Hull_Case")
out_low_las = os.path.join(output_path, f"{base_name}_Cropped_low.las")
tree_crown_las_path = os.path.join(output_path, f"{base_name}_Tree_crown.las")
os.makedirs("Output_Convex_Hull_Case/labelled_las", exist_ok=True)
os.makedirs("Output_Convex_Hull_Case/rings", exist_ok=True)
folder_path_separated_las_files = os.path.join(output_path, "labelled_las")
folder_path_rings = os.path.join(output_path, "rings")

# Define parameters
parameters_DBSCAN_path = os.path.join(input_path, "Parameters_DBSCAN.txt")
with open(parameters_DBSCAN_path, "r", encoding="utf-8") as f:
    first_line = f.readline().strip().split()
    second_line = f.readline().strip().split()
    third_line = f.readline().strip().split()
    forth_line = f.readline().strip().split()
    fifth_line = f.readline().strip().split()
    sixth_line = f.readline().strip().split()

dbscan_eps = float(first_line[1])
dbscan_min_samples = int(second_line[1])
inner_radius = float(third_line[1])
outer_radius = float(forth_line[1])
height = float(fifth_line[1])
spacing = float(sixth_line[1])


tree_crown_ply_path = os.path.join(output_path, f"{base_name}_Tree_crown.ply")
output_high_points_obj = os.path.join(output_path, f"{base_name}_Tree_Crown_convex_hull.obj")
image_path = os.path.join(output_path, "estimated_clusters.png")

combined_deletion = extracting_tree_crown_points(initial_las_path, out_low_las, folder_path_separated_las_files, folder_path_rings, image_path, dbscan_eps, dbscan_min_samples, inner_radius, outer_radius, height, spacing)
raw = input("Enter indices to remove in descending order (e.g. [62,55,54]): ")
removing_indices = ast.literal_eval(raw)

func_remove_indices(initial_las_path, removing_indices, combined_deletion, tree_crown_las_path)
func_TreeCrownCreation(tree_crown_las_path, tree_crown_ply_path, output_high_points_obj)
