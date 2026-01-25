#!/usr/bin/env python3

# import rospy
# from sensor_msgs.msg import PointCloud2
# import sensor_msgs.point_cloud2 as pc2
# from std_msgs.msg import Header
# from jsk_recognition_msgs.msg import BoundingBox, BoundingBoxArray

# import time
# import numpy as np
# from pyquaternion import Quaternion

# import argparse
# import glob
# from pathlib import Path

# import mayavi.mlab as mlab
# import numpy as np
# import torch
# import scipy.linalg as linalg

# import sys
# sys.path.append("/home/kang/PointPillars_ROS/src/pointpillars_ros")

# from pcdet.config import cfg, cfg_from_yaml_file
# from pcdet.datasets import DatasetTemplate
# from pcdet.models import build_network, load_data_to_gpu
# from pcdet.utils import common_utils

# class DemoDataset(DatasetTemplate):
#     def __init__(self, dataset_cfg, class_names, training=True, root_path=None, logger=None, ext='.bin'):
#         """
#         Args:
#             root_path: 根目录
#             dataset_cfg: 数据集配置
#             class_names: 类别名称
#             training: 训练模式
#             logger: 日志
#             ext: 扩展名
#         """
#         super().__init__(
#             dataset_cfg=dataset_cfg, class_names=class_names, training=training, root_path=root_path, logger=logger
#         )
        


# class Pointpillars_ROS:
#     def __init__(self):
#         config_path, ckpt_path = self.init_ros()
#         self.init_pointpillars(config_path, ckpt_path)


#     def init_ros(self):
#         """ Initialize ros parameters """
#         config_path = rospy.get_param("/config_path", "/home/kang/PointPillars_ROS/src/pointpillars_ros/cfgs/custom_models/custom.yaml")
#         ckpt_path = rospy.get_param("/ckpt_path", "/home/kang/PointPillars_ROS/src/pointpillars_ros/models/checkpoint_epoch_80.pth")
#         self.sub_velo = rospy.Subscriber("/cloud_registered", PointCloud2, self.lidar_callback, queue_size=1,  buff_size=2**12)
#         self.pub_bbox = rospy.Publisher("/detections", BoundingBoxArray, queue_size=1)
#         return config_path, ckpt_path


#     def init_pointpillars(self, config_path, ckpt_path):
#         """ Initialize second model """
#         import os
#         os.chdir("/home/kang/PointPillars_ROS/src/pointpillars_ros")
#         logger = common_utils.create_logger() # 创建日志
#         logger.info('-----------------Quick Demo of Pointpillars-------------------------')
#         cfg_from_yaml_file(config_path, cfg)  # 加载配置文件
        
#         self.demo_dataset = DemoDataset(
#             dataset_cfg=cfg.DATA_CONFIG, class_names=cfg.CLASS_NAMES, training=False,
#             ext='.bin', logger=logger
#         )
#         self.model = build_network(model_cfg=cfg.MODEL, num_class=len(cfg.CLASS_NAMES), dataset=self.demo_dataset)
#         # 加载权重文件
#         self.model.load_params_from_file(filename=ckpt_path, logger=logger, to_cpu=True)
#         self.model.cuda() # 将网络放到GPU上
#         self.model.eval() # 开启评估模式


#     def rotate_mat(self, axis, radian):
#         rot_matrix = linalg.expm(np.cross(np.eye(3), axis / linalg.norm(axis) * radian))
#         return rot_matrix


#     def lidar_callback(self, msg):
#         """ Captures pointcloud data and feed into second model for inference """
#         pcl_msg = pc2.read_points(msg, skip_nans=True, field_names=("x", "y", "z","intensity","ring"))
#         np_p = np.array(list(pcl_msg), dtype=np.float32)
#         # 旋转轴
#         rand_axis = [0,1,0]  # y轴
#         #旋转角度0.1047
#         yaw =  0
#         #返回旋转矩阵
#         rot_matrix = self.rotate_mat(rand_axis, yaw)  # 绕y轴旋转的旋转矩阵
#         np_p_rot = np.dot(rot_matrix, np_p[:,:3].T).T
        
