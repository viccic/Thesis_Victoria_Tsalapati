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
    las_file = [f for f in os.listdir(input_path) if f.endswith(".las")]
    initial_las_path = os.path.join(input_path, las_file[0])

    # Create the outputs
    os.makedirs("Output", exist_ok=True)
    output_path = os.path.join(script_dir, "Output")

    # VOXELS CASE
    time_recorder = []
    voxel_sizes = [0.1]
    # voxel_sizes = [0.03, 0.05, 0.07, 0.1, 0.3, 0.5]
    xyz_file_path = os.path.join(output_path, "Study_area.xyz")
    las_to_xyz(initial_las_path, xyz_file_path)
    for i in voxel_sizes:
        start_time = time.time()
        print(f"Starting voxel size {i}")
        output_obj_file_path_1 = os.path.join(output_path, "voxels_" + str(i) + "_1_m_insitu.obj")
        output_obj_file_path_2 = os.path.join(output_path, "voxels_" + str(i) + "_2_m_insitu.obj")
        output_obj_file_path_3 = os.path.join(output_path, "voxels_" + str(i) + "_3_m_insitu.obj")
        output_obj_file_path_4 = os.path.join(output_path, "voxels_" + str(i) + "_4_m_insitu.obj")
        voxel_size = i

        txt_file_path = os.path.join(output_path, "voxel_counts_size_" + str(voxel_size) + "_insitu.txt")

        voxels_creation(initial_las_path, xyz_file_path, output_obj_file_path_1,
                                             output_obj_file_path_2, output_obj_file_path_3, output_obj_file_path_4,
                                             voxel_size, txt_file_path)
        end_time = time.time()
        time_recorder.append(round(end_time - start_time))
        print(f"Completing voxel size {i}")
        # print("Elapsed time: {:.2f} seconds".format(end_time - start_time))

    plt.plot(voxel_sizes, time_recorder, color='blue', marker='o',linestyle='-')
    plt.title("Amount of time spent for processing per voxel size")
    plt.xlabel("Voxel size (m)")
    plt.ylabel("Time (s)")
    plt.savefig(os.path.join(output_path, "plot_voxel_insitu.png"))
    plt.show()

    print("Voxel sizes: ", voxel_sizes)
    print("Time: ", time_recorder)

if __name__ == "__main__":
    main()
