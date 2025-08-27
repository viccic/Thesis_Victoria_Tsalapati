import os
import laspy
import numpy as np
import open3d as o3d
from Cube import cubes
import time

def las_to_ply(las_path, ply_path):
    # Read LAS file
    las = laspy.read(las_path)
    points = np.vstack((las.x, las.y, las.z)).transpose()

    # Optional: get color if available
    has_color = hasattr(las, "red") and hasattr(las, "green") and hasattr(las, "blue")
    if has_color:
        colors = np.vstack((las.red, las.green, las.blue)).transpose()
        colors = colors / 65535.0  # Normalize 16-bit colors
    else:
        colors = None

    # Create Open3D point cloud
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    if colors is not None:
        pcd.colors = o3d.utility.Vector3dVector(colors)

    # Save to PLY
    o3d.io.write_point_cloud(ply_path, pcd)
    print(f"Saved PLY to {ply_path}")


def main():

    start_time = time.time()

    # Define the location of files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, "Input_Point_Cloud_Case")
    las_file = [f for f in os.listdir(input_path) if f.endswith(".las")]
    initial_las_path = os.path.join(input_path, las_file[0])

    # Create the outputs
    os.makedirs("Output_Point_Cloud_Case", exist_ok=True)
    output_path = os.path.join(script_dir, "Output_Point_Cloud_Case")

    # Create output PLY file name based on LAS file
    base_name = os.path.splitext(las_file[0])[0]
    out_points_ply = os.path.join(output_path, base_name + ".ply")

    # Convert the cropped las file to ply file
    # out_points_ply = 'C:/THESIS_TUDELFT/DATA_AHN5/merged_tree_leaves_10.ply'
    las_to_ply(initial_las_path, out_points_ply)

    # POINT CLOUD CASE
    out_point_cloud_obj = os.path.join(output_path, base_name + ".obj")
    cubes(out_points_ply, 0.02, out_point_cloud_obj)
    txt_file_path_time = os.path.join(output_path, "Processing_time.txt")
    end_time = time.time()

    # Open the file
    with open(txt_file_path_time, 'a') as f:
        line = "Elapsed time: {:.2f} seconds".format(end_time - start_time)
        f.write(line + "\n")

    print("Elapsed time: {:.2f} seconds".format(end_time - start_time))

if __name__ == "__main__":
    main()