#         # convert to xyzi point cloud
#         x = np_p_rot[:, 0].reshape(-1)
#         y = np_p_rot[:, 1].reshape(-1)
#         z = np_p_rot[:, 2].reshape(-1)
#         if np_p.shape[1] == 4: # if intensity field exists
#             i = np_p[:, 3].reshape(-1)
#         else:
#             i = np.zeros((np_p.shape[0], 1)).reshape(-1)
#         points = np.stack((x, y, z, i)).T
#         print(points.shape)
#         # 组装数组字典
#         input_dict = {
#             'points': points,
#             'frame_id': 0,
#         }
#         data_dict = self.demo_dataset.prepare_data(data_dict=input_dict) # 数据预处理
#         data_dict = self.demo_dataset.collate_batch([data_dict])
#         load_data_to_gpu(data_dict) # 将数据放到GPU上
#         pred_dicts, _ = self.model.forward(data_dict) # 模型前向传播
#         boxes_lidar = pred_dicts[0]['pred_boxes'].detach().cpu().numpy()
#         scores = pred_dicts[0]['pred_scores'].detach().cpu().numpy()
#         label = pred_dicts[0]['pred_labels'].detach().cpu().numpy()
#         num_detections = boxes_lidar.shape[0]
#         rospy.loginfo("The num is: %d ", num_detections)

#         # print(boxes_lidar)
#         # print(scores)
#         # print(label)

#         arr_bbox = BoundingBoxArray()  # 创建BoundingBoxArray消息
#         for i in range(num_detections):
#             bbox = BoundingBox()

#             bbox.header.frame_id = msg.header.frame_id
#             bbox.header.stamp = rospy.Time.now()
#             bbox.pose.position.x = float(boxes_lidar[i][0])
#             bbox.pose.position.y = float(boxes_lidar[i][1])
#             # bbox.pose.position.z = float(boxes_lidar[i][2]) + float(boxes_lidar[i][5]) / 2
#             bbox.pose.position.z = float(boxes_lidar[i][2])
#             bbox.dimensions.x = float(boxes_lidar[i][3])  # width
#             bbox.dimensions.y = float(boxes_lidar[i][4])  # length
#             bbox.dimensions.z = float(boxes_lidar[i][5])  # height
#             q = Quaternion(axis=(0, 0, 1), radians=float(boxes_lidar[i][6]))
#             bbox.pose.orientation.x = q.x
#             bbox.pose.orientation.y = q.y
#             bbox.pose.orientation.z = q.z
#             bbox.pose.orientation.w = q.w
#             bbox.value = scores[i]
#             bbox.label = label[i]
#             print(bbox.label)

#             arr_bbox.boxes.append(bbox)
        
#         arr_bbox.header.frame_id = msg.header.frame_id
#         arr_bbox.header.stamp = rospy.Time.now()
        
#         self.pub_bbox.publish(arr_bbox)


# if __name__ == '__main__':
#     sec = Pointpillars_ROS()
#     rospy.init_node('pointpillars_ros_node', anonymous=True)
#     try:
#         rospy.spin()
#     except KeyboardInterrupt:
#         del sec
#         print("Shutting down")


# import rospy
# from sensor_msgs.msg import PointCloud2
# import sensor_msgs.point_cloud2 as pc2
# from std_msgs.msg import Header
# from jsk_recognition_msgs.msg import BoundingBox, BoundingBoxArray

# import time
# import numpy as np
# from pyquaternion import Quaternion

# import argparse
# import glob
# from pathlib import Path

# import mayavi.mlab as mlab
# import numpy as np
# import torch
# import scipy.linalg as linalg

# import sys
# sys.path.append("/home/ubuntu/PointPillars_ROS/src/pointpillars_ros")
# # 定义要保留的目标标签（例如只保留 label=1 的检测框，多个标签用逗号分隔，如 [1,3]）
# TARGET_LABELS = [1]  # 关键：替换为你需要保留的标签

# from pcdet.config import cfg, cfg_from_yaml_file
# from pcdet.datasets import DatasetTemplate
# from pcdet.models import build_network, load_data_to_gpu
# from pcdet.utils import common_utils

# class DemoDataset(DatasetTemplate):
#     def __init__(self, dataset_cfg, class_names, training=True, root_path=None, logger=None, ext='.bin'):
#         """
#         Args:
#             root_path: 根目录
#             dataset_cfg: 数据集配置
#             class_names: 类别名称
#             training: 训练模式
#             logger: 日志
#             ext: 扩展名
#         """
#         super().__init__(
#             dataset_cfg=dataset_cfg, class_names=class_names, training=training, root_path=root_path, logger=logger
#         )
        


