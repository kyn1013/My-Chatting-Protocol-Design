import socket
from threading import Thread
from datetime import datetime
import emoji #이모티콘 사용 라이브러리
from emoji_module import *

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5007
BUF_SIZE = 1024
SEP = ":"

#전송이 실패한 경우의 카운트
BRFcount = 0 
UNFcount = 0
MUFcount = 0
MUCFcount = 0
OUTFcount = 0

def listen_for_messages():
    while True:
        try:
            message = s.recv(BUF_SIZE).decode()
            print("\n" + message)
        except Exception as e:
            print(f"Error어어이이잉:{e}")

#실패 카운트 초기화 함수, 전송이 성공한 경우는 실패 카운트를 초기화함
def reset_fail_count():
    global BRFcount
    global UNFcount
    global MUFcount
    global MUCFcount
    global OUTFcount
    BRFcount = 0 
    UNFcount = 0 
    MUFcount = 0
    MUCFcount = 0
    OUTFcount = 0

def showCommand():
    command ="""
<명령어>
su  (채팅방에 접속중인 사람들 조회)
br:메시지  (전체 메시지 전송)
un:상대방:메시지   (1대1 메시지 전송)
mmu:채팅방이름:초대할 사람1/초대할 사람2 ...  (단체 채팅방 생성)
mu:채팅방이름:메시지  (단체 채팅방 메시지 전송)
smu  (참여중인 채팅방 목록 조회)
emu  (단체 채팅방 나가기)
show  (명령어리스트 조회)
emoji  (이모티콘 리스트 조회)
e  (서버 나가기)

"""
    print(command)
    return True

def showEmoji():
    command = emoji.emojize( 
    """
<이모티콘 리스트>
/사랑 /박수 /엥 /ㅎㅎ/짜증 /굿 /안녕 /ㅋㅋ /공부 /바보 /황당 /짱 /일등 /이등 /삼등 /산타 

-> 메시지 안에 넣어서 사용하면 됩니다 ex) 사랑/안해! -> :beating_heart:안해!
""")
    print(command)
    return True

# TCP 소켓 초기화
s = socket.socket()
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
# 서버에 연결
s.connect((SERVER_HOST, SERVER_PORT))
print("[+] Connected.")

t = Thread(target=listen_for_messages)
t.daemon = True
t.start()

# 서버에 내 ID를 등록
current_date = datetime.now()
print(f"{current_date.year}년{current_date.month}월{current_date.day}일") #서버에 처음 접속할때 날짜 알려주기
myID = input("Enter your ID: ")

# 이모티콘 기능 활성화 묻기
replace_emoji = True
replace_emoji_active = input("이모티콘 키워드 대체 기능을 사용하시겠습니까?(y/n): ")

if replace_emoji_active.upper() == 'N':
    replace_emoji = False
elif replace_emoji_active.upper() == 'Y':
    replace_emoji = True

current_datetime = datetime.now()
time = f"{current_datetime.hour}시 {current_datetime.minute}분"

to_Msg = "JOIN" + SEP + myID + SEP + time
s.send(to_Msg.encode())
showCommand()

