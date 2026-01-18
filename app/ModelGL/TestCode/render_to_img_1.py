import numpy as np
import trimesh
import pyrender
from PIL import Image

MODEL_PATH = "toycar_asset/ToyCar.gltf"
OUT_FILE = "offscreen_like_viewer.png"
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
    pose[:3, 2] = -z   # 카메라가 -Z를 바라보게
    pose[:3, 3] = eye
    return pose

def add_raymond_lighting(scene, center, radius):
    directions = [
        ( 1,  1,  1),
        (-1,  1,  1),
        ( 0, -1,  1),
    ]
    intensities = [2.5, 2.0, 1.8]

    for dir_vec, intensity in zip(directions, intensities):
        direction = np.array(dir_vec, dtype=np.float64)
        direction /= (np.linalg.norm(direction) + 1e-9)

        # 라이트 위치(방향광이라 방향이 중요하지만 pose 계산용으로 위치를 둠)
        eye = center - direction * (radius * 3.0)

        light = pyrender.DirectionalLight(color=np.ones(3), intensity=float(intensity))
        scene.add(light, pose=look_at(eye=eye, target=center))

def main():
    # 1) glTF 로드 (scene graph 유지)
    tm_scene = trimesh.load(MODEL_PATH, force="scene")

    # 2) transform 적용된 mesh들을 추출 (중요!)
    baked_meshes = tm_scene.dump(concatenate=False)

    if not baked_meshes:
        raise RuntimeError("No meshes found in the loaded scene.")

    # 3) baked_meshes 기준으로 bounds/center/radius 계산 (중요!)
    all_bounds = np.array([m.bounds for m in baked_meshes])  # (k,2,3)
    bmin = all_bounds[:, 0, :].min(axis=0)
    bmax = all_bounds[:, 1, :].max(axis=0)

    center = (bmin + bmax) * 0.5
    extents = (bmax - bmin)
    radius = float(np.linalg.norm(extents))  # 대각 길이 기반
    if radius < 1e-9:
        radius = 1.0

    # 4) pyrender scene (bg_color는 0~1 float이 안전)
    scene = pyrender.Scene(bg_color=[1.0, 1.0, 1.0, 1.0])
    scene.ambient_light = np.array([0.4, 0.4, 0.4])

    # 5) geometry 추가 (transform bake된 mesh)
    for m in baked_meshes:
        # smooth=True가 더 보기 좋은 경우가 많음(원하면 False로)
        scene.add(pyrender.Mesh.from_trimesh(m, smooth=True))

    # 6) lights
    add_raymond_lighting(scene, center, radius)

    # 7) camera (비스듬한 위치 + 충분한 거리)
    camera = pyrender.PerspectiveCamera(yfov=np.deg2rad(45.0))
    cam_eye = center + np.array([radius * 1.5, radius * 0.8, radius * 2.2])
    scene.add(camera, pose=look_at(eye=cam_eye, target=center))

    # 8) render
    r = pyrender.OffscreenRenderer(W, H)
    color, depth = r.render(scene)
    r.delete()

    print("color min/max:", int(color.min()), int(color.max()))
    print("depth min/max:", float(np.min(depth)), float(np.max(depth)))

    Image.fromarray(color).save(OUT_FILE)
    print("Saved:", OUT_FILE)

if __name__ == "__main__":
    main()
