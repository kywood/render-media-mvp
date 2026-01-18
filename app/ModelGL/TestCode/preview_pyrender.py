import trimesh
import pyrender

path = "toycar_asset/ToyCar.gltf"

tm_scene = trimesh.load(path, force="scene")

scene = pyrender.Scene(bg_color=[255, 255, 255, 255])
for g in tm_scene.geometry.values():
    scene.add(pyrender.Mesh.from_trimesh(g, smooth=False))

pyrender.Viewer(scene, use_raymond_lighting=True)


