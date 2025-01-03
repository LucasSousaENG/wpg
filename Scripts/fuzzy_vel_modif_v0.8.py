# -*- coding: utf-8 -*-
#!/usr/bin/env python

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
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

global kp
global ki
global kd
global topico
global client

# Escrever o topico no qual deseja fazer a analise do PID
topico = '/arm_1/arm_controller/gains/arm_joint_2'

# Crie um cliente de reconfiguração dinâmica para poder modificar futuramente os valores de PID
client = Client(topico)

####################################################################################
#YOLO
# Coordenadas do ponto de interesse [x, y]
point_coordinates = [0, 0]
depth_at_point = 0.0  # Distância inicial
roi_size = 20  # Tamanho da região de interesse (largura e altura)

# Inicializando a ponte entre ROS e OpenCV
bridge = CvBridge()

# Carregando o modelo YOLOv3 e as classes
net = cv2.dnn.readNetFromDarknet('/home/lucas/Downloads/yolov3-tiny.cfg', '/home/lucas/Downloads/yolov3-tiny.weights')
classes = []
with open('/home/lucas/Downloads/coco.names', 'r') as f:
    classes = [line.strip() for line in f]

def round_float(x):
    max = 0.99
    min = 0.01
    if x in [float("-inf"),float("inf")]:
        return float(0)
    if x >= max:
        return max
    if x <= min:
        return min
    if np.isnan(x)== True:
        return float(0)
    return x

# Função de callback para o tópico de imagem
def image_callback(msg):
    global point_coordinates, depth_at_point

    try:
        # Convertendo a mensagem de imagem do ROS para um objeto OpenCV
        cv_image = bridge.imgmsg_to_cv2(msg, 'bgr8')
    except Exception as e:
        print(e)
        return

    # Configurando parâmetros para detecção de objetos
    height, width, _ = cv_image.shape
    #print(height, width)
    net.setInput(cv2.dnn.blobFromImage(cv_image, 0.00392, (416, 416), (0, 0, 0), True, crop=False))
    layer_names = net.getUnconnectedOutLayers()
    outs = net.forward(layer_names)

    # Lista para armazenar caixas delimitadoras, confiança e classes
    boxes = []
    confidences = []
    class_ids = []

    # Iterando sobre cada detecção
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.2:
                # Coordenadas da caixa delimitadora
                # Detection [0] e [1] sao os cantos esquerdos superiores e inferiores da imagem
                center_x, center_y = int(round_float(detection[0]) * width), int(round_float(detection[1]) * height)
                #print(detection[0])
                #print(detection[3])
                #print(detection[0])
                #print(detection[1])
                
                w, h = int(round_float(detection[2]) * width), int(round_float(detection[3]) * height)

                # Coordenadas da caixa delimitadora (canto superior esquerdo)
                x, y = int(center_x - w / 2), int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Aplicando supressão não máxima para evitar caixas delimitadoras sobrepostas
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.2, 0.2)

    # Desenhando caixas delimitadoras na imagem e adicionando informações de distância
    for i in range(len(boxes)):
        if i in indices:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])

            # Atualizando as coordenadas do ponto de interesse para o centroide da detecção
            point_coordinates = [int(x + w / 2), int(y + h / 2)]

            # Adicionando a distância à câmera na caixa delimitadora
            cv2.rectangle(cv_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = str(label + " | Distancia: " + str(depth_at_point) + "m")
            cv2.putText(cv_image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Exibindo a imagem com as caixas delimitadoras
    cv2.imshow('YOLOv3 Object Detection', cv_image)
    cv2.waitKey(3)

# Função de callback para o tópico de profundidade
def depth_callback(msg):
    global point_coordinates, depth_at_point

    # Verifique se as coordenadas do ponto de interesse foram atualizadas
    if point_coordinates != [0, 0]:
        # Converter a mensagem do ROS para uma matriz OpenCV
        depth_image = bridge.imgmsg_to_cv2(msg)

        # Coordenadas da area de interesse da imagem de (canto superior esquerdo e inferior direito)
        bbox_x1, bbox_y1 = max(0, point_coordinates[0] - 0.5 * roi_size), max(0, point_coordinates[1] - 0.5 * roi_size)
        bbox_x2, bbox_y2 = min(depth_image.shape[1], point_coordinates[0] + 0.5 * roi_size), min(depth_image.shape[0], point_coordinates[1] + 0.5 * roi_size)

        # Calcular a distância média na região de interesse
        roi_depth = depth_image[int(bbox_y1):int(bbox_y2), int(bbox_x1):int(bbox_x2)]
        depth_at_point = np.mean(roi_depth)

        # Exibir informações
        #rospy.loginfo("Coordenadas do ponto: " + str(point_coordinates[0]) + ", " + str(point_coordinates[1]))
        #rospy.loginfo("Distância no ponto: " + str(depth_at_point))
        #print("Distancia no ponto:" + str(depth_at_point))


###########################################################################
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

    if new_kp == 0.0 and new_ki == 0.0 and new_kd == 0.0:
        rospy.logwarn("Mensagem do Simulink contém parâmetros zerados. Ignorando.")
        return

    rospy.loginfo("Novo P: %s", new_kp)
    rospy.loginfo("Novo I: %s", new_ki)    
    rospy.loginfo("Novo D: %s", new_kd)
    rospy.loginfo("Nova distancia: %s", depth_at_point)

    print(new_kp, new_ki, new_kd)

    # Adicionar uma funcao que so acessa a nova etapa SE LER VALORES NOVOS DE PID
    change_PID(new_kp,new_ki,new_kd, float(depth_at_point))

    # Exiba os novos ganhos modificados
    receive_current_pid()

    print("teste")
    # Programa fica infinitamente travado aqui e nao sei como sair do rospy.subscriber
    return None



def change_PID(novo_P,novo_I,novo_D,dist):
    # Funcao que modifica os valores de PID antigos pelos novos
    print("\n Foram recebidos novos valores de PID\n Gostaria de realizar a modificacao dos valores antigos?")
    print("PID Antigo: P = %.3f, I = %.3f, D = %.3f" % (kp, ki, kd))
    print("PID Novo: P = %.3f, I = %.3f, D = %.3f, Distancia = %.3f" % (novo_P, novo_I, novo_D, dist))
    #print(str(depth_at_point))
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
        #time.sleep(1)

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

    #time.sleep(2)

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

    #rate = rospy.Rate(0.05)  # Taxa de publicação (0.05 Hz) (Simulacao roda rapido porem nao funciona direito no simulink)
    rate = rospy.Rate(1)  # Taxa de publicação (1 Hz)

    while not rospy.is_shutdown():
        # Assinando os tópicos de imagem e profundidade
        rospy.Subscriber('/camera2/color/image_raw', Image, image_callback)
        rospy.Subscriber('/camera2/depth/image_raw', Image, depth_callback)

        # Criando uma mensagem para os valores de PID (Aqui e enviado para o simulink)
        # Esses atributos "kP..." estao presentes no arquivo de mensagem fuzzy_lcs importado
        pid_msg = fuzzy()
        pid_msg.kP = (kp)
        pid_msg.kI = (ki)
        pid_msg.kD = (kd)
        pid_msg.obj_vel = float("{:.3f}".format(depth_at_point))

        # Publicando os valores no topico "valores_fuzzy"
        fuzzy_pub.publish(pid_msg)

        # Recebendo os dados do simulink via topico "valores_defuzzy"
        rospy.Subscriber('valores_defuzzy', defuzzy, receive_defuzzy)


        # Recebendo os valores atualizados dos parametros desejados
        receive_current_pid()

        rate.sleep()
