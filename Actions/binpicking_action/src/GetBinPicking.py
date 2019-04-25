#!/usr/bin/env python2
# Tiago Almeida Tavares , DEM-UA  77001 , 17 April 2019
import rospy
import time  # sleep
import sys
import copy

from actionlib.action_server import ActionServer
from binpicking_action.msg import Robot_binpickingAction, Robot_binpickingFeedback, Robot_binpickingResult

# include for moveit
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg

# include for picking
import moveit_commander
from moveit_msgs.msg import RobotTrajectory
from math import pi
import numpy as np
# import tf
from tf.msg import tfMessage
from tf.transformations import quaternion_from_euler
from geometry_msgs.msg import Vector3, Pose2D, Pose, PointStamped, Quaternion
from std_msgs.msg import Float32, Header
import roslaunch
import math
from bin_picking.msg import TargetsPose
from robonuc.msg import ios

from generate_plan_move import generate_plan, move_robot

#import subprocess
# import threading
# import collections

from bin_picking.srv import *

from sensor_msgs.msg import Joy

normal = Vector3()
approx_point = Vector3()
eef_position_laser = Vector3()
roll = np.pi
pitch = Float32()
yaw = Float32()
laser_reading = Float32()


def monitoring_ios(function, ionumber):
    cod = function*10 + ionumber
    io_msg = ios()
    io_msg.code = cod
    print "Setting IOs code:"
    print cod
    #io_pub.publish(io_msg)

def callback_targets_pose(targets_pose):

    normal.x = targets_pose.normal.x
    normal.y = targets_pose.normal.y
    normal.z = targets_pose.normal.z
    approx_point.x = targets_pose.approx_point.x
    approx_point.y = targets_pose.approx_point.y
    approx_point.z = targets_pose.approx_point.z
    eef_position_laser.x = targets_pose.eef_position.x
    eef_position_laser.y = targets_pose.eef_position.y
    eef_position_laser.z = targets_pose.eef_position.z
    pitch.data = targets_pose.euler_angles.y
    yaw.data = targets_pose.euler_angles.x

def callback_laser_sensor(output_laser_reading):

    laser_reading.data = output_laser_reading.data

def get_targets_pose_client():
    x=1
    rospy.wait_for_service('get_targets_pose')
    try:
        get_targets_pose_ = rospy.ServiceProxy('get_targets_pose', get_targets_pose)
        resp1 = get_targets_pose_(x)
        print(resp1.my_response)

        return
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e
        return


def get_laser_average_client():
    x=1
    rospy.wait_for_service('get_laser_average')
    try:
        get_laser_average_ = rospy.ServiceProxy('get_laser_average', get_laser_average)
        resp1 = get_laser_average_(x)
        print(resp1.my_response)
        return
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e
        return


