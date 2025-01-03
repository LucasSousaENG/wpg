#!/usr/bin/env python

import rospy
#from std_msgs.msg import Float64
from wpg.msg import fuzzy_lcs as fuzzy
from wpg.msg import defuzzy_lcs as defuzzy
import time
from dynamic_reconfigure.msg import Config
import sys
from io import BytesIO

def callback(msg):
    parameters = msg.doubles  # ou msg.ints, msg.bools, msg.strs, etc. dependendo dos tipos de parametros
    for parameter in parameters:
        log_string = "Nome do Parametro: {}, Valor: {}\n".format(parameter.name, parameter.value)
        log_buffer.write(log_string.encode('utf-8'))

def extract_pid(input_string, pid_var):
    index = input_string.find(pid_var)
    if index != -1:
        start_index = index + len(pid_var)
        end_index = input_string.find("\n", start_index)
        if end_index != -1:
            result = input_string[start_index:end_index]
            return result.strip()
        else:
            return None
    else:
        return None

def collect_pid_values():
    # Simulando a coleta de valores PID
    kp = 2000
    ki = 1
    kd = 0.1
    return kp, ki, kd

if __name__ == '__main__':
    # Cria um buffer de bytes para armazenar os logs
    log_buffer = BytesIO()

    # inicia o no do ROS
    rospy.init_node('pid_publisher', anonymous=True)

    # Inicia o processo de subscricao para coletar os dados de PID do topico especifico
    rospy.Subscriber('/arm_1/arm_controller/gains/arm_joint_2/parameter_updates', Config, callback)

    #print("\n Atualizacao")

    time.sleep(2)

    # Captura os logs do buffer e decodifica como uma string unicode
    ros_to_str = log_buffer.getvalue().decode('utf-8')

    # Faça o que quiser com os logs capturados
    print("Logs capturados:")
    print(ros_to_str)

    #Segmentar os valores de P, I e D para serem posteriormente enviados
    kp = float(extract_pid(ros_to_str, " p, Valor: "))
    ki = float(extract_pid(ros_to_str, " i, Valor: "))
    kd = float(extract_pid(ros_to_str, " d, Valor: "))
    print(kp, ki, kd)
    # Limpa o buffer para a próxima iteração
    log_buffer.truncate(0)  

    # Criando um publisher para o tópico "valores_fuzzy"
    fuzzy_pub = rospy.Publisher('valores_fuzzy', fuzzy, queue_size=10)

    rate = rospy.Rate(1)  # Taxa de publicação (1 Hz)

    while not rospy.is_shutdown():
        # Criando uma mensagem para os valores de PID
        # Esses atributos "kP..." estao presentes no arquivo de mensagem fuzzy_lcs importado
        pid_msg = fuzzy()
        pid_msg.kP = (kp)
        pid_msg.kI = (ki)
        pid_msg.kD = (kd)

        # Publicando os valores no tópico "valores_fuzzy"
        fuzzy_pub.publish(pid_msg)

        rate.sleep()
