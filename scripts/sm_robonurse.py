#!/usr/bin/env python
# -*- coding: utf-8 -*-


#--------------------------------------------------
#RCJ2016 Robo Nurse用ステートマシンのROSノード
#
#author: Yutaro ISHIDA
#date: 16/03/12
#--------------------------------------------------


import sys
import roslib
sys.path.append(roslib.packages.get_pkg_dir('common_pkg') + '/scripts/common')

from common_import import *
from common_function import *


rospy.sleep(5) #paramノードが立ち上がるまで待つ


#--------------------------------------------------
#ステートマシン設計規則
#--------------------------------------------------
#ステートを跨ぐデータはパラメータ(/param/以下)に保存する


#--------------------------------------------------
#--------------------------------------------------
class init(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class CamModeChange1(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        if rospy.get_param('/param/dbg/sm/flow') == 0 and rospy.get_param('/param/dbg/speech/onlyspeech') == 0:        
            commonf_speech_single('カメラモード切り替え中。')

            call(['rosnode', 'kill', '/camera/camera_nodelet_manager'])    
            call(['rosnode', 'kill', '/camera/depth_metric'])
            call(['rosnode', 'kill', '/camera/depth_metric_rect'])
            call(['rosnode', 'kill', '/camera/depth_points'])
            call(['rosnode', 'kill', '/camera/depth_rectify_depth'])
            call(['rosnode', 'kill', '/camera/depth_registered_rectify_depth'])
            call(['rosnode', 'kill', '/camera/points_xyzrgb_hw_registered'])
            call(['rosnode', 'kill', '/camera/rectify_color'])
            rospy.sleep(5)

            os.system('yes | rosnode cleanup')
            os.system('echo horihori|sudo -S service udev reload')
        
            Popen(['rosrun', 'openni_tracker', 'openni_tracker'])
            rospy.sleep(2)

        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class WaitStartSig(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        raw_input('#####Type enter key to start#####')

        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class ApproachToGranny(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        call(['rosrun', 'common_pkg', 'detect_approach_wave_hand.py'])

        commonf_dbg_sm_stepout()            
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class CamModeChange2(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        if rospy.get_param('/param/dbg/sm/flow') == 0 and rospy.get_param('/param/dbg/speech/onlyspeech') == 0:        
            commonf_speech_single('カメラモード切り替え中。')        

            commonf_node_killer('openni_tracker')
            rospy.sleep(5)
        
            os.system('yes | rosnode cleanup')
            os.system('echo horihori|sudo -S service udev reload')

            Popen(['roslaunch', 'openni2_launch', 'openni2.launch'])
            rospy.sleep(2)

        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class SLAM_RecordGrannyPos(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        call(['rosrun', 'robonurse_pkg', 'slam_recordgrannypos.py'])

        commonf_dbg_sm_stepout() 
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class SRec_AskForPills(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['exit1','err_in_speech_rec'])


    def execute(self,userdata):
        commonf_dbg_sm_stepin()

        commonf_actionf_cam_lift(0.000)
        commonf_pubf_mic_tilt(0.174)

        if commonf_actionf_speech_rec(self.__class__.__name__) == True: #音声認識ノードに現在のステートに対する処理が記述されていた時
            commonf_pubf_mic_tilt(-0.349)
            commonf_actionf_cam_lift(0.000)

            commonf_dbg_sm_stepout()
            return 'exit1'
        else: #音声認識ノードに現在のステートに対する処理が記述されていない時
            commonf_dbg_sm_stepout()            
            return 'err_in_speech_rec'


#--------------------------------------------------
#--------------------------------------------------
class SLAM_GoToPills1(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        pills_pos = rospy.get_param('/param/pills/pos')

        commonf_actionf_move_base(pills_pos['x'], pills_pos['y'], pills_pos['yaw'])

        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class ApproachToPills1(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        call(['rosrun', 'common_pkg', 'approach_obj.py'])
               
        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class Img_CntPills(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        call(['rosrun', 'common_pkg', 'img_obj_cnt'])
       
        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class BackFromPills1(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        commonf_speech_single('４５センチ後退。')
        
        commonf_pubf_cmd_vel(-0.15, 0, 0, 0, 0, 0)
        rospy.sleep(3)
        commonf_pubf_cmd_vel(0, 0, 0, 0, 0, 0)
        
        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class SLAM_GoToGranny1(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        granny_pos = rospy.get_param('/param/granny/pos')

        commonf_actionf_move_base(granny_pos['x'], granny_pos['y'], granny_pos['yaw'])

        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class SRec_WhichPillsToBring(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['exit1','err_in_speech_rec'])


    def execute(self,userdata):
        commonf_dbg_sm_stepin()

        commonf_actionf_cam_lift(0.435)
        commonf_pubf_mic_tilt(0.174)

        if commonf_actionf_speech_rec(self.__class__.__name__) == True: #音声認識ノードに現在のステートに対する処理が記述されていた時
            commonf_pubf_mic_tilt(-0.349)
            commonf_actionf_cam_lift(0.435)

            commonf_dbg_sm_stepout()
            return 'exit1'
        else: #音声認識ノードに現在のステートに対する処理が記述されていない時
            commonf_dbg_sm_stepout()            
            return 'err_in_speech_rec'


#--------------------------------------------------
#--------------------------------------------------
class SLAM_GoToPills2(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        pills_pos = rospy.get_param('/param/pills/pos')

        commonf_actionf_move_base(pills_pos['x'], pills_pos['y'], pills_pos['yaw'])

        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class ARM_Open(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()
        
        call(['rosrun', 'common_pkg', 'iarm_open.py'])

        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class ApproachToPills2(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        call(['rosrun', 'common_pkg', 'approach_obj.py'])
               
        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class Img_DetectPills(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1', 'exit2'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()
 
        if call(['rosrun', 'common_pkg', 'img_obj_detect']) == 0:
            commonf_dbg_sm_stepout()
            return 'exit1'
        else:
            commonf_dbg_sm_stepout()
            return 'exit2'


#--------------------------------------------------
#--------------------------------------------------
class ARM_GraspPills(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        Popen(['roslaunch', 'common_pkg', 'ar_tracker.launch'])

        call(['rosrun', 'common_pkg', 'iarm_grasp.py'])

        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class BackFromPills2(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        commonf_speech_single('４５センチ後退。')
        
        commonf_pubf_cmd_vel(-0.15, 0, 0, 0, 0, 0)
        rospy.sleep(3)
        commonf_pubf_cmd_vel(0, 0, 0, 0, 0, 0)
        
        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class ARM_Close(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()
        
        call(['rosrun', 'common_pkg', 'iarm_close.py'])
                
        commonf_node_killer('ar_track_alvar')

        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class SLAM_GoToGranny2(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        granny_pos = rospy.get_param('/param/granny/pos')

        commonf_actionf_move_base(granny_pos['x'], granny_pos['y'], granny_pos['yaw'])

        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class ARM_Hand(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()
        
        call(['rosrun', 'common_pkg', 'iarm_hand.py'])

        Popen(['roslaunch', 'common_pkg', 'ar_tracker.launch'])

        call(['rosrun', 'common_pkg', 'iarm_close.py'])

        commonf_node_killer('ar_track_alvar')
         
        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#メイン関数
#--------------------------------------------------
if __name__ == '__main__':
    node_name = os.path.basename(__file__)
    node_name = node_name.split('.')
    rospy.init_node(node_name[0])


    sm = smach.StateMachine(outcomes=['exit'])


    #起動音を再生する
    commonf_actionf_sound_effect_single('launch')

   
    commonf_pubf_scan_mode('lrf')

    commonf_pubf_cam_pan(0.523)
    commonf_pubf_cam_tilt(0.523)
    commonf_pubf_mic_pan(-0.523)
    commonf_pubf_mic_tilt(-0.523)
    rospy.sleep(0.5)
    commonf_pubf_cam_pan(0)
    commonf_pubf_cam_tilt(0)
    commonf_pubf_mic_pan(0)
    commonf_pubf_mic_tilt(-0.349)
    rospy.sleep(0.5)

    commonf_pubf_cmd_vel(0, 0, 0, 0, 0, 0)

    commonf_actionf_cam_lift(0)


    #commonf_speech_single('タスク、ロボナースをスタート。')
    #commonf_speech_single('スタートステートを指定して下さい。')
    rospy.loginfo('タスク、ロボナースをスタート')
    rospy.loginfo('スタートステートを指定して下さい')

    print '#####If you want to start from first state, please type enter key#####'
    start_state = raw_input('#####Please Input First State Name##### >> ')
    if not start_state:
        start_state = 'CamModeChange1'

    #commonf_speech_single('ステートマシンをスタート。')
    rospy.loginfo('ステートマシンをスタート')


    with sm:
        smach.StateMachine.add('init', init(), 
                               transitions={'exit1':start_state})
        smach.StateMachine.add('CamModeChange1', CamModeChange1(), 
                               transitions={'exit1':'WaitStartSig'})
        smach.StateMachine.add('WaitStartSig', WaitStartSig(), 
                               transitions={'exit1':'ApproachToGranny'})
        smach.StateMachine.add('ApproachToGranny', ApproachToGranny(), 
                               transitions={'exit1':'CamModeChange2'})
        smach.StateMachine.add('CamModeChange2', CamModeChange2(), 
                               transitions={'exit1':'SLAM_RecordGrannyPos'})
        smach.StateMachine.add('SLAM_RecordGrannyPos', SLAM_RecordGrannyPos(), 
                               transitions={'exit1':'SRec_AskForPills'})
        smach.StateMachine.add('SRec_AskForPills', SRec_AskForPills(),
                               transitions={'exit1':'SLAM_GoToPills1',
                                            'err_in_speech_rec':'exit'})
        smach.StateMachine.add('SLAM_GoToPills1', SLAM_GoToPills1(), 
                               transitions={'exit1':'ApproachToPills1'})
        smach.StateMachine.add('ApproachToPills1', ApproachToPills1(), 
                               transitions={'exit1':'Img_CntPills'})
        smach.StateMachine.add('Img_CntPills', Img_CntPills(), 
                               transitions={'exit1':'BackFromPills1'})
        smach.StateMachine.add('BackFromPills1', BackFromPills1(), 
                               transitions={'exit1':'SLAM_GoToGranny1'})
        smach.StateMachine.add('SLAM_GoToGranny1', SLAM_GoToGranny1(), 
                               transitions={'exit1':'SRec_WhichPillsToBring'})
        smach.StateMachine.add('SRec_WhichPillsToBring', SRec_WhichPillsToBring(),
                               transitions={'exit1':'SLAM_GoToPills2',
                                            'err_in_speech_rec':'exit'})
        smach.StateMachine.add('SLAM_GoToPills2', SLAM_GoToPills2(), 
                               transitions={'exit1':'ARM_Open'})
        smach.StateMachine.add('ARM_Open', ARM_Open(), 
                               transitions={'exit1':'ApproachToPills2'})
        smach.StateMachine.add('ApproachToPills2', ApproachToPills2(), 
                               transitions={'exit1':'Img_DetectPills'})
        smach.StateMachine.add('Img_DetectPills', Img_DetectPills(),
                               transitions={'exit1':'ARM_GraspPills',
                                            'exit2':'exit'})
        smach.StateMachine.add('ARM_GraspPills', ARM_GraspPills(), 
                               transitions={'exit1':'BackFromPills2'})
        smach.StateMachine.add('BackFromPills2', BackFromPills2(), 
                               transitions={'exit1':'ARM_Close'})
        smach.StateMachine.add('ARM_Close', ARM_Close(), 
                               transitions={'exit1':'SLAM_GoToGranny2'})
        smach.StateMachine.add('SLAM_GoToGranny2', SLAM_GoToGranny2(), 
                               transitions={'exit1':'ARM_Hand'})
        smach.StateMachine.add('ARM_Hand', ARM_Hand(), 
                               transitions={'exit1':'exit'})


    sis = smach_ros.IntrospectionServer('sm', sm, '/SM_ROOT')
    sis.start()


    outcome = sm.execute()


    commonf_speech_single('タスクを終了します。')
    raw_input('#####Type Ctrl + c key to end#####')


    while not rospy.is_shutdown():
        rospy.spin()
