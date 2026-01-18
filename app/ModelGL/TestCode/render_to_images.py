import numpy as np
import trimesh
import pyrender
from PIL import Image

# -----------------------
# 설정
# -----------------------
MODEL_PATH = "toycar_asset/ToyCar.gltf"
OUT_DIR = "frames"
W, H = 1280, 720

FRAME_COUNT = 60        # 총 프레임 수
X_START = 0.0           # 시작 각도
X_END = 180.0           # 끝 각도 (X축 회전)

# -----------------------
# trimesh 로드 (Scene)
# -----------------------
tm_scene = trimesh.load(MODEL_PATH, force="scene")

geoms = list(tm_scene.geometry.values())
if not geoms:
    raise RuntimeError("No geometry found in the loaded Scene.")

merged = trimesh.util.concatenate([g.copy() for g in geoms])

# 센터링
merged.apply_translation(-merged.bounding_box.centroid)

# 스케일 정규화
m = float(np.max(merged.extents))
if m > 0:
    merged.apply_scale(1.0 / m)

# 🔹 회전 전 기본 메시 저장
merged_base = merged.copy()

# -----------------------
# pyrender Scene 구성 (고정 요소)
# -----------------------
scene = pyrender.Scene(
    bg_color=[255, 255, 255, 255],
    ambient_light=[0.15, 0.15, 0.15],
)

# 카메라
camera = pyrender.PerspectiveCamera(yfov=np.deg2rad(45.0))
cam_pose = np.eye(4)
cam_pose[:3, 3] = [0.0, 0.0, 2.2]
scene.add(camera, pose=cam_pose)

# 라이트
light = pyrender.DirectionalLight(color=np.ones(3), intensity=2.5)

def pose_from_dir(direction, distance=2.0):
    direction = np.array(direction, dtype=np.float64)
    direction /= (np.linalg.norm(direction) + 1e-9)
    pos = -direction * distance

    up = np.array([0, 1, 0], dtype=np.float64)
    z = -pos / (np.linalg.norm(pos) + 1e-9)
    x = np.cross(up, z); x /= (np.linalg.norm(x) + 1e-9)
    y = np.cross(z, x)

    M = np.eye(4)
    M[:3, 0] = x
    M[:3, 1] = y
    M[:3, 2] = z
    M[:3, 3] = pos
    return M

scene.add(light, pose=pose_from_dir([ 1,  1,  1]))
scene.add(light, pose=pose_from_dir([-1,  1,  1]))
scene.add(light, pose=pose_from_dir([ 0, -1,  1]))

# -----------------------
# 오프스크린 렌더러
# -----------------------
r = pyrender.OffscreenRenderer(viewport_width=W, viewport_height=H)

# 출력 폴더
import os
os.makedirs(OUT_DIR, exist_ok=True)

# -----------------------
# 프레임 루프 (X축 회전)
# -----------------------
for i in range(FRAME_COUNT):
    angle = np.deg2rad(
        X_START + (X_END - X_START) * i / (FRAME_COUNT - 1)
    )

    mesh = merged_base.copy()

    Rx = trimesh.transformations.rotation_matrix(
        angle=angle,
        direction=[1, 0, 0],
        point=[0, 0, 0],
    )
    mesh.apply_transform(Rx)

    # 이전 메시 제거
    for node in list(scene.mesh_nodes):
        scene.remove_node(node)

    # 새 메시 추가
    pmesh = pyrender.Mesh.from_trimesh(mesh, smooth=False)
    scene.add(pmesh)

    # 렌더
    color, _ = r.render(scene)

    # 저장
    out_path = f"{OUT_DIR}/frame_{i:03d}.png"
    Image.fromarray(color).save(out_path)
    print("Saved:", out_path)

r.delete()
print("Done.")
