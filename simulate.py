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

class Queue(object):
    """
    Create the initial object queue
    """

    def __init__(self, env, servers, servicetime):
        self.env = env
        self.server = simpy.Resource(env, servers)
        self.servicetime = servicetime

    def service(self, customer):
        """The process"""
        yield self.env.timeout(1/MU)

def customer(env, name, qu):
    """Each customer has a ``name`` and requests a server
    Subsequently, it starts a process.
    need to do sthis differently though...
    """

    global arrivals

    a = env.now
    # print(f'{name} arrives at the servicedesk at {a:.2f}')
    arrivals += 1

    with qu.server.request() as request:
        yield request

        global counter
        global waiting_time
        global leavers

        b = env.now
        # print('%s enters the servicedesk at %.2f.' % (name, b))
        waitingtime = (b - a)
        # print(f'{name} waiting time was {waitingtime:.2f}')
        waiting_time += waitingtime
        counter += 1

        yield env.process(qu.service(name))
        # print('%s leaves the servicedesk at %.2f.' % (name, env.now))
        leavers += 1
        
        
def setup(env, servers, servicetime, t_inter):
    """Create a queue, a number of initial customers and keep creating customers
    approx. every 1/lambda*60 minutes."""
    # Generate queue
    queue = Queue(env, SERVERS, MU)

    # Create 1 initial customer
    # for i in range(1):
    i = 0
    env.process(customer(env, f'Customer {i}', queue))

    # Create more customers while the simulation is running
    while True:
        yield env.timeout(np.random.exponential(1/LAMBDA, 1)[0])
        i += 1
        env.process(customer(env, f'Customer {i}', queue))

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
SIMULATIONS = 10

while(start_time <= end_time):
    print("Current Time:", start_time)
    
    Events = RequestMonitor(start_time)
    print(Events)

    TotalEventValues = np.array(list(Events.values()))
    ComparedEventValues = np.array(list(Events.values()))
    
    # 인스턴스 실행중인 경우
    if InferentiaInstances > 0:
        ### SETTINGS
        # Set RHO to a little bit smaller then 1; makes the simulation interesting
        # RHO = 서버 활용도
        # MU > LAMBDA, if  mu = 1 and c is 1 otherwise no queue.
        # 1/MU > 1/LAMBDA if c=2 or higher?
        # If mu = 2, avg is every 0.5 time step is the time costs of a service.
        # suppose lambda < 1
        InferentiaJobs += Events[1]
        ComparedEventValues -= np.array(list(PerformInferentia.values())) * InferentiaInstances
        
        print('Servers:', InferentiaInstances)
        # SIM_TIME: simulation time in time units
        time_idx =0 
        for TimeKey, SIM_TIME in PerformInferentia.items():
            MU = SIM_TIME # 1/mu is exponential service times
            
            SERVERS = InferentiaInstances
            LAMBDA = TotalEventValues[time_idx]
            RHO = LAMBDA / (MU * SERVERS)
            
            print("SIM_TIME:",SIM_TIME)
            print("EXPECTED VALUES AND PROBABILITIES")

            print(f'Rho: {RHO}\nMu: {MU}\nLambda: {LAMBDA}\nExpected interarrival time: {1 / LAMBDA:.5f} time units')
            print(f'Expected processing time per server: {1 / MU:.5f} time units\n')
            print(f'Probability that a job has to wait: {pwait(SERVERS, RHO):.5f}')
            print(f'Expected waiting time E(W): {expw(MU, SERVERS, RHO):.5f} time units')
            print(f'Expected queue length E(Lq): {expquel(SERVERS, RHO):.5f} customers\n')
            time_idx +=1
            
            E = expw(MU, SERVERS, RHO)
            if E > TARGET_LATENCY / 1000:
                print("Violate Target Latency")
    print("Lambda_Workers:",LambdaWorkers)
    print("InferentiaInstances:",InferentiaInstances, "Worked by Inferentia Job:", InferentiaJobs)    
    
    # 실행중인 인스턴스 제외하고 판단    
    RemainPreferedLambda = np.array(list(PerformLambda.values())) > ComparedEventValues
    RemainLambdaRatio = len(RemainPreferedLambda[RemainPreferedLambda == True]) / len(RemainPreferedLambda)
    print("RemainLambdaRatio:",RemainLambdaRatio)

    TotalPreferedLambda = np.array(list(PerformLambda.values())) > TotalEventValues
    TotalLambdaRatio = len(TotalPreferedLambda[TotalPreferedLambda == True]) / len(TotalPreferedLambda)
    print("TotalLambdaRatio:",TotalLambdaRatio)
    
                 
    if RemainLambdaRatio <= 0.5:
        # 인스턴스를 추가로 켜야하는 경우
        InferentiaInstances += 1
    
    # 더이상 인스턴스가 필요없는 경우
    if TotalLambdaRatio > 0.5:
        InferentiaInstance -= 1
    else:
        LambdaWorkers += Events[1]
    
    
    start_time += 1
    #if real simulation
    #time.sleep(1)
