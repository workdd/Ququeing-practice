import numpy as np
import queue

# Interval Time , Service time 변수  
lamb=float(5) 
mu = float(3) 
Wait_time = 0

# 큐생성
queue = queue.Queue()

# 처음 작업이 들어오는 경우.
Fisrt_Arrival = np.random.exponential(lamb)
First_Service = np.random.exponential(mu) 

# 처음 작업 출력.
print("First_Arrival : ", Fisrt_Arrival)
print("First_Service : ", First_Service)
print("---------------------------------------------------")

# 변수 통일을 위해 저장.
Next_Arrival = Fisrt_Arrival
Next_Service = First_Service
count = 0

# 카운트 만큼 실행.
while count < 10:
    count+=1
    print("count : ", count)
    # 작업 끝나는 시간 저장.

    # 처음 작업이 진행 될때.
    if(count == 1):
        # 처음 도착 시간 + 서비스 시간
        queue.put(Fisrt_Arrival+First_Service)
    else:
        # 이전 종료시간 + 서비스 시간
        queue.put(Finish_time+Next_Service)

    # 기다리는 시간이 없을 경우 새로운 작업 종료시간 갱신.
    if(Wait_time == 0):
        New_Finish_time = Next_Arrival + Next_Service

    # 도착 시간 갱신.
    while Next_Arrival < Next_Service:
        Next_Arrival += np.random.exponential(lamb)

    # 작업 종료 시간 가져오기.
    Finish_time = queue.get()

    # 웨이팅이 없을 시 작업 종료 시간 변경.
    if(Wait_time == 0):
        Finish_time = New_Finish_time
    # wait 시간 계산.
    Wait_time = Finish_time - Next_Arrival
    print("Finsh : ", Finish_time)

    # 서비스 시간 갱신.
    if queue.empty():
        Next_Service = Next_Arrival + np.random.exponential(mu)
    else:
        Next_Service = Next_Service + np.random.exponential(mu)

    # 웨이트 시간 출력 및 시간..
    print("Next_Arrival : ", Next_Arrival)
    
    # 웨이트 시간 없을때의 예외처리.
    if(Wait_time < 0):
        print("Wait Time : 0")
        Wait_time = 0
    else:
        print("Wait Time : ", Wait_time)
        
    print("Next_Service : ", Next_Service)

    print("---------------------------------------------------")
