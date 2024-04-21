# server_thread dictionary exit
# 클라이언트로 부터 exit 문자열이 올때까지 계속 수신
# exit 문자열을 수신하면 while 문 탈출하여 연결종료

from socket import *
from select import * 
from threading import Thread, Event
from datetime import datetime
import emoji

event = Event()  # 키보드 입력받으면 키보드 종료시키기 위한 이벤트

HOST = ''
PORT = 5007
BUFSIZE = 1024
ADDR = (HOST, PORT)

invalidUserCount = 0 #유효하지 않은 사용자를 단톡방에 초대한 경우의 에러 횟수
invalidPermissionCount = 0 #채팅방에 참여하지 않았거나 존재하지 않는 채팅방의 채팅 메서드에 접근한 경우의 에러 횟수

# 연결된 client의 소켓 집합 set of connected client sockets
clientSockets = {}
# client의 소켓의 ID 집합
id = []
# 단체체팅방 정보를 담은 딕셔너리
multiInfo = {}

def joinServer(cs, m):
    tokens = m.split(':')
    myID = tokens[1]
    time = tokens[2]

    print(f"등록 ID:{myID}")
    clientSockets[myID] = cs
    id.append(myID)
    cs.send(f"{myID} 등록에 성공했습니다".encode()) #서버->클라
    for socket in clientSockets.values(): # 접속시 다른 클라이언트에게 알림
        socket.send(f"{myID}가 접속했습니다!".encode()) #서버->클라
    return True
    
def showUser(cs, m):
    tokens = m.split(':')
    fromID = tokens[1] #보내는사람
    time = tokens[2]

    toSocket = clientSockets.get(fromID)
    toSocket.send(f"현재 {id} 총 {len(id)}명 접속중입니다!".encode()) #서버->클라
    return True

def broadcastChat(cs, m):
    tokens = m.split(':')
    print('broadcast data: ', m)

    fromId = tokens[1]
    BRFcount = tokens[2]
    BRFcount = int(BRFcount)
    err = tokens[3]
    time = tokens[4]

    if tokens[3] == "no err" :
        msg = tokens[5]
        icon = tokens[6]
        for socket in clientSockets.values(): # broadcast
            if (cs == socket): #보낼 클라이언트 소켓집합
                cs.send("BR 메시지 전송 성공".encode())
                cs.send(f"{icon} {fromId} : {msg}".encode())
            elif (cs != socket):
                socket.send(f"{icon} {fromId} : {msg}".encode())
        return True
    else :
        cs.send(f"BR 메시지 전송 실패! 전송시도횟수:{BRFcount}".encode())
        #부정확한 입력형식으로 인한 전송실패횟수가 5의 배수에 해당한다면, 올바른 메시지 입력형식을 클라이언트에게 안내
        if BRFcount % 5 == 0:
            cs.send(f"':'을 포함하여 'BR:메시지'형식에 맞춰서 입력해주세요.".encode())

def unicastChat(cs, m):
    global invalidUserCount
    tokens = m.split(':')

    myID = tokens[1]
    UNFcount = tokens[2]
    UNFcount = int(UNFcount)
    err = tokens[3]
    time = tokens[4]

    if err == "no err" : #형식은 올바름
        toID = tokens[5]
        msg = tokens[6]
        if toID in id : #보낼 사용자가 유효한 경우
            toSocket = clientSockets.get(toID)
            toSocket.send(f"{myID} : {msg} ({time})".encode())
            cs.send(f"{toID}님에게 메시지 전송 성공".encode())
            cs.send(f"{myID} : {msg} ({time})".encode())
        else:
            invalidUserCount += 1
            cs.send(f"전송 실패! 유효하지 않은 사용자가 있습니다. 유효하지 않은 사용자를 포함한 채팅방 생성시도횟수:{invalidUserCount}".encode())
              #존재하지 않는 사용자로 인한 전송실패횟수가 5의 배수에 해당한다면, 올바른 메시지 입력형식과 접속중인 사용자를 클라이언트에게 안내
            if invalidUserCount % 5 == 0:
                cs.send(f"현재 {id}님이 접속중입니다!".encode())
                cs.send(f"':'과 '/'을 포함하여 ''UN:전송할 사용자:메시지'형식에 맞춰서 입력해주세요.".encode())
                cs.send(f"접속중인 사용자만 메시지를 전송해주세요.".encode())
        
    else : #형식이 올바르지 않은 경우
        cs.send(f"UN 메시지 전송 실패! 전송시도횟수:{UNFcount}".encode())
         #부정확한 입력형식으로 인한 전송실패횟수가 5의 배수에 해당한다면, 올바른 메시지 입력형식과 접속중인 사용자를 클라이언트에게 안내
        if UNFcount % 5 == 0:
            cs.send(f"현재 {id}님이 접속중입니다!".encode())
            cs.send(f"':'을 포함하여 'UN:보낼사용자:메시지'형식에 맞춰서 입력해주세요.".encode())

    return True

