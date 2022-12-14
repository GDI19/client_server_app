from socket import *
import time


s = socket(AF_INET, SOCK_STREAM)
s.bind(('', 8888))
s.listen(5)


while True:

    client, addr = s.accept()

    # print("Получен запрос на соединение от %s" % str(addr))
    # timestr = time.ctime(time.time()) + "\n"
    # client.send(timestr.encode("ascii"))

    data = client.recv(1024)
    print('Сообщение: ', data.decode('utf-8'), ', было отправлено клиентом: ', addr)

    msg = f'Привет, клиент '
    client.send(msg.encode('utf-8'))


    client.close()