# class Pointpillars_ROS:
#     def __init__(self):
#         # 初始化计时变量
#         self.total_inference_time = 0.0
#         self.total_preprocessing_time = 0.0
#         self.frame_count = 0
#         self.avg_inference_time = 0.0
#         self.avg_preprocessing_time = 0.0
#         self.avg_fps = 0.0
        
#         config_path, ckpt_path = self.init_ros()
#         self.init_pointpillars(config_path, ckpt_path)


#     def init_ros(self):
#         """ Initialize ros parameters """
#         config_path = rospy.get_param("/config_path", "/home/ubuntu/detect_pointcloud/src/pointpillars_ros/cfgs/custom_models/custom.yaml")
#         ckpt_path = rospy.get_param("/ckpt_path", "/home/ubuntu/detect_pointcloud/src/pointpillars_ros/models/checkpoint_epoch_80.pth")
#         self.sub_velo = rospy.Subscriber("/livox/lidar", PointCloud2, self.lidar_callback, queue_size=1,  buff_size=2**12)
#         self.pub_bbox = rospy.Publisher("/detections", BoundingBoxArray, queue_size=1)
        
#         # 发布推理时间信息
#         self.pub_inference_time = rospy.Publisher("/inference_time", Header, queue_size=1)
        
#         return config_path, ckpt_path


#     def init_pointpillars(self, config_path, ckpt_path):
#         """ Initialize second model """
#         import os
#         os.chdir("/home/ubuntu/detect_pointcloud/src/pointpillars_ros")
#         logger = common_utils.create_logger() # 创建日志
#         logger.info('-----------------Quick Demo of Pointpillars-------------------------')
#         cfg_from_yaml_file(config_path, cfg)  # 加载配置文件
        
#         self.demo_dataset = DemoDataset(
#             dataset_cfg=cfg.DATA_CONFIG, class_names=cfg.CLASS_NAMES, training=False,
#             ext='.bin', logger=logger
#         )
#         self.model = build_network(model_cfg=cfg.MODEL, num_class=len(cfg.CLASS_NAMES), dataset=self.demo_dataset)
#         # 加载权重文件
#         self.model.load_params_from_file(filename=ckpt_path, logger=logger, to_cpu=True)
#         self.model.cuda() # 将网络放到GPU上
#         self.model.eval() # 开启评估模式


#     def rotate_mat(self, axis, radian):
#         rot_matrix = linalg.expm(np.cross(np.eye(3), axis / linalg.norm(axis) * radian))
#         return rot_matrix


#     def lidar_callback(self, msg):
#         """ Captures pointcloud data and feed into second model for inference """
#         # 记录开始时间
#         total_start_time = time.time()
        
#         pcl_msg = pc2.read_points(msg, skip_nans=True, field_names=("x", "y", "z","intensity","ring"))
#         np_p = np.array(list(pcl_msg), dtype=np.float32)
#         # 旋转轴
#         rand_axis = [0,1,0]  # y轴
#         #旋转角度0.1047
#         yaw =  0
#         #返回旋转矩阵
#         rot_matrix = self.rotate_mat(rand_axis, yaw)  # 绕y轴旋转的旋转矩阵
#         np_p_rot = np.dot(rot_matrix, np_p[:,:3].T).T
        
#         # convert to xyzi point cloud
#         x = np_p_rot[:, 0].reshape(-1)
#         y = np_p_rot[:, 1].reshape(-1)
#         z = np_p_rot[:, 2].reshape(-1)
#         if np_p.shape[1] == 4: # if intensity field exists
#             i = np_p[:, 3].reshape(-1)
#         else:
#             i = np.zeros((np_p.shape[0], 1)).reshape(-1)
#         points = np.stack((x, y, z, i)).T
#         print(points.shape)
        
#         # 数据预处理开始时间
#         preprocessing_start_time = time.time()
        
#         # 组装数组字典
#         input_dict = {
#             'points': points,
#             'frame_id': 0,
#         }
#         data_dict = self.demo_dataset.prepare_data(data_dict=input_dict) # 数据预处理
#         data_dict = self.demo_dataset.collate_batch([data_dict])
#         load_data_to_gpu(data_dict) # 将数据放到GPU上
        
#         # 数据预处理结束时间
#         preprocessing_time = time.time() - preprocessing_start_time
        
#         # 模型推理开始时间
#         inference_start_time = time.time()
        
