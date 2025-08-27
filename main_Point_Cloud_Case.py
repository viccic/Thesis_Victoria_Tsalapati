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

    # Convert the cropped las file to ply file
    out_points_ply = 'C:/THESIS_TUDELFT/DATA_AHN5/merged_tree_leaves_10.ply'
    out_points_las = 'C:/THESIS_TUDELFT/DATA_AHN5/merged_tree_leaves_10.las'
    las_to_ply(out_points_las, out_points_ply)

    # POINT CLOUD CASE
    out_point_cloud_obj = os.path.join("C:/THESIS_TUDELFT/Point_cloud_case_output/merged_tree_leaves_10.obj")
    point_cloud = cubes(out_points_ply, 0.02, out_point_cloud_obj)

    end_time = time.time()
    print("Elapsed time: {:.2f} seconds".format(end_time - start_time))

if __name__ == "__main__":
    main()