def makeMulticastChat(cs, m):
    global invalidUserCount
    tokens = m.split(':')

    myID = tokens[1]
    MUFcount = tokens[2]
    MUFcount = int(MUFcount)
    err = tokens[3]
    time = tokens[4]

    # 빈 set 생성
    ChatUsers = set()
    toUsers = [] #초대당한 사람들 리스트

    if tokens[3] == "no err" :
        roomID = tokens[5]
        joinUsers = tokens[6] #a/b/c ...
        usersToken = joinUsers.split("/") #입력받아온 만큼 /로 나누기

        if all(user in id for user in usersToken): #초대할 사용자들이 모두 유효한 경우
            invalidUserCount = 0
            for user in usersToken:
                ChatUsers.add(user)
                toUsers.append(user)

            ChatUsers.add(myID) #만든이 포함

            multiInfo[roomID] = ChatUsers #딕셔너리에 단톡방 정보 등록

            for toID in ChatUsers:
                toSocket = clientSockets.get(toID)
                toSocket.send(f"{myID}님이 {roomID}방에 {toUsers}님을 초대하였습니다".encode())
            cs.send(f"{roomID}방이 생성됐습니다!".encode())

        else:
            invalidUserCount += 1
            cs.send(f"방 생성 실패! 유효하지 않은 사용자가 있습니다. 유효하지 않은 사용자를 포함한 채팅방 생성시도횟수:{invalidUserCount}".encode())
              #존재하지 않는 사용자로 인한 전송실패횟수가 5의 배수에 해당한다면, 올바른 메시지 입력형식과 접속중인 사용자를 클라이언트에게 안내
            if invalidUserCount % 5 == 0:
                cs.send(f"현재 {id}님이 접속중입니다!".encode())
                cs.send(f"':'과 '/'을 포함하여 ''MU:생성할 방 이름:초대할 사용자1/초대할 사용자2 ..'형식에 맞춰서 입력해주세요.".encode())
                cs.send(f"접속중인 사용자만 초대해주세요.".encode())
    else :
        cs.send(f"방 생성 실패! 단체 톡방 생성시도횟수:{MUFcount}".encode())
        #부정확한 입력형식으로 인한 전송실패횟수가 5의 배수에 해당한다면, 올바른 메시지 입력형식과 접속중인 사용자를 클라이언트에게 안내
        if MUFcount % 5 == 0:
            cs.send(f"현재 {id}님이 접속중입니다!".encode())
            cs.send(f"':'과 '/'을 포함하여 ''MU:생성할 방 이름:초대할 사용자1/초대할 사용자2 ..'형식에 맞춰서 입력해주세요.".encode())

    return True

def showMulticastChatList(cs, m): #단톡방 목록 조회
    tokens = m.split(':')
    fromID = tokens[1] #보내는사람
    toSocket = clientSockets.get(fromID)

    myMuList=[]
    
    if any( fromID in value for value in multiInfo.values()):
        for key, value in multiInfo.items():
            if fromID in value:
                myMuList.append(key)
        toSocket.send(f"현재 {myMuList} 채팅방에 참여중입니다!".encode()) #서버->클라
    else:
        toSocket.send(f"{fromID}님은 현재 참여중인 채팅방이 없습니다!".encode()) #서버->클라

    return True

