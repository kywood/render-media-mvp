# render-media-mvp


PyOpenGL / GLFW 와 비교
항목	ModernGL	PyOpenGL + GLFW
성격	고수준 래퍼	저수준 바인딩
윈도우 필요	❌ (standalone 가능)	✅ 필요
서버 적합성	⭐⭐⭐⭐⭐	⭐⭐
초기 진입	쉬움	상대적으로 어려움
디버깅	간단	컨텍스트/스레드 이슈 잦음

👉 “서버에서 돌릴 3D 스트리밍”이면 ModernGL이 정답에 가까움




ModernGL + EGL(OSMesa) + FFmpeg

오프스크린 3D 렌더링

ModernGL

OpenGL 직접 다루지 않아도 됨

FBO(FrameBuffer) 기본 지원

fbo.read() → numpy bytes 바로 뽑힘

서버/헤드리스 렌더링에 최적


EGL (Linux/WSL/서버)

(Windows 로컬 테스트는 GLFW로 시작해도 OK)

👉 ModernGL은 EGL 컨텍스트를 공식 지원


H.264 인코딩

FFmpeg

사실상 표준

stdin 파이프 입력 가능

libx264 / h264_nvenc 선택 가능


