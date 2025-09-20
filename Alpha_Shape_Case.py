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
        file_path = os.path.join(input_path, individual)
        las = laspy.read(file_path)
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
            base_name, _ = os.path.splitext(individual)
            output_path = os.path.join(script_dir, "Output_Alpha_Shape_Case")
            j_str = str(j).replace('.', '_')

            obj_path = os.path.join(
                output_path,
                str(individual),
                f"{base_name}_alpha_shape_{j_str}_centered.obj"
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
                f"{base_name}_alpha_shape_{j_str}.obj"
            )
            os.makedirs(os.path.dirname(obj_path), exist_ok=True)

            with open(obj_centered_path, "w") as f:
                f.writelines(new_lines)

