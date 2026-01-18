import os
import numpy as np
import trimesh
import pyrender
from PIL import Image

MODEL_PATH = "toycar_asset/ToyCar.gltf"

OUT_DIR = "frames_y_rotate"
NUM_FRAMES = 120
START_DEG = 0.0
END_DEG = 360.0

W, H = 1280, 720

def look_at(eye, target, up=(0, 1, 0)):
    eye = np.array(eye, dtype=np.float64)
    target = np.array(target, dtype=np.float64)
    up = np.array(up, dtype=np.float64)

    z = target - eye
    z /= (np.linalg.norm(z) + 1e-9)

    x = np.cross(z, up)
    x /= (np.linalg.norm(x) + 1e-9)

    y = np.cross(x, z)
    y /= (np.linalg.norm(y) + 1e-9)

    pose = np.eye(4)
    pose[:3, 0] = x
    pose[:3, 1] = y
    pose[:3, 2] = -z
    pose[:3, 3] = eye
    return pose

def rotation_y(deg):
    rad = np.deg2rad(deg)
    c, s = np.cos(rad), np.sin(rad)

    mat = np.eye(4)
    mat[0, 0] = c
    mat[0, 2] = s
    mat[2, 0] = -s
    mat[2, 2] = c
    return mat

def add_raymond_lighting(scene, center, radius):
    directions = [(1,1,1), (-1,1,1), (0,-1,1)]
    intensities = [2.5, 2.0, 1.8]

    for d, inten in zip(directions, intensities):
        d = np.array(d, dtype=np.float64)
        d /= (np.linalg.norm(d) + 1e-9)
        eye = center - d * radius * 3.0
        light = pyrender.DirectionalLight(color=np.ones(3), intensity=float(inten))
        scene.add(light, pose=look_at(eye, center))

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # 1) load glTF
    tm_scene = trimesh.load(MODEL_PATH, force="scene")
    baked_meshes = tm_scene.dump(concatenate=False)
    if not baked_meshes:
        raise RuntimeError("No meshes found")

    # 2) bounds
    bounds = np.array([m.bounds for m in baked_meshes])
    bmin = bounds[:, 0].min(axis=0)
    bmax = bounds[:, 1].max(axis=0)
    center = (bmin + bmax) * 0.5
    extents = bmax - bmin
    radius = float(np.linalg.norm(extents))
    if radius < 1e-9:
        radius = 1.0

    # 3) scene
    scene = pyrender.Scene(bg_color=[1, 1, 1, 1])
    scene.ambient_light = np.array([0.4, 0.4, 0.4])

    # 4) add meshes (노드로 보관)
    mesh_nodes = []
    for m in baked_meshes:
        mesh = pyrender.Mesh.from_trimesh(m, smooth=True)
        node = scene.add(mesh, pose=np.eye(4))
        mesh_nodes.append(node)

    # 5) lights
    add_raymond_lighting(scene, center, radius)

    # 6) camera (고정)
    camera = pyrender.PerspectiveCamera(yfov=np.deg2rad(45.0))
    cam_eye = center + np.array([radius * 1.5, radius * 0.8, radius * 2.5])
    scene.add(camera, pose=look_at(cam_eye, center))

    # 7) renderer
    r = pyrender.OffscreenRenderer(W, H)

    angles = np.linspace(START_DEG, END_DEG, NUM_FRAMES, endpoint=False)

    for i, deg in enumerate(angles):
        rot = rotation_y(deg)

        for node in mesh_nodes:
            scene.set_pose(node, pose=rot)

        color, depth = r.render(scene)
        out_path = os.path.join(OUT_DIR, f"frame_{i:04d}.png")
        Image.fromarray(color).save(out_path)

        if (i + 1) % 10 == 0:
            print(f"[{i+1}/{NUM_FRAMES}] {out_path}")

    r.delete()
    print("Done:", OUT_DIR)

if __name__ == "__main__":
    main()