#         with torch.no_grad():  # 确保在推理时不计算梯度
#             pred_dicts, _ = self.model.forward(data_dict) # 模型前向传播
        
#         # 模型推理结束时间
#         inference_time = time.time() - inference_start_time
        
#         boxes_lidar = pred_dicts[0]['pred_boxes'].detach().cpu().numpy()
#         scores = pred_dicts[0]['pred_scores'].detach().cpu().numpy()
#         label = pred_dicts[0]['pred_labels'].detach().cpu().numpy()
#         num_detections = boxes_lidar.shape[0]
        
#         # 总处理时间
#         total_time = time.time() - total_start_time
        
#         # 更新统计信息
#         self.frame_count += 1
#         self.total_inference_time += inference_time
#         self.total_preprocessing_time += preprocessing_time
        
#         # 计算平均值
#         self.avg_inference_time = self.total_inference_time / self.frame_count
#         self.avg_preprocessing_time = self.total_preprocessing_time / self.frame_count
#         self.avg_fps = self.frame_count / (self.total_inference_time + self.total_preprocessing_time)
        
#         # 打印详细的性能信息
#         rospy.loginfo("\n=== 模型性能统计 ===")
#         rospy.loginfo("检测到目标数量: %d", num_detections)
#         rospy.loginfo("当前帧 - 预处理时间: %.4f秒", preprocessing_time)
#         rospy.loginfo("当前帧 - 推理时间: %.4f秒", inference_time)
#         rospy.loginfo("当前帧 - 总处理时间: %.4f秒", total_time)
#         rospy.loginfo("当前帧 - FPS: %.2f", 1.0 / total_time)
#         rospy.loginfo("累计统计 - 平均预处理时间: %.4f秒", self.avg_preprocessing_time)
#         rospy.loginfo("累计统计 - 平均推理时间: %.4f秒", self.avg_inference_time)
#         rospy.loginfo("累计统计 - 平均FPS: %.2f", self.avg_fps)
#         rospy.loginfo("累计处理帧数: %d", self.frame_count)
#         rospy.loginfo("===================")

#         # print(boxes_lidar)
#         # print(scores)
#         # print(label)

#         arr_bbox = BoundingBoxArray()  # 创建BoundingBoxArray消息
#         # for i in range(num_detections):
#         #     bbox = BoundingBox()

#         #     bbox.header.frame_id = msg.header.frame_id
#         #     bbox.header.stamp = rospy.Time.now()
#         #     bbox.pose.position.x = float(boxes_lidar[i][0])
#         #     bbox.pose.position.y = float(boxes_lidar[i][1])
#         #     # bbox.pose.position.z = float(boxes_lidar[i][2]) + float(boxes_lidar[i][5]) / 2
#         #     bbox.pose.position.z = float(boxes_lidar[i][2])
#         #     bbox.dimensions.x = float(boxes_lidar[i][3])  # width
#         #     bbox.dimensions.y = float(boxes_lidar[i][4])  # length
#         #     bbox.dimensions.z = float(boxes_lidar[i][5])  # height
#         #     q = Quaternion(axis=(0, 0, 1), radians=float(boxes_lidar[i][6]))
#         #     bbox.pose.orientation.x = q.x
#         #     bbox.pose.orientation.y = q.y
#         #     bbox.pose.orientation.z = q.z
#         #     bbox.pose.orientation.w = q.w
#         #     bbox.value = scores[i]
#         #     bbox.label = label[i]

#         #     arr_bbox.boxes.append(bbox)
#         for i in range(num_detections):
#     # 1. 先获取当前检测框的标签
#             current_label = label[i]  # label 是模型输出的标签数组
        
#         # 2. 标签过滤：只保留目标标签的检测框，其他直接跳过
#             if current_label not in TARGET_LABELS:
#                 continue  # 跳过非目标标签，不构造边界框
        
#         # 3. 只有符合目标标签的检测框，才继续构造 BoundingBox
#             bbox = BoundingBox()

