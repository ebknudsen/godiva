import cubit
import os
from data import radii, material_id_to_name, volume_id_to_material_id
cubit.init(['cubit', '-nojournal'])

def generate_geometry(aniso, angle):
    cwd = os.getcwd()
    cmd = cubit.cmd
    cmd("reset")
    id_to_radius = {}

    volume_count = 0
    for r in radii:
        cmd(f"create sphere radius {r}")
        volume_count += 1
        id_to_radius[volume_count] = r

    for i in range(10, 1, -1):
        cmd(f"subtract volume {i-1} from volume {i} keep_tool")
        last_id = cubit.get_last_id("volume")
        cmd(f"Volume {last_id} Id {i}")

    cmd("merge tolerance 0.0005")
    cmd("imprint volume all")
    cmd("merge volume all")

    for mat, matname in material_id_to_name.items():
        cmd(f'create material "{matname}" property_group "CUBIT-ABAQUS"')

    for vol, mat in volume_id_to_material_id.items():
        matname = material_id_to_name[mat]
        cmd('set duplicate block elements off')
        cmd(f'block {mat} add volume {vol}')
        cmd(f'block {mat} name "{matname}"')
        cmd(f'block {mat} material "{matname}"')

    cmd(f'set trimesher coarse on ratio {aniso} angle {angle}')
    cmd('surface all scheme trimesh')
    cmd('mesh surface all')

    cmd(f'save cub5 "{cwd}/cub5/geometry_angle_{angle}_aniso_{aniso}.cub5" overwrite journal')
    cmd(f'export cf_dagmc "{cwd}/h5m/geometry_angle_{angle}_aniso_{aniso}.h5m"  overwrite')


if __name__ == "__main__":
    aniso = 100
    for angle in [0.5, 1, 2, 3, 4, 5]:
        print(f"GENERATING GEOMETRY WITH angle={angle} aniso={aniso}")
        generate_geometry(aniso=aniso, angle=angle)

