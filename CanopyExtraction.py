import trimesh
from trimesh.transformations import translation_matrix
import laspy
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from laspy import ExtraBytesParams
import os


def crop_high_points(las_file):
    # Read the LAS file
    las = laspy.read(las_file)

    # Filter points with height (z) < 1.5
    mask = las.z < 1.5
    low_points = las.points[mask]

    return low_points

def points_inside_ring(las_point_cloud, center_x, center_y, center_z, inner_radius, outer_radius, height):
    dx = las_point_cloud.x - center_x
    dy = las_point_cloud.y - center_y
    dz = las_point_cloud.z

    radius = np.sqrt(dx ** 2 + dy ** 2)
    z_max = center_z + height/2

    # Define the geometric region
    inside_radius = (radius >= inner_radius) & (radius <= outer_radius)
    inside_height = (dz >= center_z - height/2) & (dz <= z_max)

    mask = inside_radius & inside_height
    return las_point_cloud[mask]

def func_points_inside_inner_higher_ring(las_point_cloud, center_x, center_y, center_z, inner_radius, height):
    dx = las_point_cloud.x - center_x
    dy = las_point_cloud.y - center_y
    dz = las_point_cloud.z

    radius = np.sqrt(dx ** 2 + dy ** 2)

    # Define the geometric region
    inside_inner_radius = radius <= inner_radius
    inside_height = (dz >= center_z - height/2) & (dz <= center_z + height/2)

    mask = inside_inner_radius & inside_height
    return las_point_cloud[mask]


def delete_points(las_point_cloud, center_x, center_y, inner_radius, minimum_height):
    dx = las_point_cloud.x - center_x
    dy = las_point_cloud.y - center_y
    dz = las_point_cloud.z

    radius = np.sqrt(dx ** 2 + dy ** 2)
    mask = ~((radius <= inner_radius) & (dz <= minimum_height))

    return mask

