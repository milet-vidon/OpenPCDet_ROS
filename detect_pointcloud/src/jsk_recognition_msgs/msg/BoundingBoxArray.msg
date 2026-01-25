# jsk_recognition_msgs/msg/BoundingBoxArray.msg
# 多个 3D Bounding Box 的集合

# 消息头，包含时间戳和坐标系信息
std_msgs/Header header

# 包含的所有 BoundingBox
jsk_recognition_msgs/BoundingBox[] boxes
