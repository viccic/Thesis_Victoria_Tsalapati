import os
import laspy
import numpy as np
import open3d as o3d
from matplotlib import pyplot as plt
from Voxelization import voxels_creation
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

# FROM LAS TO XYZ
def las_to_xyz(las_path, xyz_path):
    # Read the LAS file
    print("Reading LAS file...")
    las = laspy.read(las_path)

    # Open the output .xyz file for writing
    with open(xyz_path, "w") as xyz_file:
        print("Writing to XYZ file...")
        for x, y, z in zip(las.x, las.y, las.z):
            xyz_file.write(f"{x} {y} {z}\n")

    print(f"Conversion complete. XYZ file saved to {xyz_path}")


def main():

    # Define the location of files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, "Input")
    branches_las_file = [f for f in os.listdir(input_path) if f.endswith("Branches.las")]
    branches_las_path = os.path.join(input_path, branches_las_file[0])
    leaves_las_file = [f for f in os.listdir(input_path) if f.endswith("Leaves.las")]
    leaves_las_path = os.path.join(input_path, leaves_las_file[0])

    # Create the outputs
    os.makedirs("Output", exist_ok=True)
    output_path = os.path.join(script_dir, "Output")

    # VOXELS CASE
    time_recorder = []
    # voxel_sizes = [0.03, 0.05, 0.07, 0.1, 0.3, 0.5]
    voxel_sizes = [0.03]
    branches_xyz_file_path = os.path.join(output_path, "Branches.xyz")
    leaves_xyz_file_path = os.path.join(output_path, "Leaves.xyz")

    las_to_xyz(branches_las_path, branches_xyz_file_path)
    las_to_xyz(leaves_las_path, leaves_xyz_file_path)

    for i in voxel_sizes:
        start_time = time.time()
        print("Start of voxel construction of size of " + str(i) + "m")
        output_obj_file_path_branches = os.path.join(output_path, "voxels_" + str(i) + "_branches.obj")
        output_obj_file_path_leaves = os.path.join(output_path, "voxels_" + str(i) + "_leaves.obj")
        voxel_size = i

        txt_file_path = os.path.join(output_path, "voxel_counts_size_" + str(voxel_size) + ".txt")
        voxels_creation(branches_las_path, leaves_las_path, output_obj_file_path_branches, output_obj_file_path_leaves, voxel_size, txt_file_path)

        end_time = time.time()
        time_recorder.append(round(end_time - start_time))
        print("End of voxel construction of size of " + str(voxel_size) + "m")

    plt.plot(voxel_sizes, time_recorder, color='blue', marker='o',linestyle='-')
    plt.title("Amount of time spent for processing per voxel size")
    plt.xlabel("Voxel size (m)")
    plt.ylabel("Time (s)")
    plt.savefig(os.path.join(output_path, "plot_voxel_size.png"))
    plt.show()

    print("Voxel sizes: ", voxel_sizes)
    print("Time: ", time_recorder)

if __name__ == "__main__":
    main()