def func_DBSCAN(las, las_points, eps, min_samples):

    # getting scaling and offset parameters
    las_scaleX = las.header.scale[0]
    las_offsetX = las.header.offset[0]
    las_scaleY = las.header.scale[1]
    las_offsetY = las.header.offset[1]
    las_scaleZ = las.header.scale[2]
    las_offsetZ = las.header.offset[2]

    # calculating coordinates
    p_X = np.array((las_points.x * las_scaleX) + las_offsetX)
    p_Y = np.array((las_points.y * las_scaleY) + las_offsetY)
    p_Z = np.array((las_points.z * las_scaleZ) + las_offsetZ)

    # plotting points
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(p_X, p_Y, p_Z, c='r', marker='o')
    plt.show()

    low_las = laspy.create(point_format=las.header.point_format, file_version=las.header.version)
    low_las.header = las.header  # Copy header information
    low_las.points = las_points
    points_low_las = np.vstack((las_points.x, las_points.y, las_points.z)).T

    # implementing DBSCAN
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(points_low_las)
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)

    unique_labels = set(labels)
    core_samples_mask = np.zeros_like(labels, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True

    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = [0, 0, 0, 1]

        class_member_mask = labels == k

        xy = points_low_las[class_member_mask & core_samples_mask]
        plt.plot(
            xy[:, 0],
            xy[:, 1],
            "o",
            markerfacecolor=tuple(col),
            markeredgecolor="k",
            markersize=14,
        )

        xy = points_low_las[class_member_mask & ~core_samples_mask]
        plt.plot(
            xy[:, 0],
            xy[:, 1],
            "o",
            markerfacecolor=tuple(col),
            markeredgecolor="k",
            markersize=6,
        )

    plt.title(f"Estimated number of clusters: {n_clusters_}")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plt.savefig(os.path.join(script_dir, "estimated_number_clusters.png"))
    plt.show()

    return labels, unique_labels

def extracting_tree_crown_points(laz_path, tree_crown_las, out_low_las, las_folder_path, ring_folder_path, dbscan_eps, dbscan_min_samples, inner_radius, outer_radius, height, spacing):

    las = laspy.read(laz_path)
    points = np.vstack((las.x, las.y, las.z)).T

    # Create a new LAS file from low_points
    low_las = laspy.create(point_format=las.header.point_format, file_version=las.header.version)
    low_points = crop_high_points(laz_path)
    low_las.header = las.header
    low_las.points = low_points
    low_las.write(out_low_las)

    labels, unique_labels = func_DBSCAN(las, low_points, dbscan_eps, dbscan_min_samples)

    # Copy existing point data
    for dim in las.point_format.dimension_names:
        setattr(low_las, dim, getattr(las, dim)[las.z < 1.5])  # same mask as used in crop_high_points()

    # Add labels as extra dimension
    label_dim = ExtraBytesParams(name="label", type=np.uint16)
    low_las.add_extra_dim(label_dim)
    low_las["label"] = labels

    for i in unique_labels:
        mask = low_las.label == i
        label_points = low_las.points[mask]

        filtered_labelled_las = laspy.create(point_format=las.header.point_format, file_version=las.header.version)
        filtered_labelled_las.header = las.header  # Copy header information
        filtered_labelled_las.points = label_points
        os.makedirs(las_folder_path, exist_ok=True)
        output_path = os.path.join(las_folder_path, f"label_{i}.las")
        filtered_labelled_las.write(output_path)


    # List all LAS/LAZ files
    las_files = [f for f in os.listdir(las_folder_path) if f.lower().endswith((".las", ".laz"))]

    # Create the ring mesh
    ring_mesh = trimesh.creation.annulus(r_min=inner_radius, r_max=outer_radius, height=height)
    # spacing = 1.0
    combined_deletion = []

    print(f"Initial point count: {len(las.x)}")

    # Iterate over label files
    for j, filename in enumerate(las_files):
        file_path = os.path.join(las_folder_path, filename)
        las_label = laspy.read(file_path)
        if len(las_label.x) == 0:
            print(f"Skipping empty file: {filename}")
            continue

        origin_x = np.mean(las_label.x)
        origin_y = np.mean(las_label.y)
        origin_z = np.min(las_label.z)

        print("Cluster: ", j)
        print("origin_x:", origin_x, "origin_y:", origin_y, "origin_z:", origin_z)

        # Create mesh and find z_offset where it intersects points
        for i in range(100):
            z_offset = origin_z + i * spacing
            T = translation_matrix([origin_x, origin_y, z_offset])
            mesh_copy = ring_mesh.copy()
            mesh_copy.apply_transform(T)

            ring_folder = ring_folder_path + "/" + str(j)
            # ring_folder_1 = f"C:/THESIS_TUDELFT/GITHUB/Thesis_Tsalapati/assets/tree_crown_case/rings"
            os.makedirs(ring_folder, exist_ok=True)
            mesh_copy.export(os.path.join(ring_folder, "higher_ring.stl"))
            # mesh_copy.export(os.path.join(ring_folder_1, "higher_ring" + str(j) + ".stl"))

            ring_points = points_inside_ring(las, origin_x, origin_y, z_offset, inner_radius, outer_radius, height)

            if len(ring_points.points) != 0:
                break
        print("origin_x: ", origin_x)
        print("origin_y: ", origin_y)
        print("z_offset: ", z_offset)

        # Remove stem points up to detected height
        points_above = func_points_inside_inner_higher_ring(las, origin_x, origin_y, z_offset, inner_radius, height)

        if len(points_above.z) == 0:
            print(f"No points in ring at iteration {j}, skipping deletion.")
            continue
        print("number of stem points: ", len(points_above.z))
        minimum_height = min(points_above.z)
        print("minimum_height: ", minimum_height)
    #sos
        # Compute deletion mask from current filtered_las
        deletion_mask = delete_points(las, origin_x, origin_y, inner_radius, minimum_height)
        combined_deletion.append(deletion_mask)

    indices_to_remove = [62, 55, 54, 53, 49, 48, 44, 38, 25, 19]  # must be in descending order
    for i in indices_to_remove:
        del combined_deletion[i]
    print('Outliers deleted')

    combined_deletion_mask = np.ones(len(las.x), dtype=bool)
    for mask in combined_deletion:
        combined_deletion_mask &= mask

    cropped_las = laspy.create(point_format=las.header.point_format, file_version=las.header.version)
    cropped_las.header = las.header
    for dim in las.point_format.dimension_names:
        if hasattr(las, dim):
            setattr(cropped_las, dim, getattr(las, dim)[combined_deletion_mask])
    cropped_las.write(tree_crown_las)

    print("Remaining after mask:", np.sum(combined_deletion_mask))





