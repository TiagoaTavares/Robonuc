#!/usr/bin/env python2

import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
# import geometry_msgs.msg
from math import pi
import numpy as np
# import tf
from tf.msg import tfMessage
from tf.transformations import quaternion_from_euler
from geometry_msgs.msg import Vector3, Pose2D, Pose, PointStamped
from std_msgs.msg  import Float32
import roslaunch
import math
from bin_picking.msg import TargetsPose

# initialize moveit_commander and rospy
print "============ Starting movement setup"
moveit_commander.roscpp_initialize(sys.argv)
rospy.init_node('bin_picking_move_fanuc',
                anonymous=True)

# This RobotCommander object is an interface to the robot as a whole.
robot = moveit_commander.RobotCommander()

# This PlanningSceneInterface object is an interface to the world surrounding the robot.
scene = moveit_commander.PlanningSceneInterface()

# MoveGroupCommander object. This object is an interface to one group of joints. 
# In this case the group is the joints in the manipulator. This interface can be used
# to plan and execute motions on the manipulator.
group = moveit_commander.MoveGroupCommander("manipulator")

# DisplayTrajectory publisher which is used to publish trajectories for RVIZ to visualize.
display_trajectory_publisher = rospy.Publisher(
                                    '/move_group/display_planned_path',
                                    moveit_msgs.msg.DisplayTrajectory)

# Publisher of pointStamped of the grasping point
grasping_point_pub = rospy.Publisher(
                                    '/graspingPoint',
                                    PointStamped)

print "============ Waiting for RVIZ..."
rospy.sleep(10)
print "============ Starting movement "

print "============ Reference frame: %s" % group.get_planning_frame()
print "============ Name of the end-effector link: %s" % group.get_end_effector_link()

print "============ Robot Groups:"
print robot.get_group_names()

print "============ Printing robot state"
print robot.get_current_state()
print "============"


normal = Vector3()
approx_point = Vector3()
eef_position_laser = Vector3()
roll = 0.0
pitch = 0.0
yaw = 0.0
laser_reading = 0.0

# def callback_normal(normal_in_robot_base):
#     normal.x = normal_in_robot_base.x
#     normal.y = normal_in_robot_base.y
#     normal.z = normal_in_robot_base.z

# def callback_approx_point(approximation_point_in_robot_base):
#     approx_point.x = approximation_point_in_robot_base.x
#     approx_point.y = approximation_point_in_robot_base.y
#     approx_point.z = approximation_point_in_robot_base.z
    
# def callback_eef_position(eef_position_laser_reading_in_robot_base):
#     eef_position_laser.x = eef_position_laser_reading_in_robot_base.x
#     eef_position_laser.y = eef_position_laser_reading_in_robot_base.y
#     eef_position_laser.z = eef_position_laser_reading_in_robot_base.z
    
# def callback_euler_angles(euler_angles):
#     roll = 0.0
#     pitch = euler_angles.y
#     yaw = euler_angles.x

# def callback_laser_sensor(output_laser_reading):
#     laser_reading = output_laser_reading

def callback_laser_sensor(output_laser_reading):

    normal.x = normal_in_robot_base.x
    normal.y = normal_in_robot_base.y
    normal.z = normal_in_robot_base.z

    approx_point.x = approximation_point_in_robot_base.x
    approx_point.y = approximation_point_in_robot_base.y
    approx_point.z = approximation_point_in_robot_base.z

    eef_position_laser.x = eef_position_laser_reading_in_robot_base.x
    eef_position_laser.y = eef_position_laser_reading_in_robot_base.y
    eef_position_laser.z = eef_position_laser_reading_in_robot_base.z

    roll = 0.0
    pitch = euler_angles.y
    yaw = euler_angles.x

    laser_reading = output_laser_reading

# rospy.Subscriber("/normal_in_robot_base", Vector3, callback_normal)
# rospy.Subscriber("/approximation_point_in_robot_base", Vector3, callback_approx_point)
# rospy.Subscriber("/eef_position_laser_reading_in_robot_base", Vector3, callback_eef_position)
# rospy.Subscriber("/euler_angles", Pose2D, callback_euler_angles)
# rospy.Subscriber("/output_laser_sensor", Float32, callback_laser_sensor)

rospy.Subscriber("/targets_pose", TargetsPose, callback_targets_pose)


print "=================================== Generating plan 1 = 1st POSITION - Visualize Workspace  ==================================="
group.set_planning_time(10)

group.set_joint_value_target([0, 0, 0, 0, -pi / 2, 0])

