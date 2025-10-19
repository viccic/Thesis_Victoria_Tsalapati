import laspy
import open3d as o3d
import numpy as np
import os

def create_voxel(x, y, z, size):
    half_size = size / 2
    vertices = [
        (x - half_size, y - half_size, z - half_size),
        (x + half_size, y - half_size, z - half_size),
        (x + half_size, y + half_size, z - half_size),
        (x - half_size, y + half_size, z - half_size),
        (x - half_size, y - half_size, z + half_size),
        (x + half_size, y - half_size, z + half_size),
        (x + half_size, y + half_size, z + half_size),
        (x - half_size, y + half_size, z + half_size),
    ]
    faces = [
        (1, 2, 3, 4),
        (5, 6, 7, 8),
        (1, 5, 8, 4),
        (2, 6, 7, 3),
        (4, 3, 7, 8),
        (1, 2, 6, 5),
    ]
    return vertices, faces

def generate_obj_voxel_from_dictionary(voxels_dict, voxel_size, output_obj_file_path):
    """Writes voxelized output as an OBJ file."""
    written_voxels = [create_voxel(center[0], center[1], center[2], voxel_size) for center in voxels_dict]

    with open(output_obj_file_path, 'w') as obj_file:
        vertex_index = 1
        for vertices, faces in written_voxels:
            for vertex in vertices:
                obj_file.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
            for face in faces:
                obj_file.write(f"f {face[0] + vertex_index - 1} {face[1] + vertex_index - 1} "
                               f"{face[2] + vertex_index - 1} {face[3] + vertex_index - 1}\n")
            vertex_index += 8  # Move to the next voxel


def las_to_xyz(las_path, xyz_path):
    print("Reading LAS file...")
    las = laspy.read(las_path)
    with open(xyz_path, "w") as xyz_file:
        print("Writing to XYZ file...")
        for x, y, z in zip(las.x, las.y, las.z):
            xyz_file.write(f"{x} {y} {z}\n")
    print(f"Conversion complete. XYZ file saved to {xyz_path}")

def voxelize_las(las_point_cloud, voxel_size):
    points = np.vstack((las_point_cloud.x, las_point_cloud.y, las_point_cloud.z)).T
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    return o3d.geometry.VoxelGrid.create_from_point_cloud(pcd, voxel_size)

def main():

    # Define the location of files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, "Input_Voxel_Grid_Case_1rst_Approach_February")
    trees_las_file = [f for f in os.listdir(input_path) if f.endswith(".las")]
    trees_las_path = os.path.join(input_path, trees_las_file[0])

    # Create the outputs
    os.makedirs("Output_Voxel_Grid_Case_1rst_Approach_February", exist_ok=True)
    output_path = os.path.join(script_dir, "Output_Voxel_Grid_Case_1rst_Approach_February")

    # VOXELS CASE
    voxel_sizes = [0.03, 0.05, 0.1, 0.3, 0.5]
    las = laspy.read(trees_las_path)

    for i in voxel_sizes:
        voxel_size = i
        voxel_grid = voxelize_las(las, voxel_size)

        centers = []
        for voxel in voxel_grid.get_voxels():
            idx = np.array(voxel.grid_index, dtype=np.int32)
            x, y, z = voxel_grid.get_voxel_center_coordinate(idx)
            centers.append([x, y, z])

        output_obj_file_path = os.path.join(output_path, f"voxel_grid_{i}.obj")
        generate_obj_voxel_from_dictionary(centers, voxel_size, output_obj_file_path)

        print(f"Voxel grid of size of {i} m completed.")

if __name__ == "__main__":
    main()