while True:
    msg =  input()
    tokens = msg.split(SEP)
    method = tokens[0]

    if method.upper() == 'E':
        current_datetime = datetime.now()
        time = f"{current_datetime.hour}시 {current_datetime.minute}분"

        to_Msg = "EXIT" + SEP + myID + SEP + time
        s.send(to_Msg.encode())
        break

    elif method.upper() == "SHOW":
        showCommand()

    elif method.upper() == "EMOJI":
        showEmoji()

    elif method.upper() == "SU":
        current_datetime = datetime.now()
        time = f"{current_datetime.hour}시 {current_datetime.minute}분"

        to_Msg = method + SEP + myID + SEP + time
        s.send(to_Msg.encode())

    elif method.upper()  == "BR" :
        try:

            msg = tokens[1]

            current_datetime = datetime.now()

            #이모티콘 기능을 켠 경우만 실행되도록 함
            if replace_emoji:
                msg = replace_emoji_to_message(msg)

            #항상 실행
            msg = add_emoji_to_message(msg)

            time = f"{current_datetime.hour}시 {current_datetime.minute}분"
            err = "no err"
            icon = emoji.emojize(':loudspeaker:')
            
            # 성공할 경우 실패 카운트 초기화
            reset_fail_count()

            to_Msg = method + SEP + myID + SEP + str(BRFcount) + SEP + str(err) + SEP + time + SEP + msg + SEP + icon
            s.send(to_Msg.encode())

        except IndexError as e:
            print(f"명령어 입력 형식이 맞지 않아 전송에 실패했습니다.")

            BRFcount += 1
            err = e
            current_datetime = datetime.now()
            time = f"{current_datetime.hour}시 {current_datetime.minute}분"

            to_Msg = method + SEP + myID + SEP + str(BRFcount) + SEP + str(err) + SEP + time
            s.send(to_Msg.encode())

        except Exception as e:
            print(f"에러가 발생했습니다. 발생사유:{e}")

            BRFcount += 1
            err = e
            current_datetime = datetime.now()
            time = f"{current_datetime.hour}시 {current_datetime.minute}분"

            to_Msg = method + SEP + myID + SEP + str(BRFcount) + SEP + str(err) + SEP + time
            s.send(to_Msg.encode())

    elif method.upper() == "UN":
        try:
            toID = tokens[1]
            msg = tokens[2]
            
            current_datetime = datetime.now()

            #이모티콘 기능을 켠 경우만 실행되도록 함
            if replace_emoji:
                msg = replace_emoji_to_message(msg)

            #항상 실행
            msg = add_emoji_to_message(msg)

            time = f"{current_datetime.hour}시 {current_datetime.minute}분"
            err = "no err"
            
            # 성공할 경우 실패 카운트 초기화
            reset_fail_count()

            #un:z:xx
            to_Msg = method + SEP + myID + SEP + str(UNFcount) + SEP + str(err) + SEP + time + SEP + toID +SEP + msg
            s.send(to_Msg.encode())
        
        except IndexError as e:
            print(f"명령어 입력 형식이 맞지 않아 전송에 실패했습니다.")

            UNFcount += 1
            err = e
            current_datetime = datetime.now()
            time = f"{current_datetime.hour}시 {current_datetime.minute}분"

            to_Msg = method + SEP + myID + SEP + str(UNFcount) + SEP + str(err) + SEP + time
            s.send(to_Msg.encode())

        except Exception as e:
            print(f"에러가 발생했습니다. 발생사유:{e}")

            UNFcount += 1
            err = e
            current_datetime = datetime.now()
            time = f"{current_datetime.hour}시 {current_datetime.minute}분"

            to_Msg = method + SEP + myID + SEP + str(UNFcount) + SEP + str(err) + SEP + time
            s.send(to_Msg.encode())
    
    elif method.upper() == "MMU":
        try:
            roomID = tokens[1]
            joinUsers = tokens[2]

            current_datetime = datetime.now()

            time = f"{current_datetime.hour}시 {current_datetime.minute}분"
            err = "no err"
            
            # 성공할 경우 실패 카운트 초기화
            reset_fail_count()

            #mu:num1:a:b
            to_Msg = method + SEP + myID + SEP + str(MUFcount) + SEP + str(err) + SEP + time + SEP + roomID + SEP + joinUsers
            s.send(to_Msg.encode())

        except IndexError as e:
            print(f"명령어 입력 형식이 맞지 않아 전송에 실패했습니다.")

            MUFcount += 1
            err = e
            current_datetime = datetime.now()
            time = f"{current_datetime.hour}시 {current_datetime.minute}분"

            to_Msg = method + SEP + myID + SEP + str(MUFcount) + SEP + str(err) + SEP + time
            s.send(to_Msg.encode())

        except Exception as e:
            print(f"에러가 발생했습니다. 발생사유:{e}")

            MUFcount += 1
            err = e
            current_datetime = datetime.now()
            time = f"{current_datetime.hour}시 {current_datetime.minute}분"

            to_Msg = method + SEP + myID + SEP + str(MUFcount) + SEP + str(err) + SEP + time
            s.send(to_Msg.encode())


    elif method.upper() == "SMU": #단톡방목록조회
        current_datetime = datetime.now()
        time = f"{current_datetime.hour}시 {current_datetime.minute}분"

        to_Msg = method + SEP + myID + SEP + time
        s.send(to_Msg.encode())

    elif method.upper() == "EMU": #단톡방나가기 out:qq
        try:
            roomID = tokens[1]

            current_datetime = datetime.now()

            time = f"{current_datetime.hour}시 {current_datetime.minute}분"
            err = "no err"
            
            # 성공할 경우 실패 카운트 초기화
            reset_fail_count()

            #mu:num1:a:b
            to_Msg = method + SEP + myID + SEP + str(OUTFcount) + SEP + str(err) + SEP + time + SEP + roomID
            s.send(to_Msg.encode())

        except IndexError as e:
            print(f"명령어 입력 형식이 맞지 않아 전송에 실패했습니다.")

            OUTFcount += 1
            err = e
            current_datetime = datetime.now()
            time = f"{current_datetime.hour}시 {current_datetime.minute}분"

            to_Msg = method + SEP + myID + SEP + str(OUTFcount) + SEP + str(err) + SEP + time
            s.send(to_Msg.encode())

        except Exception as e:
            print(f"에러가 발생했습니다. 발생사유:{e}")

            OUTFcount += 1
            err = e
            current_datetime = datetime.now()
            time = f"{current_datetime.hour}시 {current_datetime.minute}분"

            to_Msg = method + SEP + myID + SEP + str(OUTFcount) + SEP + str(err) + SEP + time
            s.send(to_Msg.encode())
    
    elif method.upper() == "MU":
        try:
            roomID = tokens[1]
            msg = tokens[2]
            
            current_datetime = datetime.now()

            #이모티콘 기능을 켠 경우만 실행되도록 함
            if replace_emoji:
                msg = replace_emoji_to_message(msg)

            #항상 실행
            msg = add_emoji_to_message(msg)

            time = f"{current_datetime.hour}시 {current_datetime.minute}분"
            err = "no err"
            
            #성공할 경우 실패 카운트 초기화
            reset_fail_count()

            #mu:num1:안뇽
            to_Msg = method + SEP + myID + SEP + str(MUCFcount) + SEP + str(err) + SEP + time + SEP + roomID + SEP + msg

            s.send(to_Msg.encode())

            reset_fail_count() # 실패 카운트 초기화
        except IndexError as e:
            print(f"명령어 입력 형식이 맞지 않아 전송에 실패했습니다.")

            MUCFcount += 1
            err = e
            current_datetime = datetime.now()
            time = f"{current_datetime.hour}시 {current_datetime.minute}분"

            to_Msg = method + SEP + myID + SEP + str(MUCFcount) + SEP + str(err) + SEP + time
            s.send(to_Msg.encode())

        except Exception as e:
            print(f"에러가 발생했습니다. 발생사유:{e}")

            MUCFcount += 1
            err = e
            current_datetime = datetime.now()
            time = f"{current_datetime.hour}시 {current_datetime.minute}분"

            to_Msg = method + SEP + myID + SEP + str(MUCFcount) + SEP + str(err) + SEP + time
            s.send(to_Msg.encode())

    else:
        print(f"적절한 문장형식을 입력해주세요") #메서드 중에서 없는 문장 입력하면 발생 / re치면 나옴
        continue
    to_Msg = ''  # 초기화

# 소켓을 닫습니다
s.close()