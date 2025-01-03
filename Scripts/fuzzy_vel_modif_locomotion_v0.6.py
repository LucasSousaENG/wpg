import rospy
import std_msgs.msg
from geometry_msgs.msg import Twist
from wpg.msg import fuzzy_vel_modif as fuzzy
from wpg.msg import defuzzy_vel_modif as defuzzy
import time

old_speed = 1.0
h = std_msgs.msg.Header() #Cria um header para ser adicionado posteriormente

def read_distances():
    distances = []
    with open('/home/lucas/Downloads/distance.txt', 'r') as f:
        for line in f:
            distances.append(float(line.strip()))
    return distances

def read_speed():
    with open('/home/lucas/Downloads/velocity.txt', 'r') as f:
        time.sleep(0.5)
        #print(str(f.readline()))
        try:
            speed = float(f.readline())
            return speed
        except:
            print(str(f.readline()))

            #esse erro indica que em algum momento o arquivo esta sendo atualizado como uma sting


def callback(data):
    publish_distances()

def receive_new_velocity(data):
    global old_speed
    new_speed = data.new_velocity
    #print(is_float(new_speed))

    if new_speed == 0.0:
        rospy.logwarn("Mensagem do Simulink contem parametros zerados. Ignorando.")
        return

    #rospy.loginfo("Nova velocidade recebida do programa externo: %s", new_speed)
    if new_speed is not None:
        with open('/home/lucas/Downloads/velocity.txt', 'w') as f:
            f.write(str(new_speed))
            old_speed = new_speed
    
    else:
        with open('/home/lucas/Downloads/velocity.txt', 'w') as f:
            f.write(str(old_speed))

if __name__ == '__main__':
    rospy.init_node('distance_reader', anonymous=True)
    pub_distances = rospy.Publisher('entrada_fuzzy', fuzzy, queue_size=10)

    #rospy.loginfo("Distancia ate o objetivo (green_ball): %f", distance_to_goal)
    #rospy.loginfo("Distancia ate o obstaculo (red_ball): %f", distance_to_obstacle)
    #rospy.loginfo("Velocidade atual do robo: %f", speed)

    h.stamp = rospy.Time.now() #Primeiramente chamar rospy.init_node()
    
    rate = rospy.Rate(1)  # Taxa de publicacao

    while not rospy.is_shutdown():
        # Publica as distancias antes de subscrever a qualquer outro topico
        #Inicia o processo de obtencao de dados de distancia e velocidade
        distances = read_distances()
        distance_to_goal, distance_to_obstacle = distances[0], distances[1]
        speed = read_speed()
        vel_msg = fuzzy()
        vel_msg.distance_to_objective = distance_to_goal
        vel_msg.distance_to_obstacle = distance_to_obstacle
        vel_msg.velocity = speed
        print(speed)

        if vel_msg.velocity is not None:
            pub_distances.publish(vel_msg)
        else:
            vel_msg.velocity = old_speed
            pub_distances.publish(vel_msg)
        rospy.Subscriber('saida_defuzzy', defuzzy, receive_new_velocity)  # Subscreve para a nova velocidade do programa externo

        rate.sleep()
