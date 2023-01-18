import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import copy

twitter_datas = pd.read_csv("twitter-42.csv")
twitter_datas.columns = ['Time', 'QPS']
perform_datas = pd.read_csv("perform.csv")

lambda_data_2048 = {
    'mobilenet_v2': 43.6,
    'inception_v3': 275.5,
    'resnet50' : 193,
    'vgg16': 466,
    'vgg19': 554,
}
lambda_price_2048 = 0.0000000333

display(perform_datas)

datas = twitter_datas
display(datas)

x = list(datas.get('Time').values)
y = list(datas.get('QPS').values)

print(datas['QPS'].sum())

y_min = 25
y_max = 55
plt.ylim(y_min,y_max)
plt.plot(x,y)
plt.show()


TARGET_LATENCY = 200 #ms
T = [1,2,3,5,10,30,60,180]

default = {}
for t in T:
    default[t] = 0

model = "resnet50"

df = perform_datas[perform_datas["models"].isin([model])]
inferentia_per_second = int(df['InferentiaPerform'].values[0] / 60)
lambda_per_second = int(df['LambdaPerform'].values[0] / 60)

print("inferentia_per_second:",inferentia_per_second)
print("lambda_per_second:",lambda_per_second)

PerformInferentia = copy.deepcopy(default)
for t in T:
    PerformInferentia[t] = inferentia_per_second * t

PerformLambda = copy.deepcopy(default)
for t in T:
    PerformLambda[t] = lambda_per_second * t

print("Perform_Inferentia:", PerformInferentia)
print("Perform_Lambda:", PerformLambda)

InferentiaInstances = 0
InferentiaJobs = 0
LambdaWorkers = 0

# Time Step 별 도착하는 Event 양 체크
def RequestMonitor(start_time):
    requests = copy.deepcopy(default)
    for t in T:
        # 현재 시간 부터 앞으로의 t 만큼 체크, 이벤트의 총합 계산
        requests[t] = twitter_datas[start_time:start_time + t]['QPS'].values.sum(axis=0)
    return requests

def Ququeing():
    # Ququeing 모델에 대한 함수 작성
    return True
start_time = 0
end_time = 59

instance_start_time = 0

while(start_time <= end_time):
    print("Current Time:", start_time)
    
    Events = RequestMonitor(start_time)
    print(Events)
    
    # 인스턴스 실행중인 경우
    EventValues = np.array(list(Events.values()))
    if InferentiaInstances > 0:
        InferentiaJobs += Events[1]
        EventValues -= np.array(list(PerformInferentia.values())) * InferentiaInstances
    
    print(EventValues)
    
    print("Lambda_Workers:",LambdaWorkers)
    print("InferentiaInstances:",InferentiaInstances, "Worked by Inferentia Job:", InferentiaJobs)    
    
    # 실행중인 인스턴스 제외하고 판단    
    PreferedLambda = np.array(list(PerformLambda.values())) > EventValues
    LambdaPreferRatio = len(PreferedLambda[PreferedLambda == True]) / len(PreferedLambda)
    print(LambdaPreferRatio)
    MDCQueue = []
    
    # 이벤트 값이 마이너스가 된다면 인스턴스 종료
    if len(EventValues[EventValues < 0]) > 0:
        InferentiaInstances -= 1
                 
    elif LambdaPreferRatio <= 0.5:
        # 인스턴스를 추가로 켜야하는 경우
        InferentiaInstances += 1
        # Inferentia Queue에 Event를 담기
        
        # M/D/C Ququeing Model 활용
    
    else:
        LambdaWorkers += Events[1]
    
    
    start_time += 1
    #if real simulation
    #time.sleep(1)
