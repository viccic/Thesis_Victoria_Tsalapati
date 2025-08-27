import laspy
import numpy as np
import matplotlib.pyplot as plt
from alphashape import alphashape
import trimesh
from shapely.geometry import MultiPolygon
import os

#-----------first OK------------------------#

for i in range(1,62):
    if i!= 39:
        print("Entering the folder of tree " + str(i) + "...")

        # Load LAS
        las = laspy.read("C:/THESIS_TUDELFT/DATA_AHN5/clean_trees/" + str(i) + "/merged_tree_" + str(i) + "_syn.las")
        points = np.vstack((las.x, las.y, las.z)).T

        mean_x = np.mean(points[:,0])
        mean_y = np.mean(points[:,1])
        mean_z = np.mean(points[:,2])

        new_points = np.vstack((las.x - mean_x, las.y - mean_y, las.z - mean_z)).T

        # # Downsample if needed
        # points = points[::100]  # reduce density for performance

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
            obj_path = "C:/THESIS_TUDELFT/DATA_AHN5/clean_trees/" + str(i) + "/alpha_" + str(j) + "_syn.obj"
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

            with open("C:/THESIS_TUDELFT/DATA_AHN5/clean_trees/" + str(i) + "/alpha_shape_" + str(j) + "_centered_tree" + str(i) + "_syn.obj", "w") as f:
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
