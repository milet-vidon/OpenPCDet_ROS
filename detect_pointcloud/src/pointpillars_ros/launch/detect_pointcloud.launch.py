from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # 获取 pointpillars_ros 包的共享目录路径
    pointpillars_ros_dir = get_package_share_directory('pointpillars_ros')
    
    # 定义 rviz 配置文件的路径
    rviz_config_path = os.path.join(pointpillars_ros_dir, 'launch', 'pointpillars.rviz')

    return LaunchDescription([
        # 启动 bbox_tracker_node
        Node(
            package='pointpillars_ros',
            executable='bbox_tracker_node',
            name='bbox_tracker_node',
            output='screen'
        ),
        # 启动 pointpillars_ros 节点 (ros.py)
        Node(
             package='pointpillars_ros',
    executable='ros.py',
    name='pointpillars_ros',
    output='screen',
    # ... 其他 parameters 等
    # 关键改动：在运行 ros.py 之前，先激活 ros_visual 环境
   
        ),
        # 启动 rviz2
        # Node(
        #     package='rviz2',
        #     executable='rviz2',
        #     name='rviz2',
        #     arguments=['-d', rviz_config_path],
        #     output='screen'
        # )
    ])
