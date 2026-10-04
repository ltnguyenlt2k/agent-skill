# Repository evidence

Inspect only relevant files outside `.agent-skill/`, upstream/, optional/ and
conditional/. The kit's own package.json files must not classify the host project.
Read package.json dependency keys rather than searching any mention of "React".
React/Next manifests suggest frontend/web; affected files decide whether they matter.
CMake, C++ sources and Qt package references indicate C++/desktop. package.xml alone
is insufficient for ROS2: confirm ament/rclcpp/rclpy. STM32 .ioc, CMSIS, startup,
linker and platformio files suggest embedded. OpenCV/Pylon/Basler/YOLO/ONNX/TensorRT
suggest computer vision only where acquisition/processing/inference is involved.
Backend routes, proxy configuration, containers and CI indicate backend/devops.
Detect multiple domains, then retain only those relevant to the requested outcome.
Do not convert a Qt desktop task into a web implementation.
