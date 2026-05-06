# Лабораторная работа №12: Kubernetes

**Студент:** Любимов Кирилл Алексеевич (s15)  
**Группа:** 331  
**Проект:** shipments-s15  
**Порт:** 8270  
**App:** shipments-app  
**Container:** shipments-container

## Описание

Создание Kubernetes манифестов для деплоя приложения: Deployment и Service.

## Реализация

### Deployment (k8s/deployment.yaml)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shipments-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: shipments-app
  template:
    spec:
      containers:
      - name: shipments-container
        image: shipments-s15:latest
        ports:
        - containerPort: 8270
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8270
        readinessProbe:
          httpGet:
            path: /health
            port: 8270
```

### Service (k8s/service.yaml)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: shipments-svc-s15
spec:
  type: ClusterIP
  selector:
    app: shipments-app
  ports:
  - protocol: TCP
    port: 8270
    targetPort: 8270
```

## Запуск

```bash
kubectl apply -f k8s/
```

## Проверка

```bash
cd ~/Code/Network-Software
STUDENT_ID=s15 GROUP=331 python -m pytest -q weeks/week-12/tests
```

Результат: Все тесты пройдены

## Ключевые концепции

**Deployment** — описание приложения и количество реплик  
**Service** — стабильный сетевой адрес для подов  
**Probes** — проверки здоровья (liveness, readiness)  
**Resources** — лимиты CPU и памяти  
**Replicas** — количество копий приложения
