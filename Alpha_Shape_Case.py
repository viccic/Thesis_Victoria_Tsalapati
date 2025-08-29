import laspy
import numpy as np
from alphashape import alphashape
import trimesh
from shapely.geometry import MultiPolygon
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(script_dir, "Input_Alpha_Shape_Case")
las_files = [f for f in os.listdir(input_path) if f.endswith(".las")]

for individual in las_files:
        print("Processing the tree file with name " + str(individual) + "...")

        # Load LAS
        las = laspy.read(individual)
        points = np.vstack((las.x, las.y, las.z)).T

        mean_x = np.mean(points[:,0])
        mean_y = np.mean(points[:,1])
        mean_z = np.mean(points[:,2])

        new_points = np.vstack((las.x - mean_x, las.y - mean_y, las.z - mean_z)).T

        for j in [0.5, 1.0, 1.5]:

            print("Extracting alpha-shape with parameter as " + str(j) + "...")

            # Compute 3D alpha shape
            alpha = alphashape(new_points, j)

            # Ensure output is a 3D mesh (some alpha shapes return 2D polygons)
            if isinstance(alpha, MultiPolygon):
                raise ValueError("Alpha shape is 2D. Cannot export as OBJ without converting to 3D mesh.")

            # Convert to trimesh if needed
            if not isinstance(alpha, trimesh.Trimesh):
                mesh = trimesh.Trimesh(vertices=alpha.vertices, faces=alpha.faces)
            else:
                mesh = alpha

            # Define output path
            base_name, _ = os.path.splitext(individual[0])
            output_path = os.path.join(script_dir, "Output_Alpha_Shape_Case")
            j_str = str(j).replace('.', '_')

            obj_path = os.path.join(
                output_path,
                str(individual),
                f"_{base_name}_alpha_shape_ct{j_str}.obj"
            )
            os.makedirs(os.path.dirname(obj_path), exist_ok=True)
            # Export as OBJ
            with open(obj_path, "wb") as f:
                f.write(trimesh.exchange.obj.export_obj(mesh).encode("utf-8"))

            new_lines = []

            with open(obj_path, "r") as f:
                for line in f:
                    if line.startswith("v "):  # vertex position
                        parts = line.strip().split()
                        x, y, z = map(float, parts[1:4])
                        x += mean_x
                        y += mean_y
                        z += mean_z
                        new_lines.append(f"v {x:.6f} {y:.6f} {z:.6f}\n")
                    else:
                        new_lines.append(line)

            obj_centered_path = os.path.join(
                output_path,
                str(individual),
                f"_{base_name}_alpha_shape_ct{j_str}_centered.obj"
            )
            os.makedirs(os.path.dirname(obj_path), exist_ok=True)

            with open(obj_centered_path, "w") as f:
                f.writelines(new_lines)

# # Load LAS
# las = laspy.read("C:/THESIS_TUDELFT/DATA_AHN5/clean_trees/1/merged_tree_1.las")
# points = np.vstack((las.x, las.y, las.z)).T
#
# # # Downsample if needed
# # points = points[::100]  # reduce density for performance
#
# # Compute 3D alpha shape
# alpha = alphashape(points, 1.5)
#
# # Ensure output is a 3D mesh (some alpha shapes return 2D polygons)
# if isinstance(alpha, MultiPolygon):
#     raise ValueError("Alpha shape is 2D. Cannot export as OBJ without converting to 3D mesh.")
#
# # Convert to trimesh if needed
# if not isinstance(alpha, trimesh.Trimesh):
#     mesh = trimesh.Trimesh(vertices=alpha.vertices, faces=alpha.faces)
# else:
#     mesh = alpha
#
# # Define output path
# obj_path = "C:/THESIS_TUDELFT/DATA_AHN5/clean_trees/1/alpha1_5.obj"
# os.makedirs(os.path.dirname(obj_path), exist_ok=True)
#
# # Export as OBJ
# with open(obj_path, "wb") as f:
#     f.write(trimesh.exchange.obj.export_obj(mesh).encode("utf-8"))


# Optional: Matplotlib 3D plot
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# ax.scatter = ax.scatter(points[:, 0], points[:, 1], points[:, 2])
# ax.plot_trisurf(*zip(*alpha.vertices), triangles=alpha.faces)
# plt.show()
# ---------------------------------#

# # Convert to Shapely Points (2D: X, Y only)
# geoms = [Point(x, y) for x, y in points[:, :2]]
#
# # Create GeoDataFrame
# gdf = gpd.GeoDataFrame(geometry=geoms, crs="EPSG:28992")  # Use correct CRS
#
# from alphashape import alphashape
# alphashape([point.coords[0] for point in gdf['geometry'][0]], 0.7).show()


# import open3d as o3d
# import laspy
# import numpy as np
# from alphashape import alphashape
#
# # Load your LAS file
# las = laspy.read("C:/THESIS_TUDELFT/DATA_AHN5/clean_trees/1/merged_tree_1.las")
# points = np.vstack((las.x, las.y, las.z)).T
#
# # Create Open3D point cloud
# pcd = o3d.geometry.PointCloud()
# pcd.points = o3d.utility.Vector3dVector(points)
# pcd.estimate_normals()
#
# # Visualize raw point cloud
# o3d.visualization.draw_geometries([pcd])
#
# # Ball Pivoting surface reconstruction
# radii = [0.5, 1.0, 2.0]  # You may need to tune these for your tree size (in meters)
# rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
#     pcd, o3d.utility.DoubleVector(radii))
#
# # Visualize the result
# o3d.visualization.draw_geometries([pcd, rec_mesh])
