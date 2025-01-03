#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
import yaml
import os
import math

# Global variable to store the robot's current position
current_position = None

# Load goals from a YAML file
def load_goals(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Callback function to update the current position of the robot
def odom_callback(data):
    global current_position
    current_position = data.pose.pose

# Function to check if the robot has reached the goal
def goal_reached(goal_pose):
    tolerance = 0.5  # Tolerance distance for reaching the goal (meters)
    if current_position:
        distance = math.sqrt(
            (goal_pose.position.x - current_position.position.x) ** 2 +
            (goal_pose.position.y - current_position.position.y) ** 2
        )
        return distance < tolerance
    return False

# Function to publish goals to the '/move_base_simple/goal' topic
def publish_goals(goals):
    pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=10)
    rospy.init_node('publish_goals', anonymous=True)
    rate = rospy.Rate(1)  # 1 Hz

    # Subscribe to the 'odom' topic to get the robot's position
    rospy.Subscriber('/odom', Odometry, odom_callback)

    # Ensure there is enough time for the publisher and subscriber to initialize
    rospy.sleep(1)

    for goal in goals:
        goal_msg = PoseStamped()
        goal_msg.header.frame_id = "odom"
        goal_msg.header.stamp = rospy.Time.now()

        goal_msg.pose.position.x = goal['position']['x']
        goal_msg.pose.position.y = goal['position']['y']
        goal_msg.pose.position.z = goal['position']['z']
        
        goal_msg.pose.orientation.x = goal['orientation']['x']
        goal_msg.pose.orientation.y = goal['orientation']['y']
        goal_msg.pose.orientation.z = goal['orientation']['z']
        goal_msg.pose.orientation.w = goal['orientation']['w']

        rospy.loginfo("Publishing goal: %s" % goal_msg)
        pub.publish(goal_msg)

        # Wait until the robot reaches the goal
        while not goal_reached(goal_msg.pose) and not rospy.is_shutdown():
            rospy.loginfo("Current position: x=%.2f, y=%.2f, goal: x=%.2f, y=%.2f" %
                         (current_position.position.x, current_position.position.y,
                          goal_msg.pose.position.x, goal_msg.pose.position.y))
            rate.sleep()

        rospy.loginfo("Reached goal: %s" % goal_msg)

        # Add a delay to give time between goals
        rospy.sleep(1)

if __name__ == '__main__':
    try:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.realpath(__file__))
        # Construct the path to the YAML file (one folder above)
        goals_file = os.path.join(script_dir, '..', 'goals.yaml')
        goals = load_goals(goals_file)
        publish_goals(goals)
    except rospy.ROSInterruptException:
        pass
