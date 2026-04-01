"""Subscribe to AprilTag detections and to TF (e.g. tag poses on /tf).

ROS parameters (all optional):

- ``detections_topic`` — default ``detections``
- ``tf_topic`` — default ``/tf`` (use ``/tf_static`` if you only care about static links)
- ``tf_child_frame_filter`` — default ``tag``; only TF lines logged when ``child_frame_id``
  contains this substring (case-insensitive). Set to ``""`` to log every transform
  (can be very noisy).
"""

import rclpy
from rclpy.node import Node
from apriltag_msgs.msg import AprilTagDetectionArray
from tf2_msgs.msg import TFMessage


class DetectionsListener(Node):
    def __init__(self):
        super().__init__('detections_listener')
        self.declare_parameter('detections_topic', 'detections')
        self.declare_parameter('tf_topic', '/tf')
        self.declare_parameter('tf_child_frame_filter', 'tag')

        det_topic = self.get_parameter('detections_topic').get_parameter_value().string_value
        tf_topic = self.get_parameter('tf_topic').get_parameter_value().string_value
        self._tf_filter = self.get_parameter(
            'tf_child_frame_filter'
        ).get_parameter_value().string_value

        self.create_subscription(
            AprilTagDetectionArray,
            det_topic,
            self._on_detections,
            10,
        )
        self.create_subscription(
            TFMessage,
            tf_topic,
            self._on_tf,
            100,
        )
        self.get_logger().info('Listening detections=%r tf=%r' % (det_topic, tf_topic))

    def _on_detections(self, msg: AprilTagDetectionArray):
        h = msg.header
        frame = h.frame_id if h.frame_id else '(no frame)'
        stamp = h.stamp.sec + h.stamp.nanosec * 1e-9
        n = len(msg.detections)
        self.get_logger().info(
            'detections: frame=%s stamp=%.6f count=%d' % (frame, stamp, n)
        )
        for d in msg.detections:
            self.get_logger().info(
                '  id=%d family=%r hamming=%d margin=%.3f centre=(%.1f, %.1f)' % (
                    d.id,
                    d.family,
                    d.hamming,
                    d.decision_margin,
                    d.centre.x,
                    d.centre.y,
                )
            )

    def _on_tf(self, msg: TFMessage):
        self.get_logger().debug('tf batch: %d transform(s)' % len(msg.transforms))
        f = self._tf_filter.lower() if self._tf_filter else ''
        for t in msg.transforms:
            cid = t.child_frame_id
            if f and f not in cid.lower():
                continue
            tr = t.transform.translation
            rot = t.transform.rotation
            h = t.header
            stamp = h.stamp.sec + h.stamp.nanosec * 1e-9
            self.get_logger().info(
                'tf: %s -> %s stamp=%.6f t=(%.3f,%.3f,%.3f) q=(%.3f,%.3f,%.3f,%.3f)' % (
                    h.frame_id,
                    cid,
                    stamp,
                    tr.x,
                    tr.y,
                    tr.z,
                    rot.x,
                    rot.y,
                    rot.z,
                    rot.w,
                )
            )


def main(args=None):
    rclpy.init(args=args)
    node = DetectionsListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
