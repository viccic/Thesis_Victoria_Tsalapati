import laspy
import numpy as np
import os

def func_cropping(input_las_path, min_x, max_x, min_y, max_y, cropped_las_file_path):

    # Load LAS file
    las = laspy.read(input_las_path)

    # Define the bounding box
    mask = ((las.x >= min_x) & (las.x <= max_x) & (las.y >= min_y) & (las.y <= max_y))

    # Filter points based on the bounding box
    cropped = laspy.create(point_format=las.header.point_format, file_version=las.header.version)
    cropped.header = las.header
    cropped.points = las.points[mask]

    # Write the cropped LAS file
    cropped.write(cropped_las_file_path)

def func_thinning(input_las_path, percentage, output_las_path):
    # Load LAS file
    inFile = laspy.read(input_las_path)

    # Select a percentage of points
    fraction = percentage/100
    indices = np.random.choice(len(inFile.points), int(len(inFile.points) * fraction), replace=False)

    # Create new LAS file with selected points
    outFile = laspy.create(point_format=inFile.header.point_format, file_version=inFile.header.version)
    outFile.points = inFile.points[indices]
    outFile.header = inFile.header
    outFile.write(output_las_path)

def main():

    # Define the location of files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, "Input_Thinning")
    laz_file = [f for f in os.listdir(input_path) if f.lower().endswith(".laz")]
    initial_las_path = os.path.join(input_path, laz_file[0])
    os.makedirs("Output_Thinning", exist_ok=True)
    output_path = os.path.join(script_dir, "Output_Thinning")

    # Define the location of boundaries
    boundaries_path = os.path.join(input_path, "Cropping_Boundaries.txt")
    with open(boundaries_path, "r", encoding="utf-8") as f:
        first_line = f.readline().strip().split()
        second_line = f.readline().strip().split()

    min_x = float(first_line[2].replace(",", ""))
    max_x = float(first_line[3])
    min_y = float(second_line[2].replace(",", ""))
    max_y = float(second_line[3])

    # build output filename with same basename but .las (or .ply, etc.)
    base_name, _ = os.path.splitext(laz_file[0])

    crop_path = os.path.join(output_path, f"{base_name}_cropped.las")

    # Cropping the laz file
    func_cropping(initial_las_path, min_x, max_x, min_y, max_y, crop_path)

    # Define the thinning percentage
    perc_path = os.path.join(input_path, "Thinning_Percentage.txt")
    with open(perc_path, "r", encoding="utf-8") as f:
        parts = f.readline().strip().split()
    percentage = int(parts[1])

    output_las_path = os.path.join(output_path, f"{base_name}_thinned_{percentage}.las")

    # Thinning the las file
    func_thinning(initial_las_path, percentage, output_las_path)

if __name__ == "__main__":
    main()