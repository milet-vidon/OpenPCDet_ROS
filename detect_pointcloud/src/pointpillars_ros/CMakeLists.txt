cmake_minimum_required(VERSION 3.8)
project(pointpillars_ros)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(jsk_recognition_msgs REQUIRED)
find_package(pointpillars_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(eigen3_cmake_module REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(PCL REQUIRED COMPONENTS common io filters)
# find_package(pcl_conversions REQUIRED)
find_package(PCL 1.12 REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
install(PROGRAMS
  tools/ros.py
  DESTINATION lib/${PROJECT_NAME}
)
install(PROGRAMS
  tools/bag2cloud.py 
  DESTINATION lib/${PROJECT_NAME}
)
add_executable(bbox_tracker_node src/bbox_tracker_node.cpp)
target_include_directories(bbox_tracker_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
  ${Eigen3_INCLUDE_DIRS}
)

# 2. 链接依赖库
ament_target_dependencies(bbox_tracker_node
  rclcpp
  std_msgs
  jsk_recognition_msgs
  geometry_msgs
  pointpillars_msgs
  nav_msgs
  visualization_msgs
  tf2
  tf2_ros
  tf2_geometry_msgs
  Eigen3
)
# -------------------------------------------------

# 安装可执行文件
install(TARGETS
  bbox_tracker_node
  DESTINATION lib/${PROJECT_NAME}
)
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)


if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
