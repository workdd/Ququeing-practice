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
T = [1,5,10,30,60,180]

default = {}
for t in T:
    default[t] = 0

model = "vgg16"

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

Instance_Cold_Start = 10
EVENT_TESTING = 5

WorkedByLambda = []
WorkedByInferentia = []

# Time Step 별 도착하는 Event 양 체크
def RequestMonitor(start_time):
    requests = copy.deepcopy(default)
    for t in T:
        # 현재 시간 부터 앞으로의 t 만큼 체크, 이벤트의 총합 계산
        requests[t] = twitter_datas[start_time:start_time + t]['QPS'].values.sum(axis=0) * EVENT_TESTING
    return requests

start_time = 0
end_time = 59

instance_start_time = 0
SIMULATIONS = 10

while(start_time <= end_time):
    print("Current Time:", start_time)
    
    Events = RequestMonitor(start_time)
    print(Events)

    ComparedEventValues = TotalEventValues = np.array(list(Events.values()))
    
    CurrentLambdaJobs = 0
    CurrentInferentiaJobs = 0

    ### SETTINGS
    # Set RHO to a little bit smaller then 1; makes the simulation interesting
    # RHO = 서버 활용도
    # MU > LAMBDA, if  mu = 1 and c is 1 otherwise no queue.
    # 1/MU > 1/LAMBDA if c=2 or higher?
    # If mu = 2, avg is every 0.5 time step is the time costs of a service.
    # suppose lambda < 1
    
    NeedInstances = 0
    while True:
        RemainEvents = TotalEventValues - np.array(list(PerformInferentia.values())) * (NeedInstances + 1)
        EventRatio = len(RemainEvents[RemainEvents > 0]) / len(RemainEvents)
        if EventRatio < 0.5:
            break
        else:
            NeedInstances +=1
            
#     InferentiaInstances = list(np.array(list(PerformInferentia.values())) // TotalEventValues)
#     InferentiaInstances = Counter(NeedInstances)
#     InferentiaInstances = NeedInstances.most_common(n=1)[0][0]
    print(NeedInstances)
    InferentiaInstances = NeedInstances
    
    RemainEvents = np.array(list(PerformInferentia.values())) % TotalEventValues
        
    PreferedLambda = np.array(list(PerformLambda.values())) > RemainEvents
    LambdaRatio = len(PreferedLambda[PreferedLambda == True]) / len(PreferedLambda)
    print("LambdaRatio:", LambdaRatio)
    
    LambdaUsed = False
    if LambdaRatio <= 0.5:
        NeedInstances +=1
    else:
        LambdaUsed = True
        

    CurrentInferentiaJobs = Events[1]
    InferentiaInstances = NeedInstances
    
    if InferentiaInstances > 0:
#         print('Servers:', InferentiaInstances)
        # SIM_TIME: simulation time in time units
        time_idx =0 
        for TimeKey, SIM_TIME in PerformInferentia.items():
            
#             print(SIM_TIME)
#             print(TimeKey)
#             print(1/MU)
            SERVERS = InferentiaInstances
            MU = SIM_TIME / TimeKey # 1/mu is exponential service times
            LAMBDA = TotalEventValues[time_idx] / TimeKey
            RHO = LAMBDA / (MU * SERVERS)
            
#             print("RHO:",RHO)
#             print(expw(MU, SERVERS, RHO) / 2)
            W = expw(MU, SERVERS, RHO) / 2 + 1/MU
#             print("SIM_TIME:",SIM_TIME)
#             print("EXPECTED VALUES AND PROBABILITIES")

#             print(f'Rho: {RHO}\nMu: {MU}\nLambda: {LAMBDA}\nExpected interarrival time: {1 / LAMBDA:.5f} time units')
#             print(f'Expected processing time per server: {1 / MU:.5f} time units\n')
#             print(f'Probability that a job has to wait: {pwait(SERVERS, RHO):.5f}')
#             print(f'Expected queue length E(Lq): {expquel(SERVERS, RHO):.5f} customers\n')
#             print(f'Expected waiting time E(W): {W:.5f} time units\n')
#             E = expw(MU, SERVERS, RHO)
            
            time_idx +=1
            
            if W > TARGET_LATENCY / 1000:
                LambdaUsed = True
                CurrentLambdaJobs += int(TotalEventValues[0] / 2)
                print("W:", W, "Violate Target Latency")

    if LambdaUsed:
        CurrentLambdaJobs += RemainEvents[0]
        LambdaWorkers += CurrentLambdaJobs
    
    CurrentInferentiaJobs = Events[1] - CurrentLambdaJobs
    InferentiaJobs += CurrentInferentiaJobs
    
    WorkedByLambda.append(CurrentLambdaJobs)
    WorkedByInferentia.append(CurrentInferentiaJobs)
    
    print("Lambda_Workers:",LambdaWorkers)
    print("InferentiaInstances:",InferentiaInstances, "Worked by Inferentia Job:", InferentiaJobs)    
    
    start_time += 1
    #if real simulation
    #time.sleep(1)
