import laspy
import numpy as np


def func_remove_indices(las_path, indices_to_remove, combined_deletion, tree_crown_las):
    las = laspy.read(las_path)

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