def exitMulticastChat(cs, m):
    global invalidPermissionCount
    tokens = m.split(':')

    myID = tokens[1]
    OUTcount = tokens[2]
    OUTcount = int(OUTcount)


    err = tokens[3]
    time = tokens[4]

    if tokens[3] == "no err" :
        roomID = tokens[5]
        if roomID in multiInfo: #존재하는 단톡방인지 확인
            if myID in multiInfo[roomID]: #나갈 사람이 채팅방에 소속되어 있는지 확인
                invalidPermissionCount = 0
                try:
                    for toID in multiInfo[roomID]:
                        if toID != myID:  # 나가는 사용자는 제외하고 메시지 전송
                            toSocket = clientSockets.get(toID)
                            toSocket.send(f"{roomID}방에서 {myID}님이 나가셨습니다. ({time})".encode())

                    cs.send(f"{roomID}에서 나가기 성공!".encode())

                    # 채팅방에서 myID 제거
                    multiInfo[roomID].remove(myID)
                except Exception as e:
                    cs.send(f"나가기 실패: {e} 이유:{e}".encode())
            else:
                invalidPermissionCount += 1
                cs.send(f"방의 참여자가 아니므로 나갈 수 없습니다. 나가기 시도 횟수:{invalidPermissionCount}".encode())
                #방에서 나갈 권한이 없는 경우로 인한 전송실패횟수가 5의 배수에 해당한다면, 올바른 메시지 입력형식과 참여중인 채팅방 안내
                if invalidPermissionCount % 5 == 0:
                    showMulticastChatList(myID, f"SMU:{myID}:{time}")
                    cs.send(f"참여중인 채팅방만 나갈 수 있습니다.".encode())
        else:
            invalidPermissionCount += 1
            cs.send(f"{roomID}은 존재하지 않는 채팅방입니다. 나가기 시도 횟수:{invalidPermissionCount}".encode())
            #방에서 나갈 권한이 없는 경우로 인한 전송실패횟수가 5의 배수에 해당한다면, 올바른 메시지 입력형식과 참여중인 채팅방 안내
            if invalidPermissionCount % 5 == 0:
                showMulticastChatList(myID, f"SMU:{myID}:{time}")
                cs.send(f"참여중인 채팅방만 나갈 수 있습니다.".encode())
    else :
        cs.send(f"채팅방 나가기 실패! 채팅방 나가기 시도횟수:{OUTcount}".encode())
         #부정확한 입력형식으로 인한 전송실패횟수가 5의 배수에 해당한다면, 올바른 메시지 입력형식을 안내
        if OUTcount % 5 == 0:
            cs.send(f"':'을 포함하여 'OUT:방 이름'형식에 맞춰서 입력해주세요.".encode())
    return True

def multicastChat(cs, m):
    global invalidPermissionCount
    tokens = m.split(':')

    myID = tokens[1]
    MUCFcount = tokens[2]
    MUCFcount = int(MUCFcount)
    err = tokens[3]
    time = tokens[4]

    if tokens[3] == "no err" :
        roomID = tokens[5]
        msg = tokens[6]
        if roomID in multiInfo: #존재하는 단톡방인지 확인
            if myID in multiInfo[roomID]: #보내는 사람이 단톡방에 소속되어 있는지 확인
                invalidPermissionCount = 0
                try:
                    for toID in multiInfo[roomID]:
                        toSocket = clientSockets.get(toID)
                        toSocket.send(f"{roomID} / {myID} : {msg} ({time})".encode())
                    cs.send(f"{roomID}에 메시지 전송 성공!".encode())
                except Exception as e:
                    print(f"메시지 전송 실패: {e}")
                    cs.send(f"메시지 전송 실패: {e} 이유:{e}".encode())
            else:
                invalidPermissionCount += 1
                cs.send(f"방의 참여자가 아니라면 전송 할 수 없습니다. 메시지 전송 시도 횟수:{invalidPermissionCount}".encode())
                #권한이 없는 경우로 인한 전송실패횟수가 5의 배수에 해당한다면, 올바른 메시지 입력형식과 참여중인 채팅방 안내
                if invalidPermissionCount % 5 == 0:
                    showMulticastChatList(myID, f"SMU:{myID}:{time}")
                    cs.send(f"참여중인 채팅방만 메시지를 전송할 수 있습니다.".encode())
        else:
            invalidPermissionCount += 1
            cs.send(f"{roomID}은 존재하지 않는 채팅방입니다. 메시지 전송 시도 횟수:{invalidPermissionCount}".encode())
            #권한이 없는 경우로 인한 전송실패횟수가 5의 배수에 해당한다면, 올바른 메시지 입력형식과 참여중인 채팅방 안내
            if invalidPermissionCount % 5 == 0:
                showMulticastChatList(myID, f"SMU:{myID}:{time}")
                cs.send(f"참여중인 채팅방만 나갈 수 있습니다.".encode())
    else :
        cs.send(f"그룹채팅 메시지 전송 실패! 메시지 전송시도횟수:{MUCFcount}".encode())
         #부정확한 입력형식으로 인한 전송실패횟수가 3의 배수에 해당한다면, 올바른 메시지 입력형식을 안내
        if MUCFcount % 3 == 0:
            cs.send(f"':'을 포함하여 'MUC:방 이름:메시지' 형식에 맞춰서 입력해주세요.".encode())
    return True

