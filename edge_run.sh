docker run \
    --env LANG=C.UTF-8 \
    --hostname Lenovo-Legion \
    --network host \
    --gpus all \
    --volume /opt/eyeflow/log:/opt/eyeflow/log \
    --volume /opt/eyeflow/src/edge.license:/opt/eyeflow/src/edge.license \
    --volume /opt/eyeflow/src/edge-key.pub:/opt/eyeflow/src/edge-key.pub \
    --name eyeflow_edge \
    --rm \
    --cpus=8 \
    --security-opt seccomp=unconfined \
    eyeflow.azurecr.io/eyeflow_edge:x86-tf2.2