class RefServer (ActionServer):

    def __init__(self, name):
        self.server_name = name
        action_spec = Robot_binpickingAction
        ActionServer.__init__(
            self, name, action_spec, self.goalCallback, self.cancelCallback, False)
        self.start()  # como metemos o ultimo parametro a False, damos o start aqui
        rospy.loginfo("Creating ActionServer [%s]\n", name)

        self.saved_goals = []
        self._feedback = Robot_binpickingFeedback()
        self._result = Robot_binpickingResult()

        # construtor para moveit
        # This RobotCommander object is an interface to the robot as a whole.
        robot = moveit_commander.RobotCommander()

        # This PlanningSceneInterface object is an interface to the world surrounding the robot.
        scene = moveit_commander.PlanningSceneInterface()

        # MoveGroupCommander object. This object is an interface to one group of joints.
        # In this case the group is the joints in the manipulator. This interface can be used
        # to plan and execute motions on the manipulator.
        self.group = moveit_commander.MoveGroupCommander("manipulator")

        # Publisher of pointStamped of the grasping point
        grasping_point_pub = rospy.Publisher(
            '/graspingPoint',
            PointStamped,
            queue_size=10)
        # Publisher of pointStamped of the grasping point
        io_pub = rospy.Publisher(
            '/io_client_messages',
            ios,
            queue_size=10)

        self.continye_move= False #variable to confirm planning for picking


    def joyCallback(self, msg) :
        
        if msg.buttons[1] == 1:
            self.continue_move= True;

        return
    # Function for sending a ROS msg to the vs_IO_client.cpp node responsable for altering the state of the IOs
    # function - 1 to read, 2 to switch on and 3 to switch of the respective IO number (ionumber)

    # G======================GOALCALLBACK================================
    def goalCallback(self, gh):

        success = True
        goal = gh.get_goal()

        id = gh.get_goal_id().id
        #rospy.loginfo("Received request for goal " + str(id))

        self._feedback.sequence = []

        rospy.loginfo("Got goal %d", int(goal.mode))

        # if self.is_preempt_requested():
        #     rospy.loginfo('%s: Preempted' % self.name)
        #     self.set_preempted()
        #     success = False

        if goal.mode == 1:
            gh.set_accepted()

            # process =subprocess.call(["rosrun", "bin_picking", "move_fanuc_demo.py", "&"])
            #process = subprocess.call(["roslaunch", "robonuc_integration", "display_urdf_total.launch"])

            # time.sleep(5)

            # process.kill()
            # ========PICKING==========
            rospy.Subscriber("/targets_pose", TargetsPose, callback_targets_pose)
            rospy.Subscriber("/output_laser_sensor_average", Float32, callback_laser_sensor)
            rospy.Subscriber("/joy", Joy, self.joyCallback)

            self.group.set_planning_time(10.0)
            self.group.set_planner_id("RRTConnectkConfigDefault")

            visualization_point = Vector3()
            visualization_point.x = 0.480
            visualization_point.y = 0.000
            visualization_point.z = 0.440
            # visualization_point.z = 0.440 -0.200

            # Quaternions of the Euler angles
            roll = np.pi
            quaternion_init = quaternion_from_euler(-np.pi, 0, roll)

            # 1st POSITION - Visualize Workspace
            # GENERATING PLAN
            plan1, fraction1 = generate_plan(self.group, visualization_point, 5, quaternion_init)

            # MOVEMENT
            move_robot(plan1, fraction1, self.group)

            #rospy.loginfo("iam here")
            #LAUNCH obj service
            get_targets_pose_client()
            #rospy.loginfo("SAI DA FUNcao")

            rospy.wait_for_message("/targets_pose", TargetsPose)


            # Quaternions of the Euler angles
            quaternion = quaternion_from_euler( roll, math.radians(-pitch.data), math.radians(-yaw.data), 'rzyx')

            # 2nd POSITION - Measure with laser sensor
            # GENERATING PLAN
            plan2, fraction2 = generate_plan(self.group, eef_position_laser, 5, quaternion)

            # MOVING
            print("Press BUTTON B to execute the planning and continue B-picking: ")
            time.sleep(5)
            if (self.continue_move):
                move_robot(plan2, fraction2, self.group)

                get_laser_average_client()

                rospy.wait_for_message("/output_laser_sensor_average", Float32 )


                print (laser_reading.data )
                laser_reading_float = laser_reading.data + 1.000
                # for vertical eggs
                # laser_reading_float = laser_reading.data + 1.800

                grasping_point = Vector3()
                # + or -
                grasping_point.x = approx_point.x + laser_reading_float * 0.001 * normal.x
                grasping_point.y = approx_point.y + laser_reading_float * 0.001 * normal.y
                grasping_point.z = approx_point.z + laser_reading_float * 0.001 * normal.z

                # 3rd POSITION - Approximation point
                # GENERATING PLAN
                plan3, fraction3 = generate_plan(self.group, approx_point, 5, quaternion)

                rospy.loginfo("Plan generated")


                # # MOVING
                move_robot(plan3, fraction3, self.group)

                # 4th POSITION - Grasping point
                # GENERATING PLAN
                plan4, fraction4 = generate_plan(self.group, grasping_point, 5, quaternion)

                # MOVING
                move_robot(plan4, fraction4, self.group)

                # IO number 8 activates the suction
                # First activate IO number for for IO number 8 to work
                monitoring_ios(2,4)
                monitoring_ios(2,8)

                # 5th POSITION -Return to Approximation point
                # GENERATING PLAN 5
                plan5, fraction5 = generate_plan(self.group, approx_point, 5, quaternion)

                # MOVING
                move_robot(plan5, fraction5, self.group)

                final_point = Vector3()
                final_point.x = 0.440
                final_point.y = -0.270
                final_point.z = 0.200

                # Quaternions of the Euler angles
                quaternion_final = quaternion_from_euler(-np.pi, 0, roll)

                # 1st POSITION - Visualize Workspace
                # GENERATING PLAN
                plan6, fraction6 = generate_plan(self.group, final_point, 5, quaternion_final)

                # MOVEMENT
                move_robot(plan6, fraction6, self.group)

                monitoring_ios(3,8)
                monitoring_ios(3,4)
                continue_move=False;
            else:
                success = False
                continue_move=False;

            # =========//===Endpicking===//===========
        else:
            success = False
            gh.set_aborted(None, "The ref server has aborted")
            return

        if success:
            # self._result.sequence = self._feedback.sequence
            self._feedback.sequence.append(1)
            gh.publish_feedback(self._feedback)
            self._result.result = True
            gh.set_succeeded(self._result, "Server succeeded")
            rospy.loginfo('%s: Succeeded', self)
            return
        else :
            gh.set_aborted(None, "The ref server has aborted")
            return


    def cancelCallback(self, gh):
        # process.kill()
        rospy.loginfo("XXX action canceled XXX")
        return
        # if self._as.is_preempt_requested():
        #     self._as.set_preempted()
        # pass


if __name__ == "__main__":
    rospy.init_node("BinPickingAction")
    ref_server = RefServer("BinPickingAction")

    rospy.spin()