def exitServer(cs, m):
    tokens = m.split(':')
    fromID = tokens[1]
    clientSockets.pop(fromID)
    id.remove(fromID)
    cs.close()
    for socket in clientSockets.values(): # 종료시 다른 클라이언트에게 알림
        socket.send(f"{fromID}가 종료했습니다!".encode()) #서버->클라
    print(f"연결종료ID:{fromID}")
    return False
       
def msg_proc(cs, m): #ID 메시지, 1:1 메시지, 브로드캐스트 메시지, 종료 메시지 등을 처리
    global clientSockets
    tokens = m.split(':')
    code = tokens[0] #BR:안뇽 / AAA / TO:AAA:안뇽안뇽 / tokens[0]은 함수 이름임 

    if (code.upper() == "JOIN"):
            joinServer(cs,m)

    elif (code.upper()  == "SU"):        
            showUser(cs,m)

    elif (code.upper()  == "UN"):        
            unicastChat(cs,m)
        
    elif (code.upper()  == "BR"):
            broadcastChat(cs,m)
        
    elif (code.upper()  == "MMU"): #단톡방생성
            makeMulticastChat(cs,m)
    
    elif (code.upper()  == "SMU"): #자신이 포함된 단톡방 목록 조회
            showMulticastChatList(cs,m)

    elif (code.upper()  == "EMU"): #단톡방나가기
            exitMulticastChat(cs,m)
        
    elif (code.upper()  == "MU"): #단톡방채팅
            multicastChat(cs,m)
        
    elif (code.upper()  == "EXIT"):
            exitServer(cs,m)

        
def client_com(cs):
    # 클라이언트로부터 id 메시지를 받음
    while True:
        if event.is_set(): # event 발생하면 스레드 종료
            return
        try:  # 아래 문장 무조건 실행
            recieveMsg = cs.recv(BUFSIZE).decode()
            print('recieve data : ',recieveMsg)
        except Exception as e:  # 위 문장 에러 처리: client no longer connected
            print(f"에러가 발생 햇습니다다아앙sibal:{e}")
            clientSockets.pop(cs)
        else:  # recv 성공하면 메시지 처리
            if ( msg_proc(cs, recieveMsg) == False):
                break  # 클라이언트가 종료하면 루프 탈출 후 스레드 종료
        

def client_acpt():
    # 소켓 생성
    global serverSocket 
    serverSocket = socket(AF_INET, SOCK_STREAM) 

    # 소켓 주소 정보 할당
    serverSocket.bind(ADDR)

    # 연결 수신 대기 상태
    serverSocket.listen(10)
    print('대기')

    # 연결 수락
    while True:
        if event.is_set(): # event 발생하면 스레드 종료
            return
        clientSocket, addr_info = serverSocket.accept()
        print('연결 수락: client 정보 ', addr_info)
        tc = Thread(target = client_com, args=(clientSocket,))
        tc.daemon = True
        tc.start()
        

ta = Thread(target=client_acpt)
ta.daemon = True
ta.start()

msg = input()
if msg.upper() == "E":
    event.set()
# 소켓 종료

for socket in clientSockets.values():
    try:
        socket.shutdown()
        socket.close()
    except Exception as e:
        continue
    
serverSocket.close()
print('종료')