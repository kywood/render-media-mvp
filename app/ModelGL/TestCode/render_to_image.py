import numpy as np
import trimesh
import pyrender
from PIL import Image

# -----------------------
# 설정
# -----------------------
MODEL_PATH = "toycar_asset/ToyCar.gltf"   # 또는 ToyCar_fixed.glb
OUT_FILE = "frame_0001.png"
W, H = 1280, 720

X_DEG = 90.0   # 뒤집혀 있으면 90 또는 -90 중 하나로 맞추기
# X_DEG = -90.0

# -----------------------
# trimesh 로드 (Scene)
# -----------------------
tm_scene = trimesh.load(MODEL_PATH, force="scene")

# 전체 geometry를 하나로 합쳐서 중심/스케일 계산
geoms = list(tm_scene.geometry.values())
if not geoms:
    raise RuntimeError("No geometry found in the loaded Scene.")

merged = trimesh.util.concatenate([g.copy() for g in geoms])

# 1) 센터링
merged.apply_translation(-merged.bounding_box.centroid)

# 2) 스케일 정규화 (가장 긴 변을 1로)
m = float(np.max(merged.extents))
if m > 0:
    merged.apply_scale(1.0 / m)

# 3) X축 회전(보정/연출)
Rx = trimesh.transformations.rotation_matrix(
    angle=np.deg2rad(X_DEG),
    direction=[1, 0, 0],
    point=[0, 0, 0],
)
merged.apply_transform(Rx)

# -----------------------
# pyrender Scene 구성
# -----------------------
scene = pyrender.Scene(bg_color=[255, 255, 255, 255], ambient_light=[0.15, 0.15, 0.15])

# 텍스처/머티리얼 포함해서 pyrender mesh로 변환
pmesh = pyrender.Mesh.from_trimesh(merged, smooth=False)
scene.add(pmesh)

# -----------------------
# 카메라 설정
# -----------------------
camera = pyrender.PerspectiveCamera(yfov=np.deg2rad(45.0))
cam_pose = np.eye(4)
cam_pose[:3, 3] = [0.0, 0.0, 2.2]  # 카메라 거리 (검게 나오면 3.0~6.0으로 늘려봐)
scene.add(camera, pose=cam_pose)

# -----------------------
# 라이트(= raymond lighting 비슷하게 3개 방향광)
# -----------------------
light = pyrender.DirectionalLight(color=np.ones(3), intensity=2.5)

def pose_from_dir(direction, distance=2.0):
    # direction: 빛이 "오는" 방향(대략). 라이트는 -Z를 비추는 개념이라 간단히 카메라처럼 배치.
    direction = np.array(direction, dtype=np.float64)
    direction = direction / (np.linalg.norm(direction) + 1e-9)
    pos = -direction * distance

    # look_at 행렬 만들기(라이트가 원점을 보게)
    up = np.array([0, 1, 0], dtype=np.float64)
    z = (np.array([0, 0, 0], dtype=np.float64) - pos)
    z /= (np.linalg.norm(z) + 1e-9)
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
# 오프스크린 렌더 → PNG 저장
# -----------------------
r = pyrender.OffscreenRenderer(viewport_width=W, viewport_height=H)
color, depth = r.render(scene)
r.delete()

#
# gamma = 2.2
# img = (color.astype(np.float32) / 255.0) ** (1.0 / gamma)
# color = (np.clip(img, 0.0, 1.0) * 255.0).astype(np.uint8)

# color는 (H, W, 3) uint8
Image.fromarray(color).save(OUT_FILE)
print("Saved:", OUT_FILE)
