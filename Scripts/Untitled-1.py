#!/usr/bin/env python

import rospy
#from std_msgs.msg import Float64
from wpg.msg import fuzzy_lcs as fuzzy
from wpg.msg import defuzzy_lcs as defuzzy
import time
from dynamic_reconfigure.msg import Config
from dynamic_reconfigure.client import Client
import sys
from io import BytesIO

def callback(msg):
    parameters = msg.doubles  # ou msg.ints, msg.bools, msg.strs, etc. dependendo dos tipos de parametros
    for parameter in parameters:
        log_string = "Nome do Parametro: {}, Valor: {}\n".format(parameter.name, parameter.value)
        log_buffer.write(log_string.encode('utf-8'))

# Funcao que, quando chamada, printa os valores atuais de PID do topico requisitado
def receive_current_pid():
    # Crie um cliente de reconfiguração dinâmica
    client = Client('/arm_1/arm_controller/gains/arm_joint_2')

    # Obtenha a configuração atual dos parâmetros
    config = client.get_configuration()
    # Atualize os parâmetros através do serviço de reconfiguração dinâmica
    client.update_configuration(config)

    # Exiba os novos ganhos modificados
    rospy.loginfo("Novos ganhos do PID: P = {}, I = {}, D = {}".format(config['p'], config['i'], config['d']))

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

def receive_defuzzy(data):
    # Esta função será chamada sempre que uma mensagem for recebida no tópico "valores_defuzzy"
    # Faça o processamento dos dados recebidos aqui
    rospy.loginfo("Recebido: %s", data)
    log_defuzzy = log_buffer.getvalue().decode('utf-8')

    print(type(rospy.loginfo("Recebido: %s", data)))
    #new_kp = extract_pid(log_defuzzy, "New_P: ")
    #new_ki = extract_pid(log_defuzzy, "New_I: ")
    #new_kd = extract_pid(log_defuzzy, "New_D: ")

    #print(new_kp, new_ki, new_kd)

    time.sleep(1)

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

        # Publicando os valores no topico "valores_fuzzy"
        fuzzy_pub.publish(pid_msg)

        # Recebendo os dados do simulink via topico "valores_defuzzy"
        simulink_data = rospy.Subscriber('valores_defuzzy', defuzzy, receive_defuzzy)

        # Recuperando os valores no topico "valores_defuzzy"

        # Recebendo os valores atualizados dos parametros desejados
        receive_current_pid()

        rate.sleep()
