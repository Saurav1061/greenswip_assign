import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from rclpy.qos import qos_profile_sensor_data
from cv_bridge import CvBridge
import cv2
import numpy as np

class PerceptionNode(Node):
    def __init__(self):
        super().__init__('perception_node')
        self.bridge = CvBridge()
        
        # Subscribe to the camera topic we created in the URDF
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            qos_profile_sensor_data)
        
        # Publish the visual error (X offset from center) for the Control Node
        self.error_pub = self.create_publisher(Point, '/visual_error', 10)
        
        # Optional: Publish the processed image so we can view it live
        self.debug_pub = self.create_publisher(Image, '/camera/debug_image', 10)
        
        self.get_logger().info('Perception Node Started. Looking for the target box...')

    def image_callback(self, msg):
        # 1. Convert ROS Image to OpenCV Image
        cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        height, width, _ = cv_image.shape
        center_x = width // 2
        
        # 2. Convert to HSV for better color segmentation
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        
        # TODO: Tune these bounds based on the color of the Box in your Reference Photo!
        # Currently set to isolate RED.
       # --- TUNED HSV MASK FOR DARK RED TARGET ---
 

        lower_red_1 = np.array([0, 50, 20])
        upper_red_1 = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red_1, upper_red_1)

        lower_red_2 = np.array([170, 50, 20])
        upper_red_2 = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red_2, upper_red_2)

     
        mask = mask1 | mask2
        
        # 3. Find Contours (outlines) of the masked object
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find the largest contour (assuming it's our target)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Filter out tiny specks of noise
            if cv2.contourArea(largest_contour) > 500: 
                
                # --- SHAPE DETECTION (Bonus Robustness) ---
                # To guarantee we only track the BOX and ignore spheres/cylinders of the same color:
                epsilon = 0.05 * cv2.arcLength(largest_contour, True)
                approx = cv2.approxPolyDP(largest_contour, epsilon, True)
                
                # A box viewed from the front/slight angle will generally have 4-6 distinct vertices
                if 4 <= len(approx) <= 6:
                    
                    # 4. Calculate the centroid (center pixel) of the target
                    M = cv2.moments(largest_contour)
                    if M["m00"] > 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                        
                        # Draw debug visuals (a bounding box and a dot in the center)
                        cv2.drawContours(cv_image, [largest_contour], -1, (0, 255, 0), 2)
                        cv2.circle(cv_image, (cX, cY), 5, (255, 0, 0), -1)
                        
                        # 5. Calculate Error: How far is the target from the center of the screen?
                        # Positive error = target is to the right. Negative = to the left.
                        error_x = float(cX - center_x)
                        
                        # Publish the error to our custom topic
                        error_msg = Point()
                        error_msg.x = error_x
                        self.error_pub.publish(error_msg)
                        
                        # Print to terminal
                        self.get_logger().info(f'Box Tracking Error: {error_x}', throttle_duration_sec=1.0)

        # Publish the annotated debug image
        debug_msg = self.bridge.cv2_to_imgmsg(cv_image, "bgr8")
        self.debug_pub.publish(debug_msg)

def main(args=None):
    rclpy.init(args=args)
    node = PerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
