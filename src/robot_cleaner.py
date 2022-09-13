#!/usr/bin/env python3

import rospy
import math 
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose 
class Move(object):

    def __init__(self):
        rospy.init_node("move_straight", anonymous=True)
        self.vel_msg = Twist()
        self.velocity_publisher = rospy.Publisher("/turtle1/cmd_vel", Twist, queue_size= 10)
        self.pose_subscriber = rospy.Subscriber("/turtle1/pose", Pose, self.callback)
        self.turtle_theta = 0
        self.turtle_pose_x = 0
        self.turtle_pose_y = 0

    def move(self, speed, distance, isForward):
        
        # linear velocity 
        if isForward:
            self.vel_msg.linear.x = abs(speed)
        else:
            self.vel_msg.linear.x = -abs(speed)
        self.vel_msg.linear.y = 0
        self.vel_msg.linear.z = 0

        # angular velocity
        self.vel_msg.angular.x = 0
        self.vel_msg.angular.y = 0
        self.vel_msg.angular.z = 0
    
        t0 = rospy.Time().now().to_sec()
        current_distance = 0
        rate = rospy.Rate(10)

        while current_distance < distance:
            self.velocity_publisher.publish(self.vel_msg)
            t1 = rospy.Time().now().to_sec()
            current_distance = speed * (t1 - t0)
            
        self.vel_msg.linear.x = 0
        self.velocity_publisher.publish(self.vel_msg)

    def rotate(self, angular_speed, relative_angle, clockwise):
        
        if clockwise:
            self.vel_msg.angular.z = -abs(angular_speed)
        else:
            self.vel_msg.angular.z = abs(angular_speed)
       
        self.vel_msg.angular.x = 0
        self.vel_msg.angular.y = 0

        self.vel_msg.linear.x = 0
        self.vel_msg.linear.y = 0
        self.vel_msg.linear.z = 0
       
        rate = rospy.Rate(0.5)
        t0 = rospy.Time().now().to_sec()
        current_angle = self.turtle_theta

        while True:
            self.velocity_publisher.publish(self.vel_msg)
            t1 = rospy.Time().now().to_sec()
            current_angle = angular_speed * (t1 - t0)
            if current_angle > relative_angle:
                break 

        self.vel_msg.angular.z = 0
        self.velocity_publisher.publish(self.vel_msg)
    
    def callback(self, msg):
        self.turtle_pose_x = msg.x
        self.turtle_pose_y = msg.y
        self.turtle_theta = msg.theta

    def setDesiredOrientation(self, desired_orientation):
        relative_angle = desired_orientation - math.degrees(self.turtle_theta)
        clockwise = 1 if relative_angle < 0 else 0
        self.rotate(5, math.radians(abs(relative_angle)), clockwise)

    def moveToGoal(self, goal, distance_tolerance):
        
        while True:
            turtle_coordinates = [self.turtle_pose_x, self.turtle_pose_y]
            goal_coordinates = [goal.x, goal.y]
            self.vel_msg.linear.x = 0.5 * math.dist(turtle_coordinates, goal_coordinates)
            self.vel_msg.linear.y = 0
            self.vel_msg.linear.z = 0

            self.vel_msg.angular.x = 0
            self.vel_msg.angular.y = 0
            self.vel_msg.angular.z = 4 * (math.atan2(goal.y - self.turtle_pose_y, goal.x - self.turtle_pose_x) - self.turtle_theta)

            self.velocity_publisher.publish(self.vel_msg)

            if math.dist(turtle_coordinates, goal_coordinates) < distance_tolerance:
                break

        self.vel_msg.linear.x = 0
        self.vel_msg.angular.z = 0
        self.velocity_publisher.publish(self.vel_msg)
    
    def gridClean(self):

        goal = Pose()
        goal.x = 1
        goal.y = 1
        self.moveToGoal(goal, 0.05)
        self.setDesiredOrientation(0)
        

        self.move(2, 9, 1)
        self.rotate(2, math.radians(90), 0)
        
        self.move(2, 9, 1)
        self.rotate(2, math.radians(90), 0)
        
        self.move(2, 1, 1)
        self.rotate(2, math.radians(90), 0)
        
        self.move(2, 9, 1)
        self.rotate(2, math.radians(90), 1)

        self.move(2, 1, 1)
        self.rotate(2, math.radians(90), 1)

        self.move(2, 9, 1)
        

    def spiralClean(self):

        constant_speed = 4
        self.vel_msg.linear.x = 0
        while True:
            self.vel_msg.linear.x = self.vel_msg.linear.x + 0.000005
            self.vel_msg.linear.y = 0
            self.vel_msg.linear.z = 0

            self.vel_msg.angular.x = 0
            self.vel_msg.angular.y = 0
            self.vel_msg.angular.z = constant_speed
            
            self.velocity_publisher.publish(self.vel_msg)
            
            if self.turtle_pose_x > 10.5 and self.turtle_pose_y > 10.5:
                break

        self.vel_msg.linear.x = 0
        self.vel_msg.angular.z = 0
        self.velocity_publisher.publish(self.vel_msg)

if __name__ == "__main__":

    try:
        move = Move()
        
        '''
        another_move = input("Specify the kind of your move. Press 1 for moving, 2 for rotating or 0 for exit: ")
        while int(another_move):
            
            if int(another_move) == 1:
                speed = input("Speed: ")
                distance = input("Distance: ")
                isForward = input("Move Forward: ")
                move.move(float(speed), float(distance), int(isForward))
            
            elif int(another_move) == 2:
                angular_speed = input("Angular Speed: ")
                angle = input("Angle (degrees): ")
                clockwise = input("Turn clockwise: ")
                move.rotate(float(angular_speed), math.radians(float(angle)), int(clockwise))
            else:
                break
            another_move = input("Another Move? Press 1 for moving, 2 for rotating or 0 for exit: ")
        '''

        goal = Pose()
        goal.x = rospy.get_param("x_goal")
        goal.y = rospy.get_param("y_goal")
        move.moveToGoal(goal, 0.05)

        #move.gridClean()

    except (rospy.ROSInterruptException, KeyboardInterrupt):
        pass