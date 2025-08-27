import open3d as o3d
import os

def cubes(xyz_ply, size, output_obj_file_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_path = os.path.join(script_dir, "assets")

    file_name = os.path.basename(xyz_ply)
    file = os.path.splitext(file_name)

    # Read the PLY file
    point_cloud = o3d.io.read_point_cloud(xyz_ply)
    points = point_cloud.points


    # Function to create a cube with the point as the centroid
    def create_cube_3d(x, y, z, size):
        half_size = size / 2
        # Define cube vertices (3D)
        vertices = [
            (x - half_size, y - half_size, z - half_size),  # Bottom-left-front
            (x + half_size, y - half_size, z - half_size),  # Bottom-right-front
            (x + half_size, y + half_size, z - half_size),  # Top-right-front
            (x - half_size, y + half_size, z - half_size),  # Top-left-front
            (x - half_size, y - half_size, z + half_size),  # Bottom-left-back
            (x + half_size, y - half_size, z + half_size),  # Bottom-right-back
            (x + half_size, y + half_size, z + half_size),  # Top-right-back
            (x - half_size, y + half_size, z + half_size),  # Top-left-back
        ]
        # Define cube faces (indices into the vertex list)
        faces = [
            (1, 2, 3, 4),  # Front face
            (5, 6, 7, 8),  # Back face
            (1, 5, 8, 4),  # Left face
            (2, 6, 7, 3),  # Right face
            (4, 3, 7, 8),  # Top face
            (1, 2, 6, 5),  # Bottom face
        ]
        return vertices, faces

    # Extract X, Y, and Z coordinates from the PLY file
    cubes = []
    for point in points:
        x, y, z = point
        cubes.append(create_cube_3d(x, y, z, size))  # 2 cm cube

    # Write to OBJ file
    with open(output_obj_file_path, 'w') as obj_file:
        vertex_index = 1  # Track vertex indices for faces
        for cube in cubes:
            vertices, faces = cube
            # Write vertices
            for vertex in vertices:
                obj_file.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
            # Write faces (connecting vertices in order)
            for face in faces:
                obj_file.write(f"f {face[0] + vertex_index - 1} {face[1] + vertex_index - 1} "
                               f"{face[2] + vertex_index - 1} {face[3] + vertex_index - 1}\n")
            vertex_index += 8  # Move to the next set of vertices

    print(f"OBJ file created at: {output_obj_file_path}")

    return None









