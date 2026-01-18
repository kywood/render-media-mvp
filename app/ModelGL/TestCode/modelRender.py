
import json
import os
import urllib.request
from pathlib import Path


BASE = "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/master/Models/ToyCar/glTF/"
OUT_DIR = Path("toycar_asset")

def dl(url: str, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return
    print("download:", url)
    urllib.request.urlretrieve(url, dst)

def main():
    OUT_DIR.mkdir(exist_ok=True)

    # 1) glTF 다운로드
    gltf_name = "ToyCar.gltf"
    gltf_path = OUT_DIR / gltf_name
    dl(BASE + gltf_name, gltf_path)

    # 2) glTF 파싱해서 참조 파일(텍스처/바이너리) 전부 다운로드
    gltf = json.loads(gltf_path.read_text(encoding="utf-8"))
    uris = set()

    for img in gltf.get("images", []):
        uri = img.get("uri")
        if uri and not uri.startswith("data:"):
            uris.add(uri)

    for buf in gltf.get("buffers", []):
        uri = buf.get("uri")
        if uri and not uri.startswith("data:"):
            uris.add(uri)

    for uri in sorted(uris):
        dl(BASE + uri, OUT_DIR / uri)

    print("\nOK. Saved to:", OUT_DIR.resolve())
    print("Main glTF:", (OUT_DIR / gltf_name).resolve())

    pass


if __name__ == '__main__':
    main()