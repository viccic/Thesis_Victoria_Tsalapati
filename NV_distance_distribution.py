import laspy
import open3d as o3d
import numpy as np
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt
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
        (4, 3, 2, 1),
        (5, 6, 7, 8),
        (8, 7, 3, 4),
        (8, 4, 1, 5),
        (1, 2, 6, 5),
        (3, 7, 6, 2)
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

las_path = "/path/to/your/LAS_dataset.las"
las = laspy.read(las_path)

for i in [0.03, 0.05, 0.07, 0.1, 0.3, 0.5]:
    voxel_size = i
    voxel_grid = voxelize_las(las, voxel_size)

    centers = []
    for voxel in voxel_grid.get_voxels():
        idx = np.array(voxel.grid_index, dtype=np.int32)
        x, y, z = voxel_grid.get_voxel_center_coordinate(idx)
        centers.append([x, y, z])

    array_centers = np.asarray(centers)
    if array_centers.shape[0] < 2:
        print(f"Not enough voxels for size {i} to compute distances.")
        continue

    tree = cKDTree(array_centers)
    distances, _ = tree.query(array_centers, k=2)
    nn = distances[:, 1]
    adj_nn = nn - i

    max_dist = np.max(adj_nn)
    ave_dist = np.mean(adj_nn)
    st_dev = np.std(adj_nn)

    print(f"Maximum distance between any voxel centers for size {i}: {max_dist:.3f} meters")
    print(f"Average distance between any voxel centers for size {i}: {ave_dist:.3f} meters")
    print(f"Standard deviation of distances for size {i}: {st_dev:.3f} meters")
    print(30 * " - ")

    plt.figure(figsize=(10, 6))
    counts, bins, _ = plt.hist(adj_nn, bins=50, color='skyblue', edgecolor='black')


    plt.axvline(ave_dist, color='red', linestyle='--', label=f"Mean = {ave_dist:.3f}")
    plt.xlabel("Nearest voxel distance")
    plt.ylabel("Frequency")
    plt.title(f"Nearest voxel distance distribution (voxel size = {i} m)")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(bins, [f"{b:.3f}" for b in bins], rotation=90)
    plt.tight_layout()
    plt.legend()
    foldername = "/path/to/save/output/png"
    filename = os.path.join(foldername,f"NV_distance_distribution_voxel_size_{i}m.png")
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.show()