#             bbox.header.frame_id = msg.header.frame_id
#             bbox.header.stamp = rospy.Time.now()
#             bbox.pose.position.x = float(boxes_lidar[i][0])
#             bbox.pose.position.y = float(boxes_lidar[i][1])
#             bbox.pose.position.z = float(boxes_lidar[i][2])  # 若需调整z轴（如物体中心），可改为 boxes_lidar[i][2] + boxes_lidar[i][5]/2
#             bbox.dimensions.x = float(boxes_lidar[i][3])  # width
#             bbox.dimensions.y = float(boxes_lidar[i][4])  # length
#             bbox.dimensions.z = float(boxes_lidar[i][5])  # height
#             q = Quaternion(axis=(0, 0, 1), radians=float(boxes_lidar[i][6]))
#             bbox.pose.orientation.x = q.x
#             bbox.pose.orientation.y = q.y
#             bbox.pose.orientation.z = q.z
#             bbox.pose.orientation.w = q.w
#             bbox.value = scores[i]
#             bbox.label = current_label  # 使用当前标签（已过滤）
#             arr_bbox.boxes.append(bbox)  # 只添加目标标签的边界框

        
#         arr_bbox.header.frame_id = msg.header.frame_id
#         arr_bbox.header.stamp = rospy.Time.now()
        
#         self.pub_bbox.publish(arr_bbox)
        
#         # 发布推理时间信息（可选）
#         time_header = Header()
#         time_header.stamp = rospy.Time.now()
#         time_header.frame_id = f"推理时间: {inference_time:.4f}s, FPS: {1.0/total_time:.2f}"
#         self.pub_inference_time.publish(time_header)


# if __name__ == '__main__':
#     sec = Pointpillars_ROS()
#     rospy.init_node('pointpillars_ros_node', anonymous=True)
#     try:
#         rospy.spin()
#     except KeyboardInterrupt:
#         # 在程序退出时打印最终统计信息
#         rospy.loginfo("\n=== 最终性能统计 ===")
#         rospy.loginfo("总处理帧数: %d", sec.frame_count)
#         rospy.loginfo("平均预处理时间: %.4f秒", sec.avg_preprocessing_time)
#         rospy.loginfo("平均推理时间: %.4f秒", sec.avg_inference_time)
#         rospy.loginfo("平均FPS: %.2f", sec.avg_fps)
#         rospy.loginfo("===================")
#         del sec
#         print("Shutting down")
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
#import sensor_msgs.point_cloud2 as pc2
import sensor_msgs_py.point_cloud2 as pc2
from std_msgs.msg import Header
from jsk_recognition_msgs.msg import BoundingBox, BoundingBoxArray
from builtin_interfaces.msg import Time
import time
from visualization_msgs.msg import Marker, MarkerArray
from builtin_interfaces.msg import Duration # 用于设置Marker的生存时间
import numpy as np
from pyquaternion import Quaternion
import argparse
import glob
from pathlib import Path
# import mayavi.mlab as mlab
import torch
import scipy.linalg as linalg
import sys
sys.path.append("/home/ubuntu/PointPillars_ROS/src/pointpillars_ros")

# 定义过滤参数（根据需求修改）
TARGET_LABELS = [1]  
CONFIDENCE_THRESHOLD = 0.0
MIN_POINT_COUNT = 0

from pcdet.config import cfg, cfg_from_yaml_file
from pcdet.datasets import DatasetTemplate
from pcdet.models import build_network, load_data_to_gpu
from pcdet.utils import common_utils

class DemoDataset(DatasetTemplate):
    def __init__(self, dataset_cfg, class_names, training=True, root_path=None, logger=None, ext='.bin'):
        super().__init__(
            dataset_cfg=dataset_cfg, class_names=class_names, training=training, root_path=root_path, logger=logger
        )

