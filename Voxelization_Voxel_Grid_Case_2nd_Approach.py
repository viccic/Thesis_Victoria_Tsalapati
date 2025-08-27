import laspy
import open3d as o3d
import numpy as np
import multiprocessing
import os

# Create a voxel as a cube using the centroid
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

def voxelize_las(las_point_cloud, voxel_size):
    """Converts LAS point cloud to a voxel grid."""
    points = np.vstack((las_point_cloud.x, las_point_cloud.y, las_point_cloud.z)).T
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    return o3d.geometry.VoxelGrid.create_from_point_cloud(pcd, voxel_size)

def points_inside_voxel(points_array, voxel, voxel_size):
    x, y, z = voxel
    half_size = voxel_size / 2
    mask = (
        (points_array[:, 0] >= x - half_size) & (points_array[:, 0] <= x + half_size) &
        (points_array[:, 1] >= y - half_size) & (points_array[:, 1] <= y + half_size) &
        (points_array[:, 2] >= z - half_size) & (points_array[:, 2] <= z + half_size)
    )
    return np.sum(mask)


def process_voxel(task):
    x, y, z, voxel_size, points_array = task
    # print(f"PID {os.getpid()} processing voxel at ({x:.2f}, {y:.2f}, {z:.2f})")
    num_points = points_inside_voxel(points_array, (x, y, z), voxel_size)
    return ((x, y, z), num_points)

def examine_voxel(las_point_cloud, voxel_grid, voxel_size, voxels_dict_1, voxels_dict_2, voxels_dict_3, voxels_dict_4, num_points_list, txt_file_path):
    # Inside examine_voxel
    remove_indices = []
    tasks = []
    points_array = np.vstack((las_point_cloud.x, las_point_cloud.y, las_point_cloud.z)).T

    for voxel in voxel_grid.get_voxels():
        grid_index_np = np.array(voxel.grid_index, dtype=np.int32)
        x, y, z = voxel_grid.get_voxel_center_coordinate(grid_index_np)
        tasks.append((x, y, z, voxel_size, points_array))

    with multiprocessing.Pool() as pool:
        results = pool.map(process_voxel, tasks)

    for (x, y, z), num_points in results:
        num_points_list.append(num_points)
        if num_points == 0:
            grid_index = voxel_grid.get_voxel(np.array([x, y, z]))
            if grid_index is not None:
                remove_indices.append(grid_index)

    # Remove empty voxels from the grid
    for idx in remove_indices:
        voxel_grid.remove_voxel(idx)

    max_number_points = max(num_points_list)
    min_number_points = min(num_points_list)

    with open(txt_file_path, 'w') as f:
        f.write("Voxel grid export log\n")
        f.write("=====================\n")
        f.write(f"Voxel size: {voxel_size} m\n\n")

        line_1 = "Maximum number of points inside a voxel: " + str(max_number_points)
        line_2 = "Minimum number of points inside a voxel: " + str(min_number_points)
        # print(line_1)
        # print(line_2)
        f.write(line_1 + "\n")
        f.write(line_2 + "\n")

    for (x, y, z), num_points in results:
        transparency_index = (max_number_points - num_points) / max_number_points

        if transparency_index <= 0.25:
            voxels_dict_4[(x, y, z)] = transparency_index
        elif transparency_index >= 0.26 and transparency_index <= 0.50:
            voxels_dict_3[(x, y, z)] = transparency_index
        elif transparency_index >= 0.51 and transparency_index <= 0.75:
            voxels_dict_2[(x, y, z)] = transparency_index
        else:
            voxels_dict_1[(x, y, z)] = transparency_index

    return voxels_dict_1, voxels_dict_2, voxels_dict_3, voxels_dict_4, num_points_list, voxel_grid


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

def voxels_creation(las_file_path, xyz_file_path, output_obj_file_path_1, output_obj_file_path_2, output_obj_file_path_3, output_obj_file_path_4, voxel_size, txt_file_path):

    # Read LAS file
    las = laspy.read(las_file_path)

    # # Open the output .xyz file for writing
    # with open(xyz_file_path, "w") as xyz_file:
    #     for x, y, z in zip(las.x, las.y, las.z):
    #         xyz_file.write(f"{x} {y} {z}\n")
    #
    # # Load a point cloud
    # pcd = o3d.io.read_point_cloud(xyz_file_path)

    # Convert point cloud to a voxel grid with a specific voxel size
    voxel_grid = voxelize_las(las, voxel_size)

    # Process voxels
    voxels_dict_1 = {}
    voxels_dict_2 = {}
    voxels_dict_3 = {}
    voxels_dict_4 = {}
    num_points_list = []
    voxels_dict_1, voxels_dict_2, voxels_dict_3, voxels_dict_4, num_points, voxel_grid = examine_voxel(las, voxel_grid, voxel_size, voxels_dict_1, voxels_dict_2, voxels_dict_3, voxels_dict_4, num_points_list, txt_file_path)

    voxels_dict_list = [voxels_dict_1, voxels_dict_2, voxels_dict_3, voxels_dict_4]
    output_obj_file_paths = [output_obj_file_path_1, output_obj_file_path_2, output_obj_file_path_3, output_obj_file_path_4]
    # o3d.visualization.draw_geometries([voxel_grid])

    # txt_file_path = "C:/THESIS_TUDELFT/voxel_case/voxel_counts_size" + str(voxel_size) + ".txt"

    # Open the file
    with open(txt_file_path, 'a') as f:
        # Save refined voxels to OBJ
        i = 1
        j = 0
        for voxels_dict in voxels_dict_list:
            generate_obj_voxel_from_dictionary(voxels_dict, voxel_size, output_obj_file_paths[j])
            line = f"Total voxels saved at voxels_dict_{i}: {len(voxels_dict)}"
            # print(line)
            f.write(line + "\n")
            i += 1
            j += 1


    return None
