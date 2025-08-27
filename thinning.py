import laspy
import numpy as np
import os

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
    las_file = [f for f in os.listdir(input_path) if f.endswith(".las")]
    initial_las_path = os.path.join(input_path, las_file[0])
    os.makedirs("Output_Thinning", exist_ok=True)
    output_path = os.path.join(script_dir, "Output_Thinning")

    txt_file = [f for f in os.listdir(input_path) if f.endswith(".txt")]
    with open(txt_file, "r") as f:
        first_line = f.readline().strip()
        parts = first_line.split()
        percentage = int(parts[1])

    base_name = os.path.splitext(las_file[0])[0]
    output_las_path = os.path.join(output_path, base_name + "_" + str(percentage) + "_thinned.ply")

    func_thinning(initial_las_path, percentage, output_las_path)

if __name__ == "__main__":
    main()