A reproduction of the ICSBEP HEU-MET-FAST-001 case 1 benchmark problem using DAGMC with Cubit generated surface meshes. Base OpenMC xml input files are taken from [here](https://github.com/mit-crpg/benchmarks/tree/master/icsbep/heu-met-fast-001/openmc/case-1).

Generate meshes with 
```shell
python mesh_with_cubit.py
```

This generate meshes with deviation angle in (0.5, 1., 2., 3., 4., 5), and the default anisotropic ratio of 100.

To plot the corresponding geometries, do
```shell
python main.py -p
```

To stochastically compute volumes, do
```shell
python main.py -c
```

To perform eigenvalue calculation, do 
```shell
python main.py -r
```

To do all of the above, do
```shell
python main.py -p -c -r
```
