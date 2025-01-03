#!/usr/bin/env python

# VERIFICAR!!
# Linha 80 (Programa nao volta pro main depois de entrar na funcao rospy.subscriber)
# Funcao change_PID printa duas vezes, talvez ele esteja rodando duas vezes ao mesmo tempo

import rospy
#from std_msgs.msg import Float64
from wpg.msg import fuzzy_lcs as fuzzy
from wpg.msg import defuzzy_lcs as defuzzy
import time
from dynamic_reconfigure.msg import Config
from dynamic_reconfigure.client import Client
import sys
from io import BytesIO

global kp
global ki
global kd
global topico
global client

# Escrever o topico no qual deseja fazer a analise do PID
topico = '/arm_1/arm_controller/gains/arm_joint_2'

# Crie um cliente de reconfiguração dinâmica para poder modificar futuramente os valores de PID
client = Client(topico)

def callback(msg):
    parameters = msg.doubles  # ou msg.ints, msg.bools, msg.strs, etc. dependendo dos tipos de parametros
    for parameter in parameters:
        log_string = "Nome do Parametro: {}, Valor: {}\n".format(parameter.name, parameter.value)
        log_buffer.write(log_string.encode('utf-8'))

# Funcao que, quando chamada, printa os valores atuais de PID do topico requisitado
def receive_current_pid():
    # Ja criamos o cliente de configuracao dinamica no inicio do script

    # Obtenha a configuração atual dos parâmetros
    config = client.get_configuration()
    # Atualize os parâmetros através do serviço de reconfiguração dinâmica
    client.update_configuration(config)

def extract_pid(input_string, pid_var):
    #tipos de retornos
    falha_a = " falha 1"
    falha_b = " falha 2"
    index = input_string.find(pid_var)
    if index != -1:
        start_index = index + len(pid_var)
        end_index = input_string.find("\n", start_index)
        if end_index != -1:
            result = input_string[start_index:end_index]
            return result.strip()
        else:
            return falha_a
    else:
        return falha_b

def receive_defuzzy(data):
    # Esta função será chamada sempre que uma mensagem for recebida no tópico "valores_defuzzy"
    # Faça o processamento dos dados recebidos aqui
    #log_buffer_defuzzy = BytesIO()  #NAO DA PRA FAZER ASSIM PQ A MENSAGEM N E CALLBACK
    #data_str = "Campo1: %s, Campo2: %s" % (data.New_P, data.New_I)

    # Criar variaveis e atribuir os valores de novos P, I e D nelas nos campos estabelecidos no defuzzy_lcs
    new_kp = data.New_P
    new_ki = data.New_I
    new_kd = data.New_D

    # Verifica se os parametros obtidos estao zerados
    if new_kp == 0.0 and new_ki == 0.0 and new_kd == 0.0:
        rospy.logwarn("Mensagem do Simulink contém parâmetros zerados. Ignorando.")
        return

    rospy.loginfo("Novo P: %s", new_kp)
    rospy.loginfo("Novo I: %s", new_ki)    
    rospy.loginfo("Novo D: %s", new_kd)

    print(new_kp, new_ki, new_kd)

    # Adicionar uma funcao que so acessa a nova etapa SE LER VALORES NOVOS DE PID
    change_PID(new_kp,new_ki,new_kd)

    # Exiba os novos ganhos modificados
    receive_current_pid()

    print("teste")
    # Programa fica infinitamente travado aqui e nao sei como sair do rospy.subscriber
    return None



def change_PID(novo_P,novo_I,novo_D):
    # Funcao que modifica os valores de PID antigos pelos novos
    print("\n Foram recebidos novos valores de PID\n Gostaria de realizar a modificacao dos valores antigos?")
    print("PID Antigo: P = %.3f, I = %.3f, D = %.3f" % (kp, ki, kd))
    print("PID Novo: P = %.3f, I = %.3f, D = %.3f" % (novo_P, novo_I, novo_D))
    print("\t 's' para Sim e 'n' para Nao")

    resposta = raw_input()

    if resposta == "s":
        # Ja criamos o cliente de configuracao dinamica no inicio do script
        config = client.get_configuration()

        # Modificando os ganhos por meio do dynamic reconfiguire
        config['p'] = novo_P   
        config['i'] = novo_I       
        config['d'] = novo_D       

        # Atualize os parâmetros através do serviço de reconfiguração dinâmica
        client.update_configuration(config)

        # Exiba os novos ganhos modificados
        rospy.loginfo("Novos ganhos do PID: P = {}, I = {}, D = {}".format(config['p'], config['i'], config['d']))
        time.sleep(1)

        # Continua o script
        


    elif resposta == "n":
        print("Lucas, continue com o break talvez para continuar o script")
        return None
    else:
        print("Letra digitada equivocadamente")
        return None

if __name__ == '__main__':
    # Cria um buffer de bytes para armazenar os logs
    log_buffer = BytesIO()

    # inicia o no do ROS
    rospy.init_node('pid_publisher', anonymous=True)

    # Inicia o processo de subscricao para coletar os dados de PID do topico especifico
    rospy.Subscriber(str(topico + '/parameter_updates'), Config, callback)

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
        rospy.Subscriber('valores_defuzzy', defuzzy, receive_defuzzy)


        # Recebendo os valores atualizados dos parametros desejados
        receive_current_pid()

        rate.sleep()