class PointpillarsROS2(Node):
    def __init__(self):
        super().__init__('pointpillars_ros2_node')
        
        # 初始化计时变量
        self.total_inference_time = 0.0
        self.total_preprocessing_time = 0.0
        self.frame_count = 0
        self.avg_inference_time = 0.0
        self.avg_preprocessing_time = 0.0
        self.avg_fps = 0.0
        
        self.class_names = []
        
        self.declare_parameter('config_path', '/home/ubuntu/detect_pointcloud/src/pointpillars_ros/cfgs/custom_models/r2_model.yaml')
        self.declare_parameter('ckpt_path', '/home/ubuntu/detect_pointcloud/src/pointpillars_ros/models/R2.pth')
        
        # 获取参数值
        config_path = self.get_parameter('config_path').value
        ckpt_path = self.get_parameter('ckpt_path').value
        
        # 初始化订阅和发布者
        self.sub_velo = self.create_subscription(
            PointCloud2,
            '/cloud_registered',
            self.lidar_callback,
            10  # QoS配置（ROS 2用数字表示队列大小，替代queue_size）
        )
        self.pub_inference_time = self.create_publisher(Header, '/inference_time', 10)
        self.pub_markers = self.create_publisher(MarkerArray, '/detections_markers', 10)
        self.pub_bbox=self.create_publisher(BoundingBoxArray,'/detections',10)
        # 初始化PointPillars模型
        self.init_pointpillars(config_path, ckpt_path)
        self.get_logger().info("Pointpillars ROS 2节点已启动，开始处理点云数据...")

    def init_pointpillars(self, config_path, ckpt_path):
        """Initialize PointPillars model and load weights"""
        import os
        os.chdir("/home/ubuntu/detect_pointcloud/src/pointpillars_ros")
        logger = common_utils.create_logger()
        logger.info('-----------------Quick Demo of Pointpillars-------------------------')
        # 加载模型配置
        cfg_from_yaml_file(config_path, cfg)
        
        # 保存类别名称列表（关键：用于标签到名称的映射）
        self.class_names = cfg.CLASS_NAMES
        self.get_logger().info(f"成功加载检测类别列表: {self.class_names}")
        self.get_logger().info(f"当前设置只显示标签为 {TARGET_LABELS}、置信度≥{CONFIDENCE_THRESHOLD}且点云数≥{MIN_POINT_COUNT}的目标")
        
        # 初始化数据预处理模板（推理模式）
        self.demo_dataset = DemoDataset(
            dataset_cfg=cfg.DATA_CONFIG, class_names=self.class_names,
            training=False, ext='.bin', logger=logger
        )
        # 构建模型
        self.model = build_network(model_cfg=cfg.MODEL, num_class=len(self.class_names), dataset=self.demo_dataset)
        # 加载预训练权重
        self.model.load_params_from_file(filename=ckpt_path, logger=logger, to_cpu=True)
        # 部署到GPU并开启推理模式
        self.model.cuda()
        self.model.eval()

    def rotate_mat(self, axis, radian):
        """Calculate rotation matrix around specified axis"""
        rot_matrix = linalg.expm(np.cross(np.eye(3), axis / linalg.norm(axis) * radian))
        return rot_matrix

    def count_points_in_box(self, points, box):
        """
        计算点云中位于3D检测框内的点数量
        points: 原始点云（N×3或N×4，前3列为x,y,z）
        box: 检测框参数 [x, y, z, width, length, height, yaw]
        """
        x, y, z, w, l, h, yaw = box
        
        # 转换点云到检测框的局部坐标系（消除旋转）
        points_trans = points[:, :3] - np.array([x, y, z])
        
        # 点云旋转（消除检测框的yaw角旋转）
        cos_yaw = np.cos(-yaw)
        sin_yaw = np.sin(-yaw)
        rot_matrix = np.array([[cos_yaw, -sin_yaw, 0],
                              [sin_yaw, cos_yaw, 0],
                              [0, 0, 1]])
        points_rot = np.dot(points_trans, rot_matrix.T)  
        
        # 判断点是否在轴对齐的检测框内（局部坐标系下）
        in_box = (
            (points_rot[:, 0] >= -w/2) & (points_rot[:, 0] <= w/2) &
            (points_rot[:, 1] >= -l/2) & (points_rot[:, 1] <= l/2) &
            (points_rot[:, 2] >= -h/2) & (points_rot[:, 2] <= h/2)
        )
        
        return np.sum(in_box)

    def lidar_callback(self, msg:PointCloud2):
        """Core callback: process pointcloud, infer, filter bbox, publish result"""
        # 记录总开始时间
        total_start_time = time.time()
        marker_array = MarkerArray()
        # p_numpy = pc2.read_points_numpy(msg, field_names=("x", "y", "z", "intensity"), skip_nans=True)
        pcl_msg = pc2.read_points(msg, skip_nans=True, field_names=("x", "y", "z","intensity"))
        
        points_list = []
        for p in pcl_msg:
            points_list.append([p[0], p[1], p[2], p[3]])