plan1 = group.plan()

print "=== Waiting while RVIZ displays plan1..."
rospy.sleep(5)

print "=== Visualizing plan1"
display_trajectory = moveit_msgs.msg.DisplayTrajectory()

display_trajectory.trajectory_start = robot.get_current_state()
display_trajectory.trajectory.append(plan1)
display_trajectory_publisher.publish(display_trajectory)

# group.set_joint_value_target([0, 0, 0, 0, -pi / 2, 0])
# plan = group.plan()
# print plan
# print "============ IS PLAN OK??  "
# print "If YES Press any key to MOVE!!"
# raw_input()
# group.execute(plan)

print "=== Waiting while plan1 is visualized (again)..."
rospy.sleep(5)

print "=================================== MOVING plan 1 = 1st POSITION - Visualize Workspace  ==================================="
#------MOVING-------
# if fraction == 1.0:
#     print 'planning was successful'
#     raw_input()
#     # MOVEMENT
#     group.execute(plan2)
# else:
#     print 'planning was not successfull'
# print fraction

raw_input()
# group.go()

# rospy.on_shutdown(self.shutdown)

# Launch objDetection and pointTFtransfer nodes
uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
roslaunch.configure_logging(uuid)
launch_objDetect_pointTF = roslaunch.parent.ROSLaunchParent(uuid, ["/home/joana/catkin_ws/src/Bin-picking/bin_picking/launch/objDetection_pointTFtranfer.launch"])
# Start Launch node objDetection and pointTFtransfer
launch_objDetect_pointTF.start()

# star to subscribe to all topics even though sensorRS232 have not been yet launched
# rospy.spin()

print "=== Running node objDetection and pointTFtransfer "

# WAIT for "a" to be pressed
while raw_input('') != 'a':
    print "Normal: "
    print normal
    print "Approximation Point: "
    print approx_point
    print "End-effector Position for laser sensor measurement: "
    print eef_position_laser

#Stop Launch node objDetection and pointTFtransfer
launch_objDetect_pointTF.shutdown()
# after having stopped both nodes the subscribed topics will be the last published and will be a fixed value
    
print "=================================== Generating plan 2 = 2nd POSITION - Measure with laser sensor ==================================="    

# Quaternions of the Euler angles
q = quaternion_from_euler(roll, pitch, yaw)
print "The quaternion representation is %s %s %s %s." % (q[0], q[1], q[2], q[3])

# plan2 = group.plan()

# print "=== Waiting while RVIZ displays plan2..."
# rospy.sleep(5)

# print "=== Visualizing plan2"
# display_trajectory = moveit_msgs.msg.DisplayTrajectory()

# display_trajectory.trajectory_start = robot.get_current_state()
# display_trajectory.trajectory.append(plan2)
# display_trajectory_publisher.publish(display_trajectory)

# print "=== Waiting while plan2 is visualized (again)..."
# rospy.sleep(5)

#=============== WAYPOINTS2!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

starting_point = Pose()
starting_point = group.get_current_pose().pose

vector_1to2 = Vector3()
vector_1to2.x = eef_position_laser.x - starting_point.position.x
vector_1to2.y = eef_position_laser.y - starting_point.position.y
vector_1to2.z = eef_position_laser.z - starting_point.position.z

length_1to2_1to2 = math.sqrt ( vector_1to2.x ** 2.0 + vector_1to2.y ** 2.0 + vector_1to2.z ** 2.0 )

P1_1to2 = Pose()
P1_1to2.orientation.x = q[0]
P1_1to2.orientation.y = q[1]
P1_1to2.orientation.z = q[2]
P1_1to2.orientation.w = q[3]
P1_1to2.position.x = starting_point.position.x + (length_1to2/3) * vector_1to2.x
P1_1to2.position.y = starting_point.position.y + (length_1to2/3) * vector_1to2.y
P1_1to2.position.z = starting_point.position.z + (length_1to2/3) * vector_1to2.z

P2_1to2 = Pose()
P2_1to2.orientation.x = q[0]
P2_1to2.orientation.y = q[1]
P2_1to2.orientation.z = q[2]
P2_1to2.orientation.w = q[3]
P2_1to2.position.x = starting_point.position.x + 2*(length_1to2/3) * vector_1to2.x
P2_1to2.position.y = starting_point.position.y + 2*(length_1to2/3) * vector_1to2.y
P2_1to2.position.z = starting_point.position.z + 2*(length_1to2/3) * vector_1to2.z

