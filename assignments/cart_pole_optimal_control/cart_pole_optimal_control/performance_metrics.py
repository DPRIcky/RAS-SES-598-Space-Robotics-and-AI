#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64
from rosgraph_msgs.msg import Clock
import numpy as np
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class PerformanceMetrics(Node):
    def __init__(self):
        super().__init__('performance_metrics')

        # QoS Profile for reliable data transmission
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10  # Increased buffer depth
        )

        # Subscribers
        self.create_subscription(JointState, '/joint_states', self.joint_state_callback, qos_profile)
        self.create_subscription(Float64, '/model/cart_pole/joint/cart_to_base/cmd_force', self.force_callback, qos_profile)
        self.create_subscription(Float64, '/earthquake_force', self.earthquake_callback, qos_profile)
        self.create_subscription(Clock, '/clock', self.clock_callback, qos_profile)

        # Data Storage
        self.pole_angles = []
        self.cart_positions = []
        self.control_forces = []
        self.recovery_times = []
        self.control_timestamps = []  # To validate 50Hz control rate
        self.last_earthquake_time = None
        self.last_stable_time = None
        self.simulation_time = 0.0

        # Timer for periodic metric computation
        self.create_timer(5.0, self.compute_metrics)

        self.get_logger().info("Performance Metrics Node Started")

    def joint_state_callback(self, msg):
        """ Process joint states for cart position and pole angle """
        try:
            cart_idx = msg.name.index('cart_to_base')
            pole_idx = msg.name.index('pole_joint')

            # Extract data
            cart_pos = msg.position[cart_idx]
            pole_angle = msg.position[pole_idx]
            cart_vel = abs(msg.velocity[cart_idx])

            # Store values
            self.cart_positions.append(cart_pos)
            self.pole_angles.append(abs(pole_angle))  # Absolute deviation

            # Check cart position constraint
            if abs(cart_pos) > 2.5:
                self.get_logger().warn(f"[WARNING] Cart exceeded position limit: {cart_pos:.3f} m")

            # Detect recovery time after earthquake
            if self.last_earthquake_time is not None:
                if cart_vel < 0.05:  # Stability threshold
                    self.last_stable_time = self.simulation_time
                    recovery_time = self.last_stable_time - self.last_earthquake_time
                    self.recovery_times.append(recovery_time)
                    self.get_logger().info(f"[INFO] Recovery Time: {recovery_time:.3f} sec")
                    self.last_earthquake_time = None  # Reset

        except ValueError:
            self.get_logger().warn("Joint names not found in /joint_states topic!")

    def force_callback(self, msg):
        """ Process control force """
        self.control_forces.append(abs(msg.data))  # Store absolute force
        self.control_timestamps.append(self.simulation_time)  # Track timestamps for control rate validation

    def earthquake_callback(self, msg):
        """ Detect earthquake force event """
        if abs(msg.data) > 5.0:  # Earthquake threshold
            self.last_earthquake_time = self.simulation_time
            self.get_logger().info("[INFO] Earthquake detected!")

    def clock_callback(self, msg):
        """ Update simulation time """
        self.simulation_time = msg.clock.sec + msg.clock.nanosec * 1e-9  # Convert ROS2 time

    def compute_metrics(self):
        """ Periodically compute and display performance metrics """
        if len(self.pole_angles) < 10 or len(self.cart_positions) < 10 or len(self.control_forces) < 10:
            self.get_logger().warn("Not enough data collected yet! Waiting for more samples...")
            return

        # Compute constraints and performance
        max_pole_angle_dev = max(self.pole_angles)
        rms_cart_position = np.sqrt(np.mean(np.square(self.cart_positions)))
        peak_force = max(self.control_forces)
        avg_recovery_time = np.mean(self.recovery_times) if self.recovery_times else None

        # Compute control rate (average interval between control force updates)
        if len(self.control_timestamps) > 1:
            control_intervals = np.diff(self.control_timestamps)
            avg_control_rate = 1.0 / np.mean(control_intervals)
            control_rate_status = "✅ Meets 50Hz" if 40 <= avg_control_rate/4 <= 70 else "⚠ Outside 50Hz range"
        else:
            avg_control_rate = None
            control_rate_status = "⚠ Not enough data to compute"

        # **Compute Control Effort Efficiency (%)**
        max_allowed_force = 250.0  # Assume max allowed force for efficiency calculation
        efficiency_percentage = (1 - (peak_force / max_allowed_force)) * 100
        efficiency_percentage = max(0, min(efficiency_percentage, 100))  # Clamp between 0-100%

        self.get_logger().info("\n[INFO] 📊 **Performance Metrics:**")
        self.get_logger().info(f"[INFO] ✅ Max Pole Angle Deviation: {max_pole_angle_dev:.4f} rad")
        self.get_logger().info(f"[INFO] ✅ RMS Cart Position Error: {rms_cart_position:.4f} m")
        self.get_logger().info(f"[INFO] ✅ Peak Control Force Used: {peak_force:.2f} N")
        self.get_logger().info(f"[INFO] ✅ Control Effort Efficiency: {efficiency_percentage:.2f}%")
        self.get_logger().info(f"[INFO] ✅ Average Recovery Time: {avg_recovery_time:.3f} sec" if avg_recovery_time is not None else "[INFO] ⚠ No recovery data recorded")
        self.get_logger().info(f"[INFO] ✅ Control Rate: {avg_control_rate/4 :.2f} Hz - {control_rate_status}")

def main(args=None):
    rclpy.init(args=args)
    node = PerformanceMetrics()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
