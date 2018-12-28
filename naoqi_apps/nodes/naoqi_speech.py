#!/usr/bin/env python

'''
ALTextToSpeech/Status
(http://doc.aldebaran.com/2-5/naoqi/audio/altexttospeech-api.html#ALTextToSpeech/Status)
value: [idOfConcernedTask, status]
status: "enqueued", "started", "thrown", "stopped", "done"

[flow of status]
(enqueued) => (started) => (thrown/ stopped/ done)
'''
# Note
'''
At first when launching this, 

rostopic echo /speech_status 
data: "done"

will appear even though you send any speech topic to a robot.
It is because the old data remains inside NAOqi API.
So, we should wait for a while before using /speech_status topic. 

kanae@kanae-ThinkPad-T480s:~/catkin_ws/src/naoqi_bridge/naoqi_apps/nodes$ rostic echo /speech_status 
data: "done" ## this is old data
---
data: "started" ## I send speech topic
---
data: "done"
---

'''

import rospy
from naoqi_driver.naoqi_node import NaoqiNode
from std_msgs.msg import String

class NaoqiSpeech(NaoqiNode):
    def __init__(self):
        NaoqiNode.__init__(self, 'naoqi_speech')
        self.connectNaoQi()
        self.rate = rospy.Rate(1)
        self.speechStatusPub = rospy.Publisher("speech_status", String, queue_size=10)
        self.speech_status = ""
        self.speech_task = -1
        
    def connectNaoQi(self):
        rospy.loginfo("Connecting to NaoQi at %s:%d", self.pip, self.pport)
        self.memProxy = self.get_proxy("ALMemory")
        if self.memProxy is None:
            rospy.logerr("Could not get a proxy to ALMemory")
            exit(1)
        test = self.memProxy.getData("ALTextToSpeech/Status")
        self.speech_task = test[0]

    def run(self):
        while self.is_looping():
            try:
                if self.speechStatusPub.get_num_connections() > 0:
                    test = self.memProxy.getData("ALTextToSpeech/Status")
                    if self.speech_task != test[0]:
                        self.speech_task = test[0]
                        self.speech_status = test[1]
                        tmp = String()
                        tmp.data = self.speech_status
                        self.speechStatusPub.publish(tmp)
                    # self.speech_task == test[0]:
                    elif self.speech_status != test[1]:
                        self.speech_status = test[1]
                        tmp = String()
                        tmp.data = self.speech_status
                        self.speechStatusPub.publish(tmp)
            except RuntimeError, e:
                pass
            self.rate.sleep()

if __name__ == '__main__':
    speech = NaoqiSpeech()
    speech.start()
    rospy.spin()
