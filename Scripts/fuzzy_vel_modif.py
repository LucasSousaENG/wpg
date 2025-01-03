#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from mavros.utils import *
from mavros_msgs.msg import *
from mavros_msgs.srv import *

from wpg.msg import fuzzy as fuzzy_msg
from wpg.msg import defuzzyfied as defuzzy_msg
from wpg.msg import vehicle_smc_gains as vehicle_smc_gains_msg

from mavros import setpoint as SP
from tf.transformations import quaternion_from_euler

import math
import numbers
# TODO: update PySimpleGUI27 to PySimpleGUI 
import PySimpleGUI27 as sg
import _thread as thread
import time

# PID constants
KPx = KPy = KPz = 2.6
KIx = KIy = KIz = 0.25
KDx = KDy = KDz = 0.4

# non-brutness of fuzzy
SOFTNESS = 50

# set this variable to false to use the control panel
TEST_FLIGHT_MODE = True

# default reaching distance
DEFAULT_REACH_DIST = 0.1
DEFAULT_REACH_DIST_FOR_DEBUG = 0.05

# initial altitude
INITIAL_ALTITUDE = 0.5

# GAMBIT

######################
class SetpointVelocity:
    def init(self, _x, _y, _z):
        self.x = _x
        self.y = _y
        self.z = _z
        self.x_vel = 0
        self.y_vel = 0
        self.z_vel = 0

        self.reaching_distance = DEFAULT_REACH_DIST

        self.done_evt = threading.Event()

        # publisher for fuzzy (test)
        self.pub_fuz = rospy.Publisher('fuzzy_values', fuzzy_msg, queue_size=10)
        # subscriber for fuzzy (test)
        self.sub_fuz = rospy.Subscriber('defuzzy_values', defuzzy_msg, self.calculate_fuzzy)

    def start(self):
        self.activated = True
        self.fuzzyfy = False

        class Fuzzy_diff:
            def __init__(self):
                self.P_X = 0
                self.I_X = 0
                self.D_X = 0
                self.P_Y = 0
                self.I_Y = 0
                self.D_Y = 0
                self.P_Z = 0
                self.I_Z = 0
                self.D_Z = 0

    def calculate_fuzzy(self, fuz_topic):
        # TODO: implement Y and Z axis too
        self.defuzzed.P_X = fuz_topic.Delta_P_val
        self.defuzzed.I_X = fuz_topic.Delta_I_val
        self.defuzzed.D_X = fuz_topic.Delta_D_val


        ref_pose_msg = SP.PoseStamped(
            header=SP.Header(
                frame_id="setpoint_position",  # no matter, plugin don't use TF
                stamp=rospy.Time.now()
            ),  # stamp should update
        )
        fuz_msg = fuzzy_msg(
            header=SP.Header(
                frame_id="fuzzy_values",  # no matter, plugin don't use TF
                stamp=rospy.Time.now()
            ),  # stamp should update
        )
        if self.fuzzyfy:
            # TODO: fuzzy com y e z
            rospy.loginfo_once("initalized fuzzyfication for the fist time")
            if not self.defuzzed.P_X == 0:
                rospy.loginfo_once("first value of P_X modified by fuzzy system")
                rospy.loginfo_once("P_x = "+ (str(self.defuzzed.P_X)))
            global KPx
            KPx += self.defuzzed.P_X/SOFTNESS
            if KPx <= 0.6: KPx = 0.6
            if KPx >= 5.6: KPx = 5.6
            global KIx
            KIx += self.defuzzed.I_X/SOFTNESS
            if KIx <= 0.3: KIx = 0.3
            if KIx >= 4.5: KIx = 4.5
            global KDx
            KDx += self.defuzzed.D_X/SOFTNESS
            if KDx <= 0.1: KDx = 0.1
            if KDx >= 0.8: KDx = 0.8

        self.error.x.act = self.x - DronePose.x     #modificar para a posicao atual do robo
        self.error.y.act = self.y - DronePose.y
        self.error.z.act = self.z - DronePose.z

        PX = self.error.x.act * KPx
        PY = self.error.y.act * KPy
        PZ = self.error.z.act * KPz

        _time_bet_run = (rate.sleep_dur.nsecs / 1000000000.0)

        DX = ((self.error.x.Deri) * float(KDx)) / _time_bet_run
        DY = ((self.error.y.Deri) * float(KDy)) / _time_bet_run
        DZ = ((self.error.z.Deri) * float(KDz)) / _time_bet_run

        self.error.x.Intg = self.error.x.act * KIx * _time_bet_run
        IX = self.error.x.Intg
        self.error.y.Intg = self.error.y.act * KIy * _time_bet_run
        IY = self.error.y.Intg
        self.error.z.Intg = self.error.z.act * KIz * _time_bet_run
        IZ = self.error.z.Intg


        fuz_msg.Error = self.error.x.act
        fuz_msg.D_Error = self.error.x.Deri
        fuz_msg.P_val = KPx
        fuz_msg.I_val = KIx
        fuz_msg.D_val = KDx

        fuz_msg.header.stamp = rospy.Time.now()
        self.pub_fuz.publish(fuz_msg)

        rate.sleep()

