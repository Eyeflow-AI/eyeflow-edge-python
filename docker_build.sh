docker build -t eyeflow.azurecr.io/eyeflow_edge:x86-tf2.2 .
az acr login --name eyeflow
docker push eyeflow.azurecr.io/eyeflow_edge:x86-tf2.2
