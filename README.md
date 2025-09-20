# Thesis_Victoria_Tsalapati
This repository contains the executables used to generate geometric 3D tree representations for this research, including methods based on point cloud, convex hull, alpha shapes, and voxel grids.

## Usage
### Prerequisites

- Python 3.11
- Libraries: laspy, numpy, open3d, scikit-learn, trimesh, alphashape, shapely 
- LiDAR data in '.LAS' or '.LAZ' format

## Tree 3D representations
### Point Cloud Case

- Place the input point cloud data in the **Input_Point_Cloud_Case** folder
- Run *main_Point_Cloud_Case.py* 
- Access the results in the **Output_Point_Cloud_Case** folder:
  1. PLY file of the input point cloud,
  2. OBJ file of the point cloud representation,
  3. TXT file containing the processing duration.

### Alpha Shape Case

- Place the input point cloud files of separated trees in the **Input_Alpha_Shape_Case** folder
- Run *Alpha_Shape_Case.py* 
- Access the results per each individual tree inside the **Output_Alpha_Shape_Case/<name_of_las_file>** folder:
  1. OBJ file of centered points of each alpha parameters (0.5, 1.0, 1.5)
  2. OBJ file of uncentered points of each alpha parameters (0.5, 1.0, 1.5)


### Convex Hull Case
 

