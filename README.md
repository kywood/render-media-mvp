# render-media-mvp


PyOpenGL / GLFW 와 비교
항목	ModernGL	PyOpenGL + GLFW
성격	고수준 래퍼	저수준 바인딩
윈도우 필요	❌ (standalone 가능)	✅ 필요
서버 적합성	⭐⭐⭐⭐⭐	⭐⭐
초기 진입	쉬움	상대적으로 어려움
디버깅	간단	컨텍스트/스레드 이슈 잦음

👉 “서버에서 돌릴 3D 스트리밍”이면 ModernGL이 정답에 가까움
