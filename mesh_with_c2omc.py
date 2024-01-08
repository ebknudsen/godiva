import os
from data import radii, material_id_to_name, volume_id_to_material_id
import cadquery as cq
from CAD_to_OpenMC import assembly as c2a

if not os.path.exists("h5m"):
    os.makedirs("h5m")
if not os.path.exists("c2omc"):
    os.makedirs("c2omc")

def generate_geometry(aniso, angle):
    cwd = os.getcwd()
    id_to_radius = {}

    volume_count = 0
    cqa = cq.Assembly(name="godiva")
    sphere0=None
    for r in radii:
        if sphere0 is None:
            sphere = cq.Workplane().sphere(r)
        else:
            sphere = cq.Workplane().sphere(r).cut(sphere0)
            sphere0=sphere
        cqa.add(sphere)
        volume_count += 1
        id_to_radius[volume_count] = r

    #export to step
    step_filename=f"{cwd}/c2omc/geometry_angle_{angle}_aniso_{aniso}.step"
    h5m_filename=f"{cwd}/h5m/geometry_angle_{angle}_aniso_{aniso}.h5m"
    cqa.save(step_filename,'STEP')
    
    #mesh
    a=c2a.Assembly([step_filename])
    a.verbose=0
    c2a.mesher_config['threads']=1
    a.cleanup=True
    materials=a.run(
        backend='stl2',
        merge=True,
        h5m_filename=h5m_filename,
        sequential_tags=[ material_id_to_name[volume_id_to_material_id[i+1]] for i in range(len(radii)) ],
        scale=1.0
    )

if __name__ == "__main__":
    aniso = 100
    for angle in [0.5, 1, 2, 3, 4, 5]:
        print(f"GENERATING GEOMETRY WITH angle={angle} aniso={aniso}")
        generate_geometry(aniso=aniso, angle=angle)

