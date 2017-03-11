#!/usr/bin/env python
# -*- coding: utf-8 -*-


#--------------------------------------------------
#Grannyの位置を記憶するROSノード
#
#author: Yutaro ISHIDA
#date: 16/03/16
#--------------------------------------------------


import sys
import roslib
sys.path.append(roslib.packages.get_pkg_dir('common_pkg') + '/scripts/common')

from common_import import *
from common_function import *


#--------------------------------------------------
#メイン関数
#--------------------------------------------------
if __name__ == '__main__':
    node_name = os.path.basename(__file__)
    node_name = node_name.split('.')
    rospy.init_node(node_name[0])

    if rospy.get_param('/param/dbg/sm/flow') == 0 and rospy.get_param('/param/dbg/speech/onlyspeech') == 0:        
        #commonf_speech_single('おばあさんの位置を記憶します。')

        tf_listener = tf.TransformListener()

        while not rospy.is_shutdown():
            while not rospy.is_shutdown():
                try:
                    (translation, rotation) = tf_listener.lookupTransform('/map', '/base_link', rospy.Time(0))
                except:
                    continue
                break

            granny_pos = rospy.get_param('/param/granny/pos')
            
            granny_pos['x'] = translation[0]
            granny_pos['y'] = translation[1]

            euler = euler_from_quaternion([rotation[0], rotation[1], rotation[2], rotation[3]])
            granny_pos['yaw'] = euler[2]

            rospy.set_param('/param/granny/pos', granny_pos)

            #commonf_speech_single('おばあさんの位置を記憶しました。')

            sys.exit()
