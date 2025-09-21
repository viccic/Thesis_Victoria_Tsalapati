# Thesis_Victoria_Tsalapati
This repository contains the executables used to generate geometric 3D tree representations for this research, including methods based on point cloud, convex hull, alpha shapes, and voxel grids.

## Usage
### Prerequisites

- Python 3.11
- Libraries: laspy, numpy, open3d, scikit-learn, trimesh, alphashape, shapely 
- LiDAR data in '.LAS' or '.LAZ' format

## Tree 3D representations
### Point Cloud Case

- Place the input point cloud in the **Input_Point_Cloud_Case** folder
- Run *main_Point_Cloud_Case.py* 
- Access the results in the **Output_Point_Cloud_Case** folder:
  1. PLY file of the input point cloud,
  2. OBJ file of the point cloud representation,
  3. TXT file containing the processing duration.

### Alpha Shape Case

- Place the input point cloud files of separated trees in the **Input_Alpha_Shape_Case** folder
- Run *Alpha_Shape_Case.py* 
- Access the results per each individual tree inside the **Output_Alpha_Shape_Case/<name_of_las_file>** folder:
  1. OBJ file of centered points of each alpha parameters (0.5, 1.0, 1.5),
  2. OBJ file of uncentered points of each alpha parameters (0.5, 1.0, 1.5) (these files were used for the simulations)


### Convex Hull Case

- Place the input point cloud and complete the parameters of DBSCAN (maximum distance and minimum sample points), height and radius of inner and outer ring of the annulus and spacing value (use exactly this order) in **Parameters_DBSCAN.txt** in the **Input_Convex_Hull_Case** folder
- Run *main_Convex_Hull_Case.py* 
- Receive `<name of input point cloud file>_Cropped_low.las`, PNG file of the estimated clusters and *labelled_las* and *annuli* folder (clustered lower points and the corresponding highest annulus).
- Insert the indices of clusters in descending order to be removed (inspect clusters (e.g., in CloudCompare), collect the indices that are not stem and collect the indices of the annuli that include them)
- Access the results the **Output_Convex_Hull_Case** folder:
  1. `<name of input point cloud file>_Tree_crown.las`
  2. `<name of input point cloud file>_Tree_crown.ply`
  3. `<name of input point cloud file>__Tree_Crown_convex_hull.obj`

 
### Voxel Grid Case (1rst approach) for trees with canopy

- Place the input point cloud files of trees without leaves (named as *Branches.las* or configure the las name) and of leaves (named as *Leaves.las* or configure the las name) in the **Input_Voxel_Grid_Case_1rst_Approach** folder
- Run *main_Voxel_Grid_Case_1rst_Approach.py* 
- Access the results per voxel size inside the **Output_Voxel_Grid_Case_1rst_Approach** folder:
  1. XYZ files of *Branches.las* and *Leaves.las*, 
  2. LAS file of `leaves_converted.las` (LAS file of leaves with only the following fields: X, Y, Z, intensity and label,
  3. LAS file of `SyntheticLAS.las` (LAS file branches and leaves with only the following fields: X, Y, Z, intensity and label,
  4. PNG file of plot of processing duration per voxel size
  
  and for each voxel size:
  1. OBJ file of `voxels_<voxel size>_leaves.obj` ,
  2. OBJ file of `voxels_<voxel size>_branches.obj`,
  3. TXT file containing the information about the voxel grid (maximum and minimum number of points inside a voxel, number of leaves and branches voxels),
  4. TXT file containing the processing duration.
  
### Voxel Grid Case (2nd approach)

- Place the input point cloud in the **Input_Voxel_Grid_Case_2nd_Approach** folder
- Run *main_Voxel_Grid_Case_2nd_Approach.py* 
- Access the results per voxel size and inside the **Output_Voxel_Grid_Case_2nd_Approach** folder:
  1. XYZ file of point cloud,
  2. PNG file of plot of processing duration per voxel size
  
  and for each voxel size and number of grid:
  1. OBJ file of `"voxels_<voxel size>_<number of grid>_m.obj"`,
  2. TXT file containing the information about the voxel grid (maximum and minimum number of points inside a voxel, number of voxels per grid),
  3. TXT file containing the processing duration.