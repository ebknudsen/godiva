import openmc
import argparse
import numpy as np
from glob import glob
import os
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from data import material_volumes, radii

def clean():
    paths = glob("*h5") + glob("*.xml")
    for p in paths:
        os.remove(p)

def get_avail():
    paths = os.listdir("h5m")
    params = []
    for path in paths:
        strings = path.split("_")
        params.append((strings[2], strings[4].split(".")[0]))
    return params

def generate_csg():
    materials = openmc.Materials.from_xml("xml/materials.xml")
    settings = openmc.Settings.from_xml("xml/settings.xml")
    geometry = openmc.Geometry.from_xml("xml/geometry.xml", materials=materials)
    r = radii[-1]
    vol_calc = openmc.VolumeCalculation(
        [mat for mat in materials],
        10_000_000,
        upper_right=(r, r, r),
        lower_left=(-r, -r, -r),
    )
    settings.volume_calculations = [vol_calc]

    material_plot = openmc.Plot()
    material_plot.origin = (0.0, 0.0, 0.0)
    material_plot.basis = "xy"
    material_plot.width = (20, 20)
    material_plot.color_by = "material"
    material_plot.pixels = (5000, 5000)
    material_plot.filename = f"plots/material_csg.png"

    cell_plot = openmc.Plot()
    cell_plot.origin = (0.0, 00.0, 0.0)
    cell_plot.basis = "xy"
    cell_plot.width = (20, 20)
    cell_plot.color_by = "cell"
    cell_plot.pixels = (5000, 5000)
    cell_plot.filename = f"plots/cell_csg.png"
    plots = openmc.Plots(plots=[material_plot, cell_plot])

    model = openmc.Model(
        geometry=geometry, materials=materials, settings=settings, plots=plots
    )
    return model

def generate_cad(angle, aniso):
    materials = openmc.Materials.from_xml("xml/materials.xml")
    settings = openmc.Settings.from_xml("xml/settings.xml")
    # settings.verbosity = 1

    dag_univ = openmc.DAGMCUniverse(
        f"h5m/geometry_angle_{angle}_aniso_{aniso}.h5m", auto_geom_ids=True
    )
    sphere = openmc.Sphere(r=radii[-1], boundary_type="vacuum")
    cell = openmc.Cell(region=-sphere, fill=dag_univ)
    root = openmc.Universe(cells=[cell])
    geometry = openmc.Geometry(root=root)
    geometry.export_to_xml()

    r = radii[-1]
    vol_calc = openmc.VolumeCalculation(
        [mat for mat in materials],
        10_000_000,
        upper_right=(r, r, r),
        lower_left=(-r, -r, -r),
    )
    settings.volume_calculations = [vol_calc]

    material_plot = openmc.Plot()
    material_plot.origin = (0.0, 0.0, 0.0)
    material_plot.basis = "xy"
    material_plot.width = (20, 20)
    material_plot.color_by = "material"
    material_plot.pixels = (5000, 5000)
    material_plot.filename = f"plots/material_angle_{angle}_aniso_{aniso}.png"

    cell_plot = openmc.Plot()
    cell_plot.origin = (0.0, 00.0, 0.0)
    cell_plot.basis = "xy"
    cell_plot.width = (20, 20)
    cell_plot.color_by = "cell"
    cell_plot.pixels = (5000, 5000)
    cell_plot.filename = f"plots/cell_angle_{angle}_aniso_{aniso}.png"
    plots = openmc.Plots(plots=[material_plot, cell_plot])

    model = openmc.Model(
        geometry=geometry, materials=materials, settings=settings, plots=plots
    )
    return model


def plots(angle=None, aniso=None):
    if not os.path.exists("plots"):
        os.makedirs("plots")
    for angle, aniso in get_avail():
        model = generate_cad(angle, aniso)
        model.export_to_model_xml(remove_surfs=True)
        openmc.plot_geometry()
    model = generate_csg()
    model.export_to_model_xml()
    openmc.plot_geometry()

def run():
    results = []
    # RUNNING CSG MODES
    model = generate_csg()
    model.export_to_model_xml(remove_surfs=True)
    openmc.run()
    with openmc.StatePoint(f"statepoint.{model.settings.batches}.h5") as sp:
        mean = sp.keff.n
        std = sp.keff.std_dev
    results.append(["CSG", "CSG", mean, std])
    clean()

    # RUNNING CAD MODELS
    for angle, aniso in get_avail():
        print(angle, aniso)
        model = generate_cad(angle, aniso)
        model.export_to_model_xml(remove_surfs=True)
        try:
            openmc.run()
            with openmc.StatePoint(f"statepoint.{model.settings.batches}.h5") as sp:
                mean = sp.keff.n
                std = sp.keff.std_dev
            results.append([angle, aniso, mean, std])
        except RuntimeError:
            print(
                f"Calculation with angle={angle} aniso={aniso} could not complete."
            )
            results.append([angle, aniso, "error", "error"])
        clean()

    df = pd.DataFrame(data=results, columns=["angle", "aniso", "keff", "sig_keff"])
    df.to_csv("keff.csv", index=False)


def volumes():
    data = []
    index = []
    for mat, volume in material_volumes.items():
        index.append((mat, "EXACT", "EXACT"))
        data.append([volume, 0., 0.])

    # RUNNING CSG MODEL
    cwd = "."
    model = generate_csg()
    model.export_to_model_xml(path=f"{cwd}/model.xml", remove_surfs=True)
    openmc.calculate_volumes(cwd=cwd)
    vol = openmc.VolumeCalculation.from_hdf5(f'{cwd}/volume_1.h5').volumes
    vol = {model.materials[i-1].name: value for i, value in vol.items()}
    for mat, volume in vol.items():
        error = (volume.n - material_volumes[mat]) / material_volumes[mat] * 100
        index.append((mat, "CSG", "CSG"))
        data.append([volume.n, volume.s, error])

    # RUNNING CAD MODELS
    for angle, aniso in get_avail():
        model = generate_cad(angle, aniso)
        model.export_to_model_xml(path=f"{cwd}/model.xml", remove_surfs=True)
        openmc.calculate_volumes(cwd)
        vol = openmc.VolumeCalculation.from_hdf5(f'{cwd}/volume_1.h5').volumes
        vol = {model.materials[i-1].name: value for i, value in vol.items()}
        for mat, volume in vol.items():
            error = (volume.n - material_volumes[mat]) / material_volumes[mat] * 100
            index.append((mat, angle, aniso))
            data.append([volume.n, volume.s, error])
        clean()

    multiindex = pd.MultiIndex.from_tuples(index, names=["material", "angle", "aniso"])
    df = pd.DataFrame(data=data, columns=["volume", "sigvolume", "error_percent"], index=multiindex)
    df.sort_index(inplace=True)
    df.to_csv("volumes.csv")
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--calculate_volume', action='store_true', )
    parser.add_argument('-r', '--run', action='store_true', )
    parser.add_argument('-p', '--plot', action='store_true', )
    args = parser.parse_args()
    if args.calculate_volume:
        print(volumes())
    if args.plot:
        plots()
    if args.run:
        run()
