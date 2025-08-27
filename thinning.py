import laspy
import numpy as np

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

