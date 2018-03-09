import subprocess
import time

NAO_IP = "192.168.137.17"
ROSCORE_IP = "192.168.137.201"

def nao_init():
    subprocess.Popen(["roslaunch", "nao_apps", "speech.launch", "nao_ip:=%s"%NAO_IP, "roscore_ip:=%s"%ROSCORE_IP])
    time.sleep(5)
    subprocess.Popen(["roslaunch", "nao_apps", "behaviors.launch", "nao_ip:=%s"%NAO_IP, "roscore_ip:=%s"%ROSCORE_IP])

def nao_talk(say):
    cmd = "rostopic pub /speech_action/goal naoqi_bridge_msgs/SpeechWithFeedbackActionGoal \"{goal: {say: '%s'}}\" -1"%say
    subprocess.Popen(["bash", "-c", cmd])

def nao_anim(anim):
    cmd = "rostopic pub /run_behavior/goal naoqi_bridge_msgs/RunBehaviorActionGoal \"{goal: {behavior: '%s'}}\" -1"%anim
    subprocess.Popen(["bash", "-c", cmd])

if __name__ == "__main__":
    nao_anim("animations/Sit/Gestures/You_4")
    time.sleep(1)
    nao_talk("Hey, toi! ...T''es mort.")
