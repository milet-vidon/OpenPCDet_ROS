#include <rclcpp/rclcpp.hpp>
#include <jsk_recognition_msgs/msg/bounding_box.hpp>
#include <jsk_recognition_msgs/msg/bounding_box_array.hpp>
#include <visualization_msgs/msg/marker.hpp>
#include <visualization_msgs/msg/marker_array.hpp>
#include <geometry_msgs/msg/point.hpp>
#include <vector>
#include <cmath>
#include <algorithm>
#include <string>

using std::placeholders::_1;

// 定义一个简单的被跟踪物体结构
struct TrackedObject {
    int id;
    jsk_recognition_msgs::msg::BoundingBox bbox;
    int life_time; //以此判断是否消失
};

class BBoxTrackerNode : public rclcpp::Node
{
public:
    BBoxTrackerNode() : Node("bbox_tracker_node"), next_id_(0)
    {
        // 1. 订阅 ros.py 发布的 /detections 话题
        sub_bbox_ = this->create_subscription<jsk_recognition_msgs::msg::BoundingBoxArray>(
            "/detections", 10, std::bind(&BBoxTrackerNode::topic_callback, this, _1));

        // 2. 发布用于 RViz 显示的 Markers (包含ID)
        pub_marker_ = this->create_publisher<visualization_msgs::msg::MarkerArray>(
            "/tracking_markers", 10);

        RCLCPP_INFO(this->get_logger(), "BBox Tracker initialized. Listening to /detections...");
    }

private:
    void topic_callback(const jsk_recognition_msgs::msg::BoundingBoxArray::SharedPtr msg)
    {
        visualization_msgs::msg::MarkerArray markers;
        
        // 简单的数据关联 (最近邻匹配)
        std::vector<TrackedObject> new_tracked_objects;
        
        for (const auto& input_bbox : msg->boxes) {
            float min_dist = 2.0; // 匹配阈值 (2米内认为是同一个物体)
            int matched_index = -1;

            // 寻找最近的旧物体
            for (size_t i = 0; i < tracked_objects_.size(); ++i) {
                float dist = calculate_distance(input_bbox, tracked_objects_[i].bbox);
                if (dist < min_dist) {
                    min_dist = dist;
                    matched_index = i;
                }
            }

            TrackedObject obj;
            obj.bbox = input_bbox;
            obj.life_time = 5; // 存活帧数

            if (matched_index != -1) {
                // 匹配成功，继承ID
                obj.id = tracked_objects_[matched_index].id;
                // 从旧列表中移除，避免重复匹配
                tracked_objects_.erase(tracked_objects_.begin() + matched_index);
            } else {
                // 未匹配，分配新ID
                obj.id = next_id_++;
            }
            new_tracked_objects.push_back(obj);
        }

        // 更新列表
        tracked_objects_ = new_tracked_objects;

        // --- 生成可视化 Markers ---
        for (const auto& obj : tracked_objects_) {
            // 1. 3D 框 Marker
            visualization_msgs::msg::Marker box_marker;
            box_marker.header = msg->header;
            box_marker.ns = "tracking_boxes";
            box_marker.id = obj.id;
            box_marker.type = visualization_msgs::msg::Marker::CUBE;
            box_marker.action = visualization_msgs::msg::Marker::ADD;
            box_marker.pose = obj.bbox.pose;
            box_marker.scale = obj.bbox.dimensions;
            box_marker.color.r = 0.0f; box_marker.color.g = 1.0f; box_marker.color.b = 1.0f; // 青色
            box_marker.color.a = 0.5f;
            box_marker.lifetime.sec = 0; box_marker.lifetime.nanosec = 200000000; // 0.2s

            markers.markers.push_back(box_marker);

            // 2. 文字 ID Marker
            visualization_msgs::msg::Marker text_marker;
            text_marker.header = msg->header;
            text_marker.ns = "tracking_ids";
            text_marker.id = obj.id + 10000; // ID偏移，防止冲突
            text_marker.type = visualization_msgs::msg::Marker::TEXT_VIEW_FACING;
            text_marker.action = visualization_msgs::msg::Marker::ADD;
            text_marker.pose = obj.bbox.pose;
            text_marker.pose.position.z += 1.5; // 文字显示在框上方
            text_marker.scale.z = 1.0; // 字体大小
            text_marker.color.r = 1.0f; text_marker.color.g = 1.0f; text_marker.color.b = 1.0f;
            text_marker.color.a = 1.0f;
            text_marker.text = "ID: " + std::to_string(obj.id);
            text_marker.lifetime.sec = 0; text_marker.lifetime.nanosec = 200000000;

            markers.markers.push_back(text_marker);
        }

        // 发布 Markers
        pub_marker_->publish(markers);
    }

    float calculate_distance(const jsk_recognition_msgs::msg::BoundingBox& b1, 
                             const jsk_recognition_msgs::msg::BoundingBox& b2) {
        float dx = b1.pose.position.x - b2.pose.position.x;
        float dy = b1.pose.position.y - b2.pose.position.y;
        float dz = b1.pose.position.z - b2.pose.position.z;
        return std::sqrt(dx*dx + dy*dy + dz*dz);
    }

    rclcpp::Subscription<jsk_recognition_msgs::msg::BoundingBoxArray>::SharedPtr sub_bbox_;
    rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr pub_marker_;
    
    std::vector<TrackedObject> tracked_objects_;
    int next_id_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<BBoxTrackerNode>());
    rclcpp::shutdown();
    return 0;
}