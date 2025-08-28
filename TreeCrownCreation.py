import open3d as o3d
import numpy as np
import trimesh
import laspy

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
    # print(f"Saved PLY to {ply_path}")


def func_TreeCrownCreation(las_path, ply_path, output_high_points_obj):

    las_to_ply(las_path, ply_path)

    # Load the point cloud
    point_cloud = o3d.io.read_point_cloud(ply_path)

    # Convert point cloud to numpy array
    points = np.asarray(point_cloud.points)

    # Create a new point cloud with high points
    high_point_cloud = o3d.geometry.PointCloud()
    high_point_cloud.points = o3d.utility.Vector3dVector(points)

    # Create a convex hull from the high points if there are enough points
    if len(points) >= 3:  # Ensure there are enough points for a convex hull
        # Create a Trimesh object
        high_points_mesh = trimesh.Trimesh(vertices=points)

        # Generate the convex hull
        convex_hull_mesh = high_points_mesh.convex_hull

        # Keep only the vertices and faces of the convex hull
        hull_vertices = convex_hull_mesh.vertices
        hull_faces = convex_hull_mesh.faces

        # Create a new Trimesh object with only the convex hull vertices and faces
        final_mesh = trimesh.Trimesh(vertices=hull_vertices, faces=hull_faces)

        # Export the convex hull as an OBJ file
        final_mesh.export(output_high_points_obj)
        print(f"Saved tree crown OBJ to {output_high_points_obj}")
    else:
        print("Not enough points to create a convex hull.")