# Points for a clean path
waypoints2 = []

# start with the current pose
waypoints2.append(group.get_current_pose().pose)

# first orient gripper and move forward to P1
waypoints2.append(copy.deepcopy(P1_1to2))

# second move to P2
waypoints2.append(copy.deepcopy(P2_1to2))

# Final Position
pose_eef_position = Pose()
pose_eef_position.orientation.x = q[0]
pose_eef_position.orientation.y = q[1]
pose_eef_position.orientation.z = q[2]
pose_eef_position.orientation.w = q[3]
pose_eef_position.position.x = eef_position_laser.x
pose_eef_position.position.y = eef_position_laser.y
pose_eef_position.position.z = eef_position_laser.z
# group.set_pose_eef_position(pose_eef_position)

waypoints2.append(copy.deepcopy(pose_eef_position))

# We want the cartesian path to be interpolated at 
# a resolution of 1 cm which is why we will specify 
# 0.01 as the eef_step in cartesian translation. 
# We will specify the jump threshold as 0.0, effectively
# disabling it.
(plan2, fraction2) = group.compute_cartesian_path(
                             waypoints2,   # waypoints2 to follow
                             0.01,        # eef_step ??????????
                             0.0)         # jump_threshold ???????????

print "=== Waiting while RVIZ displays plan2..."
rospy.sleep(5)

print "=================================== MOVING plan 2 = 2nd POSITION - Measure with laser sensor ==================================="
if fraction2 == 1.0:
    print 'planning was successful'
    raw_input()
    # MOVEMENT
    group.execute(plan2)
else:
    print 'planning was not successfull'
print fraction2

# uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
# roslaunch.configure_logging(uuid)


launch_sensorRS232 = roslaunch.parent.ROSLaunchParent(uuid, ["/home/joana/catkin_ws/src/Bin-picking/bin_picking/launch/sensorRS232.launch"])
# Start Launch node sensorRS232
launch_sensorRS232.start()

rospy.spin()

print "=== Running node sensorRS232 "

# WAIT for "b" to be pressed
while raw_input('') != 'b':
    print "Laser Reading: "
    print laser_reading

# Stop Launch node sensorRS232
launch_sensorRS232.shutdown()

print "=================================== Generating plan 3 = 3rd POSITION - Approximation point  ==================================="    

print "=== Calculating Grasping point... "

grasping_point = Vector3()
# + or -
grasping_point.x = approx_point.x + laser_reading*normal.x
grasping_point.y = approx_point.y + laser_reading*normal.y
grasping_point.z = approx_point.z + laser_reading*normal.z

print " ========= Grasping Point ========="
print grasping_point

# Creating and publishing a PointStamped of the grasping point for visualization
grasping_point_ps = PointStamped()
grasping_point_ps.header.frame_id = "/robot_base_link"
grasping_point_ps.point.x = grasping_point.x
grasping_point_ps.point.y = grasping_point.y
grasping_point_ps.point.z = grasping_point.z

grasping_point_pub.publish(grasping_point_ps)

#===============  WAYPOINTS3!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

vector_2to3 = Vector3()
vector_2to3.x = approx_point.x - eef_position_laser.x
vector_2to3.y = approx_point.y - eef_position_laser.y
vector_2to3.z = approx_point.z - eef_position_laser.z

length_2to3 = math.sqrt ( vector_2to3.x ** 2.0 + vector_2to3.y ** 2.0 + vector_2to3.z ** 2.0 )

P1_2to3 = Pose()
P1_2to3.orientation.x = q[0]
P1_2to3.orientation.y = q[1]
P1_2to3.orientation.z = q[2]
P1_2to3.orientation.w = q[3]
P1_2to3.position.x = eef_position_laser.x + (length_2to3/2) * vector_2to3.x
P1_2to3.position.y = eef_position_laser.y + (length_2to3/2) * vector_2to3.y
P1_2to3.position.z = eef_position_laser.z + (length_2to3/2) * vector_2to3.z

# Points for a clean path
waypoints3 = []

# start with the current pose
waypoints3.append(group.get_current_pose().pose)

# first orient gripper and move forward to P1_2to3
waypoints3.append(copy.deepcopy(P1_2to3))

# Final Position
pose_approx_point = Pose()
pose_approx_point.orientation.x = q[0]
pose_approx_point.orientation.y = q[1]
pose_approx_point.orientation.z = q[2]
pose_approx_point.orientation.w = q[3]
pose_approx_point.position.x = approx_point.x
pose_approx_point.position.y = approx_point.y
pose_approx_point.position.z = approx_point.z
# group.set_pose_eef_position(pose_eef_position)

