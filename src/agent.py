import rospy
import random
import numpy as np
import math

from std_msgs.msg import String
import sensor_msgs.msg
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import tf
import random
from std_msgs.msg import Empty
from time import time

from qTable import qTable

class qAgent():
    def __init__(self,
                 _env):
        # self.rospy.init_node('qAgent')
        self.turtleName = ""
        self.velocityTopic = '/mobile_base/commands/velocity'
        self.totalReward = 0
        self.velPub = rospy.Publisher(self.velocityTopic, Twist, queue_size=10)
        self.reset_odom = rospy.Publisher('/mobile_base/commands/reset_odometry', Empty, queue_size=10)
        self.isCollision = False
        self.LINX = 0.0 #Always forward linear velocity.
        self.minRange = 0.6 #THRESHOLD value for laser scan.
        self.currentState = 0
        self.nextState = 0
        self.env = _env
        self.islearning = True
        self.currentPos = (0.0,0.0)
        self.yaw = 0.0

    def doAction(self, action):
        twist = self.genActionMsg(action)
        rospy.loginfo(twist)
        self.velPub.publish(twist)

    def learn(self,
              prevStateIndex,
              prevAction,
              currentState,
              reward):
        pass

    def getAction(self,
                  qClass,
                  currState):
        if self.islearning:
            return qClass.eGreedyPolicy(currState)
#        else:
#            qVals = qClass.qTable.setdefault(currState)
#            posQvals = [qVals[self.actionDict[act]] for act in possibleActions]
#            maxNdx = posQvals.index(max(posQvals))
#            maxAct = possibleActions[maxNdx]
#        return maxAct

    def genActionMsg(self,actionIndex):
        twist = Twist()
        if actionIndex == 0:
            twist.linear.x = 0.2
            twist.angular.z = 0
        elif actionIndex == 1:
            twist.linear.x = 0.05
            twist.angular.z = 0.3
        elif actionIndex == 2:
            twist.linear.x = 0.05
            twist.angular.z = -0.3
        else:
            twist.linear.x = 0
            twist.angular.z = 0
        return twist

    def LaserScanProcess(self, data):
        self.isCollision = False
        state = []
        mod = round(len(data.ranges)/4)
        for ndx,val in enumerate(data.ranges):
            if ndx % mod == 0:
                if math.isnan(val):
                    state.append(6)
                else:
                    state.append(int(val))
            if val < self.minRange:
                self.isCollision = True
        self.currentState = self.env.stateDict[tuple(state)]
#        rospy.loginfo("laser scan Callback")
        
    def odometry(self, msg):
        loc = msg.pose.pose.position
        self.currentPos = (loc.x,loc.y)
        orient = msg.pose.pose.orientation
        quaternion = (orient.x,
                      orient.y,
                      orient.z,
                      orient.w)
        euler = tf.transformations.euler_from_quaternion(quaternion)
        self.yaw = euler[2]
#        print("odomInput",self.currentPos,self.yaw)

    
    def getReward(self, prevAction):
        if self.isCollision:
            return -200
        if prevAction == 0:
            return 4
        elif prevAction == 1:
            return 2
        elif prevAction == 2:
            return 2
        else:
            return 0
            
    def reset(self):
        self.totalReward = 0
        timer = time()
#        while time() - timer < 0.25:
        self.reset_odom.publish(Empty())
        