# 检查是否为空
        if not points_list:
            self.get_logger().warn("接收到空的点云数据，已跳过该帧。")
            return

        
        
        np_p = np.array(list(points_list), dtype=np.float32)
        
        # 点云旋转（根据雷达安装角度调整）
        rand_axis = [0,1,0]  # y轴
        yaw = 0  # 旋转角度（弧度）
        rot_matrix = self.rotate_mat(rand_axis, yaw)
        np_p_rot = np.dot(rot_matrix, np_p[:,:3].T).T  
        
        # 构造模型需要的xyzi点云（4维）
        x = np_p_rot[:, 0].reshape(-1)
        y = np_p_rot[:, 1].reshape(-1)
        z = np_p_rot[:, 2].reshape(-1)
        i = np_p[:, 3].reshape(-1) if np_p.shape[1] == 4 else np.zeros_like(x)
        points = np.stack((x, y, z, i)).T
        # 保存旋转后的3D点（用于后续计算框内点数）
        rotated_xyz = points[:, :3]

        preprocessing_start_time = time.time()
        input_dict = {
            'points': points,
            'frame_id': 0,
        }
        data_dict = self.demo_dataset.prepare_data(data_dict=input_dict)
        data_dict = self.demo_dataset.collate_batch([data_dict])
        load_data_to_gpu(data_dict)
        preprocessing_time = time.time() - preprocessing_start_time

        # 模型推理
        inference_start_time = time.time()
        with torch.no_grad():
            pred_dicts, _ = self.model.forward(data_dict)
        inference_time = time.time() - inference_start_time

        # 解析推理结果
        boxes_lidar = pred_dicts[0]['pred_boxes'].detach().cpu().numpy()
        scores = pred_dicts[0]['pred_scores'].detach().cpu().numpy()
        labels = pred_dicts[0]['pred_labels'].detach().cpu().numpy()
        num_total_detections = boxes_lidar.shape[0]
        mask = (scores >= CONFIDENCE_THRESHOLD) & (np.isin(labels, TARGET_LABELS))
        valid_indices = np.where(mask)[0]
        # 过滤检测框并映射类别名称
        filtered_classes = []  
        low_confidence_count = num_total_detections - len(valid_indices) # 粗略统计
        low_point_count = 0
        bbox_array = BoundingBoxArray()
        bbox_array.header = msg.header
        for i in valid_indices:
            current_label = labels[i]
            current_score = scores[i]
            current_box = boxes_lidar[i]  

            # 标签过滤：只保留目标标签
            if current_label not in TARGET_LABELS:
                continue
            
            # 置信度过滤：只保留高置信度目标
            if current_score < CONFIDENCE_THRESHOLD:
                low_confidence_count += 1
                continue

            # 3. 点云数量过滤：计算框内点数量并过滤
            point_count = self.count_points_in_box(rotated_xyz, current_box)
            if point_count < MIN_POINT_COUNT:
                low_point_count += 1
                # self.get_logger().info(f"过滤低点数目标: 类别={current_label}, 点数={point_count}, 置信度={current_score:.2f}")
                continue

            # 映射数字标签到类别名称
            label_index = current_label - 1  # 标签从1开始，索引从0开始
            if 0 <= label_index < len(self.class_names):
                class_name = self.class_names[label_index]
            else:
                class_name = f"unknown(label={current_label})"
            filtered_classes.append(f"{class_name}(置信度:{current_score:.2f}, 点数:{point_count})")

            # 打印单个目标信息（包含点数）
            self.get_logger().info(f"检测到目标: {class_name} (标签: {current_label}, 置信度: {current_score:.2f}, 点数: {point_count})")
            bbox = BoundingBox()
            bbox.header = msg.header
            bbox.pose.position.x = float(current_box[0])
            bbox.pose.position.y = float(current_box[1])
            bbox.pose.position.z = float(current_box[2])
            
            q = Quaternion(axis=(0, 0, 1), radians=float(current_box[6]))
            bbox.pose.orientation.x = q.x
            bbox.pose.orientation.y = q.y
            bbox.pose.orientation.z = q.z
            bbox.pose.orientation.w = q.w
            
            bbox.dimensions.x = float(current_box[3])
            bbox.dimensions.y = float(current_box[4])
            bbox.dimensions.z = float(current_box[5])
            
            bbox.value = float(current_score)
            bbox.label = int(current_label)
            
            bbox_array.boxes.append(bbox)
            # 构造BoundingBox消息
            marker = Marker()
            marker.header = msg.header # 使用与点云相同的坐标系
            marker.ns = "detection_boxes"
            marker.id = int(i)
            marker.type = Marker.CUBE # 使用立方体表示
            marker.action = Marker.ADD
            
            # 设置生存时间（例如0.2秒），超时自动清除，防止重影
            marker.lifetime.sec = 0
            marker.lifetime.nanosec = 200000000 # 0.2s
            
            
            marker.pose.position.x = float(current_box[0])
            marker.pose.position.y = float(current_box[1])
            marker.pose.position.z = float(current_box[2])
            
            # 设置方向
            q = Quaternion(axis=(0, 0, 1), radians=float(current_box[6]))
            marker.pose.orientation.x = q.x
            marker.pose.orientation.y = q.y
            marker.pose.orientation.z = q.z
            marker.pose.orientation.w = q.w
            
            # 设置尺寸 (Scale)
            marker.scale.x = float(current_box[3]) # width
            marker.scale.y = float(current_box[4]) # length
            marker.scale.z = float(current_box[5]) # height
            
            
            marker.color.r = 0.0
            marker.color.g = 1.0
            marker.color.b = 0.0
            marker.color.a = 0.5 # 透明度
            
            marker_array.markers.append(marker)

        # 性能统计
        self.pub_markers.publish(marker_array)
        self.pub_bbox.publish(bbox_array)
        total_time = time.time() - total_start_time
        self.frame_count += 1
        self.total_inference_time += inference_time
        self.total_preprocessing_time += preprocessing_time
        
        # 计算平均值
        self.avg_inference_time = self.total_inference_time / self.frame_count
        self.avg_preprocessing_time = self.total_preprocessing_time / self.frame_count
        self.avg_fps = self.frame_count / (self.total_inference_time + self.total_preprocessing_time)

        # 打印统计日志
        num_filtered_detections = len(marker_array.markers)
        self.get_logger().info("\n=== 模型性能与检测统计 ===")
        self.get_logger().info(f"模型输出总目标数: {num_total_detections}")
        self.get_logger().info(f"标签过滤后剩余目标数: {num_total_detections - (num_total_detections - (num_filtered_detections + low_confidence_count + low_point_count))}")
        self.get_logger().info(f"低置信度过滤掉的目标数（<{CONFIDENCE_THRESHOLD}）: {low_confidence_count}")
        self.get_logger().info(f"低点数过滤掉的目标数（<{MIN_POINT_COUNT}）: {low_point_count}")
        self.get_logger().info(f"最终发布目标数: {num_filtered_detections}")
        self.get_logger().info(f"最终目标类别: {filtered_classes}")
        self.get_logger().info(f"当前帧 - 预处理时间: {preprocessing_time:.4f}s")
        self.get_logger().info(f"当前帧 - 推理时间: {inference_time:.4f}s")
        self.get_logger().info(f"当前帧 - 总处理时间: {total_time:.4f}s")
        self.get_logger().info(f"当前帧 - FPS: {1.0/total_time:.2f}")
        self.get_logger().info(f"累计统计 - 平均预处理时间: {self.avg_preprocessing_time:.4f}s")
        self.get_logger().info(f"累计统计 - 平均推理时间: {self.avg_inference_time:.4f}s")
        self.get_logger().info(f"累计统计 - 平均FPS: {self.avg_fps:.2f}")
        self.get_logger().info(f"累计处理帧数: {self.frame_count}")
        self.get_logger().info("===================")

    
        
        
        # 发布推理时间信息
        time_header = Header()
        time_header.stamp = self.get_clock().now().to_msg()
        time_header.frame_id = f"inf_time:{inference_time:.4f}s, fps:{1.0/total_time:.2f}"
        self.pub_inference_time.publish(time_header)

def main(args=None):
    rclpy.init(args=args)
    pointpillars_node = PointpillarsROS2()
    try:
        rclpy.spin(pointpillars_node)
    except KeyboardInterrupt:
        # 程序退出时打印最终统计
        pointpillars_node.get_logger().info("\n=== 最终性能统计 ===")
        pointpillars_node.get_logger().info(f"总处理帧数: {pointpillars_node.frame_count}")
        pointpillars_node.get_logger().info(f"平均预处理时间: {pointpillars_node.avg_preprocessing_time:.4f}s")
        pointpillars_node.get_logger().info(f"平均推理时间: {pointpillars_node.avg_inference_time:.4f}s")
        pointpillars_node.get_logger().info(f"平均FPS: {pointpillars_node.avg_fps:.2f}")
        pointpillars_node.get_logger().info("===================")
    finally:
        pointpillars_node.destroy_node()
        rclpy.shutdown()
        print("Pointpillars ROS 2节点已关闭")

if __name__ == '__main__':
    main()