waypoints3.append(copy.deepcopy(pose_approx_point))

(plan3, fraction3) = group.compute_cartesian_path(
                             waypoints3,   # waypoints3 to follow
                             0.01,        # eef_step
                             0.0)         # jump_threshold

print "=== Waiting while RVIZ displays plan3..."
rospy.sleep(5)

print "=================================== MOVING plan 3 = 3rd POSITION - Approximation point ==================================="
if fraction3 == 1.0:
    print 'planning was successful'
    raw_input()
    # MOVEMENT
    group.execute(plan3)
else:
    print 'planning was not successfull'
print fraction3

print "=================================== Generating plan 4 = 4th POSITION - Grasping point  ==================================="    

#=============== CHANGE WAYPOINTS4!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

P1_3to4 = Pose()
# + or -
P1_3to4.orientation.x = q[0]
P1_3to4.orientation.y = q[1]
P1_3to4.orientation.z = q[2]
P1_3to4.orientation.w = q[3]
P1_3to4.position.x = approx_point.x + (laser_reading/2)*normal.x
P1_3to4.position.y = approx_point.y + (laser_reading/2)*normal.y
P1_3to4.position.z = approx_point.z + (laser_reading/2)*normal.z

# Points for a clean path
waypoints4 = []

# start with the current pose
waypoints4.append(group.get_current_pose().pose)

# first orient gripper and move forward to P1_3to4
waypoints4.append(copy.deepcopy(P1_3to4))

# Final Position
pose_grasping_point = Pose()
pose_grasping_point.orientation.x = q[0]
pose_grasping_point.orientation.y = q[1]
pose_grasping_point.orientation.z = q[2]
pose_grasping_point.orientation.w = q[3]
pose_grasping_point.position.x = grasping_point.x
pose_grasping_point.position.y = grasping_point.y
pose_grasping_point.position.z = grasping_point.z
# group.set_pose_grasping_point(pose_grasping_point)

waypoints4.append(copy.deepcopy(pose_grasping_point))

(plan4, fraction4) = group.compute_cartesian_path(
                             waypoints4,   # waypoints4 to follow
                             0.01,        # eef_step
                             0.0)         # jump_threshold

print "=== Waiting while RVIZ displays plan4..."
rospy.sleep(5)

print "=================================== MOVING plan 4 = 4th POSITION - Grasping point ==================================="
if fraction4 == 1.0:
    print 'planning was successful'
    raw_input()
    # MOVEMENT
    group.execute(plan4)
else:
    print 'planning was not successfull'
print fraction4

# SUCTION

print "=================================== Generating plan 5 = 5th POSITION -Return to Approximation point  ==================================="    


#=============== CHANGE WAYPOINTS5!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Points for a clean path
waypoints5 = []

# start with the current pose
waypoints5.append(group.get_current_pose().pose)

# first orient gripper and move forward (+x)
waypoints5.append(copy.deepcopy(P1_3to4))

# Final Position
# pose_approx_point

# group.set_pose_eef_position(pose_eef_position)

waypoints5.append(copy.deepcopy(pose_approx_point))

(plan5, fraction5) = group.compute_cartesian_path(
                             waypoints5,   # waypoints5 to follow
                             0.01,        # eef_step
                             0.0)         # jump_threshold

print "=== Waiting while RVIZ displays plan5..."
rospy.sleep(5)

print "=================================== MOVING plan 5 = 5th POSITION -Return to Approximation point  ==================================="    

if fraction5 == 1.0:
    print 'planning was successful'
    raw_input()
    # MOVEMENT
    group.execute(plan5)
else:
    print 'planning was not successfull'
print fraction5


# q = tf.transformations.quaternion_from_euler(yaw, pitch, roll, 'rzyx')

# q = quaternion_from_euler(roll, pitch, yaw)

# print "The quaternion representation is %s %s %s %s." % (q[0], q[1], q[2], q[3])

# cr = cos(roll * 0.5)
# sr = sin(roll * 0.5)
# cp = cos(pitch * 0.5)
# sp = sin(pitch * 0.5)
# cy = cos(yaw * 0.5)
# sy = sin(yaw * 0.5)

# q.w() = cr * cy * cp + sr * sy * sp
# q.z() = sr * cy * cp - cr * sy * sp
# q.x() = cr * sy * cp - sr * cy * sp
# q.y() = cr * cy * sp + sr * sy * cp
