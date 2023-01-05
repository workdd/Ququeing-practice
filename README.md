## Ququeing 이론 정리
### M/M/c quque 

- 해당 큐에서 들어오는 요청량과 처리되는 요청량에 따라서 평균 도착률, 평균 처리율 등을 계산 가능
- 고객의 도착 시간 분포는 포아송 분포라고 가정
- 서버 시간 분포는 각 처리별로 다른 경우 M으로 표현, 같다고 가정하는 경우 D로 표현
- 서버수에 따라서 µ 값은 배로 늘어남 (서버 수 값이 2라면 2µ, i라면 iµ)
- 각각 λ 값의 평균과 µ 값의 평균에 따라서 큐에 쌓여있는 요청량이 달라지게됨 들어오는 요청량이 서비스 처리량 보다 많다면 큐가 점점 쌓이게 되며, 들어오는 요청량보다 서비스 처리량이 더 많다면 큐에 요청들이 쌓여있지 않고 빠르게 비워지는 경향을 보임



![Image](https://user-images.githubusercontent.com/28581495/210721890-a4d6d383-7477-4b3b-a107-c653b57e7cb1.png)



- 해당 큐를 통해 평균적인 요청량 수, 평균적인 총 waiting time과 큐 안에서만의 waiting time은 다음과 같이 계산
    


![Image](https://user-images.githubusercontent.com/28581495/210721922-c5730de3-5128-4ccc-ac64-55d64d1d2a6c.png)


    
- 서비스 요청이 들어오는 분포는 포아송 분포로 가정



![Image](https://user-images.githubusercontent.com/28581495/210721949-ec9e3886-65ee-4dff-951d-82012da289a6.png)



### SERF 논문에서의 사용

- M/M/c, M/D/c, M/*Minterf*/c*,*M/*Dinterf*/c 네가지 종류의 큐를 사용, 특히 서버처리 시간에 interference라는 cache 및 memory 경합으로 인한 요청간 간섭 시간을 포함하여 큐잉을 시도함
- 위의 waiting time을 구하는 공식을 interference 값을 포함하여 수식을 수정함
    


![Image](https://user-images.githubusercontent.com/28581495/210721985-c2b4c58b-0a47-46a1-bac2-3f7ebe1874e2.png)


    

### MARK 논문에서의 사용

- 추론 시간을 항상 동일하다고 가정하여 M/D/c 큐 모델을 사용
- 여러 인스턴스 종류를 사용하기 때문에 각 인스턴스당의 도착 비율의 합이 예상되는 전체 도착 비율보다 크도록 설정
- 인스턴스 당 도착한 요청에 대해서 같은 종류의 인스턴스 i가 여러개 auto scaling 될 수 있기 때문에 인스턴스 개수 만큼 나누어 계산에 반영, 전체 시스템에 걸리는 시간이 target latency보다 적도록 설정함



![Image](https://user-images.githubusercontent.com/28581495/210722013-5209a07c-9e84-4378-a431-84d3677a7376.png)

