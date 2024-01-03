import numpy as np
radii = np.array([1.0216, 1.0541, 6.2809, 6.2937, 7.7525, 7.7620, 8.2527, 8.2610, 8.7062, 8.7499])
volumes = radii**3 * np.pi * 4/3
volumes[1:] = volumes[1:] - volumes[:-1]

material_id_to_name = {
    1: "Shell_1",
    2: "Shell_2",
    3: "Shell_3",
    4: "Shell_4",
    5: "Shell_5",
    6: "Shell_6",
    7: "Air"
    }
volume_id_to_material_id = {1: 1, 2: 7, 3: 2, 4: 7, 5: 3, 6: 7, 7: 4, 8: 7, 9: 5, 10: 6}
material_volumes = {name: 0 for name in material_id_to_name.values()}
for ivol, imat in volume_id_to_material_id.items():
    mat = material_id_to_name[imat]
    material_volumes[mat] += volumes[ivol-1]
