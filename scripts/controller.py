#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion

import math
pi = 3.14159265359
pose = [0 , 0 ,0 ]
def Waypoints():
    x2 = list()
    y2 = list()	
    i=0	
    while i<=370:
    	i=i+5
        x  = pi *i/180 
    	y  = 2*(math.sin(x))*(math.sin(x/2))
        x2.append(round(x,2))
	y2.append(round(y,2))
    return [x2,y2]


def error_in_theatha(x,y):
    error = list()
    x1,y1,i=0,0,0
    while i < 73:
    	x2=x[i]
    	y2=y[i]			
    	error.append(round(math.atan((y2-y1)/(x2-x1)),2))
	x1,y1 = x2,y2
        i=i+1
	print("x :{0} ,y:{1}".format(x1,y1))
    return error 


def odom_callback(data):
    global pose
    x  = data.pose.pose.orientation.x;
    y  = data.pose.pose.orientation.y;
    z = data.pose.pose.orientation.z;
    w = data.pose.pose.orientation.w;
    pose[0] = data.pose.pose.position.x
    pose[1] = data.pose.pose.position.y
    pose[2]=euler_from_quaternion([x,y,z,w])[2]
    


def laser_callback(msg):
    global regions
    range_max = 144
    regions = {
        'bright': min(min(msg.ranges[0:144]),range_max)     ,
        'fright': min(min(msg.ranges[145:288]),range_max)   ,
        'front': min(min(msg.ranges[289:432]),range_max)    ,
        'fleft': min(min(msg.ranges[433:576]),range_max)    ,
        'bleft': min(min(msg.ranges[576:720]),range_max)    ,
    }
   



def control_loop():
    rospy.init_node('ebot_controller')
    
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rospy.Subscriber('/scan', LaserScan, laser_callback)
    rospy.Subscriber('/odom', Odometry, odom_callback)
    
    rate = rospy.Rate(10) 

    velocity_msg = Twist()
    velocity_msg.linear.x = 0
    velocity_msg.angular.z = 0
    pub.publish(velocity_msg)
    
    x2,y2=Waypoints()
    error=error_in_theatha(x2,y2) 
    
    i = 0	
    while not rospy.is_shutdown():
    	
    	#
    	# Your algorithm to complete the obstacle course
    	#
	
        rospy.loginfo("x:%f",pose[0])
        rospy.loginfo("y:%f",pose[1])
        rospy.loginfo("p:%f",pose[2])
	rospy.loginfo("i:%d",i)
	
	while pose[0]< x2[i]:
		velocity_msg.linear.x = 0.5
    		velocity_msg.angular.z = (error[i]-pose[2])*20
    		pub.publish(velocity_msg)
	
	i =i+1
	velocity_msg.linear.x = 0
    	velocity_msg.angular.z =0 
    	pub.publish(velocity_msg)
	if i ==10:
		rospy.loginfo(regions)		
			
		while not regions['front']==144:
			velocity_msg.linear.x = 0.9
    	                velocity_msg.angular.z =0.8
			pub.publish(velocity_msg)
			print("front:%f",regions['front'])

		while not regions['fright']==144:
			velocity_msg.linear.x = 0.3
    	                velocity_msg.angular.z = 0
			pub.publish(velocity_msg)
			print("fright:%f",regions['fright'])

		while regions['bright']!=144 and regions['bright']>0.5:
			velocity_msg.linear.x = 0.2
    	                velocity_msg.angular.z = -0.5
			pub.publish(velocity_msg)
			print("bright:%f",regions['bright'])
			print("fright:%f",regions['fright'])

		while regions['fright']!=144 and regions['fright']>0.5:
			velocity_msg.linear.x = 0.25
    	                velocity_msg.angular.z = -0.5
			pub.publish(velocity_msg)
			print("fright:%f",regions['fright'])
		
		while pose[0]<12.5 and pose[1]!=0 and pose[2]!=0:
			dx,dy = 12.5,0
			px,py = pose[0],pose[1]
			e = round(math.atan((dy-py)/(dx-px)),2)
			velocity_msg.linear.x = 0.5
    	        	velocity_msg.angular.z = (e-pose[2])*20
			pub.publish(velocity_msg)
		velocity_msg.linear.x = 0
    	        velocity_msg.angular.z =0
		pub.publish(velocity_msg)	               
		return 0
    	print("Controller message pushed at {}".format(rospy.get_time()))
    	rate.sleep()

     
if __name__ == '__main__':
    try:
        control_loop()
    except rospy.ROSInterruptException:
        pass
