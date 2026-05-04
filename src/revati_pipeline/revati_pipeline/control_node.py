import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point, Twist

class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')
        
        # Subscribe to the error calculated by your perception node
        self.subscription = self.create_subscription(
            Point,
            '/visual_error',
            self.error_callback,
            10)
            
        # Publish driving commands to the Ackerman plugin
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # --- TUNING PARAMETERS ---
        # How fast the robot drives forward (m/s)
        self.forward_speed = 0.25 
        
        # Proportional gain for steering (How aggressively it turns)
        self.kp_steering = 0.002 
        
        # Max steering angle in radians (based on your URDF limits)
        self.max_steering = 0.5 
        
        self.get_logger().info('Ackerman Control Node Started. Waiting for target...')

    def error_callback(self, msg):
        error_x = msg.x
        
        cmd = Twist()
        
        # STRICT ACKERMAN CONSTRAINT: We must have forward velocity to steer!
        # As long as we see the box (receiving callbacks), we drive forward.
        cmd.linear.x = self.forward_speed
        
        # Calculate steering angle based on visual error
        # If error_x is positive (box is to the right), steering must be negative (turn right)
        raw_steering = -1.0 * self.kp_steering * error_x
        
        # Clamp the steering to the physical limits of the robot joints
        if raw_steering > self.max_steering:
            cmd.angular.z = self.max_steering
        elif raw_steering < -self.max_steering:
            cmd.angular.z = -self.max_steering
        else:
            cmd.angular.z = raw_steering
            
        # Publish the command to the wheels!
        self.publisher_.publish(cmd)
        
        self.get_logger().info(f'Steering Angle: {cmd.angular.z:.2f} rad | Speed: {cmd.linear.x} m/s')

def main(args=None):
    rclpy.init(args=args)
    node = ControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
