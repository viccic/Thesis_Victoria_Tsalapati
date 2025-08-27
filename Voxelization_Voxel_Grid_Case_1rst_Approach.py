import laspy
import open3d as o3d
import numpy as np
import multiprocessing
import os
from laspy import LasData, ExtraBytesParams

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

def process_voxel_combined(task):
    x, y, z, voxel_size, points_array = task
    half_size = voxel_size / 2
    mask = (
        (points_array[:, 0] >= x - half_size) & (points_array[:, 0] <= x + half_size) &
        (points_array[:, 1] >= y - half_size) & (points_array[:, 1] <= y + half_size) &
        (points_array[:, 2] >= z - half_size) & (points_array[:, 2] <= z + half_size)
    )
    labels = points_array[mask][:, 3]
    num_points_branches = np.sum(labels == 1)
    num_points_leaves = np.sum(labels == 2)
    # print(f"PID {os.getpid()} processing voxel at ({x:.2f}, {y:.2f}, {z:.2f})")
    return ((x, y, z), num_points_branches, num_points_leaves)


def examine_voxel(las_point_cloud, voxel_grid, voxel_size, voxels_dict_branches, voxels_dict_leaves, num_points_branches_list, num_points_leaves_list, txt_file_path):
    # Inside examine_voxel
    remove_indices = []
    tasks = []
    points_array = np.vstack((las_point_cloud.x, las_point_cloud.y, las_point_cloud.z, las_point_cloud.label)).T

    for voxel in voxel_grid.get_voxels():
        grid_index_np = np.array(voxel.grid_index, dtype=np.int32)
        x, y, z = voxel_grid.get_voxel_center_coordinate(grid_index_np)
        tasks.append((x, y, z, voxel_size, points_array))

    with multiprocessing.Pool() as pool:
        results = pool.map(process_voxel_combined, tasks)

    for (x, y, z), num_points_branches, num_points_leaves in results:
        num_points_branches_list.append(num_points_branches)
        num_points_leaves_list.append(num_points_leaves)
        if num_points_branches == 0 and num_points_leaves == 0:
            grid_index = voxel_grid.get_voxel(np.array([x, y, z]))
            if grid_index is not None:
                remove_indices.append(grid_index)

    # Remove empty voxels from the grid
    for idx in remove_indices:
        voxel_grid.remove_voxel(idx)

    sums = [x + y for x, y in zip(num_points_branches_list, num_points_leaves_list)]

    max_number_points = max(sums)
    min_number_points = min(sums)

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

    for (x, y, z), num_points_branches, num_points_leaves in results:

        if num_points_branches >= num_points_leaves:
            voxels_dict_branches[(x, y, z)] = (num_points_branches, num_points_leaves)
        else:
            voxels_dict_leaves[(x, y, z)] = (num_points_branches, num_points_leaves)

    return voxels_dict_branches, voxels_dict_leaves, num_points_branches_list, num_points_leaves_list, voxel_grid


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

def merge_las_files(output_path, input_path):
    # Open input files
    with laspy.open(output_path, mode='a') as outlas:
        with laspy.open(input_path) as inlas:
            for points in inlas.chunk_iterator(2_000_000):
                outlas.append_points(points)

def voxels_creation(branches_las_path, leaves_las_path, output_obj_file_path_branches, output_obj_file_path_leaves, voxel_size, txt_file_path):

    # Read LAS file
    las_branches = laspy.read(branches_las_path)
    las_leaves = laspy.read(leaves_las_path)

    # Create a new header with PointFormat(0)
    new_header = laspy.LasHeader(point_format=0, version="1.2")
    new_header.offsets = las_branches.header.offsets
    new_header.scales = las_branches.header.scales

    # Create new LAS object
    new_branches = LasData(new_header)

    # Copy only desired dimensions
    for dim in ['X', 'Y', 'Z', 'intensity']:
        new_branches[dim] = las_branches[dim]

    # Add the "label" field to branches and set it to 1
    label_dim = ExtraBytesParams(name="label", type=np.uint16)
    new_branches.add_extra_dim(label_dim)
    new_branches["label"] = np.full(len(las_branches.points), 1, dtype=np.uint16)

    # Convert las_leaves to PointFormat 0 with same dimensions as new_branches
    leaves_header = laspy.LasHeader(point_format=0, version="1.2")
    leaves_header.offsets = las_leaves.header.offsets
    leaves_header.scales = las_leaves.header.scales

    new_leaves = LasData(leaves_header)

    for dim in ['X', 'Y', 'Z', 'intensity']:
        new_leaves[dim] = las_leaves[dim]

    # Add label = 2
    label_dim = ExtraBytesParams(name="label", type=np.uint16)
    new_leaves.add_extra_dim(label_dim)
    new_leaves["label"] = np.full(len(las_leaves.points), 2, dtype=np.uint16)

    # Prepare output path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "Output")
    synthetic_las_path = os.path.join(output_path, "SyntheticLAS.las")

    # Write new_branches LAS to file
    with laspy.open(synthetic_las_path, mode='w', header=new_branches.header) as writer:
        writer.write_points(new_branches.points)

    # Save this new_leaves to a temporary LAS file to match the format
    leaves_converted_path = os.path.join(output_path, "leaves_converted.las")
    with laspy.open(leaves_converted_path, mode='w', header=new_leaves.header) as writer:
        writer.write_points(new_leaves.points)

    merge_las_files(synthetic_las_path, leaves_converted_path)

    synthetic_las = laspy.read(synthetic_las_path)
    labels = synthetic_las["label"]
    print("Unique labels:", np.unique(labels, return_counts=True))

    # Convert point cloud to a voxel grid with a specific voxel size
    voxel_grid = voxelize_las(synthetic_las, voxel_size)

    # Process voxels
    voxels_dict_leaves = {}
    voxels_dict_branches = {}
    num_points_branches_list = []
    num_points_leaves_list = []
    voxels_dict_leaves, voxels_dict_branches, num_points_branches, num_points_leaves, voxel_grid = examine_voxel(synthetic_las, voxel_grid, voxel_size, voxels_dict_branches, voxels_dict_leaves, num_points_branches_list, num_points_leaves_list, txt_file_path)

    voxels_dict_list = [voxels_dict_leaves, voxels_dict_branches]
    output_obj_file_paths = [output_obj_file_path_leaves, output_obj_file_path_branches]

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
