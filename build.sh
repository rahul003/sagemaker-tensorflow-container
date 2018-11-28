cd docker/1.12.0_cu9/
sudo docker build -t tf_s3:v1.12.0_1 --build-arg py_version=3 --build-arg framework_installable=tensorflow-1.12.0-cp36-cp36m-linux_x86_64.whl -f Dockerfile.gpu .
sudo docker tag tf_s3:v1.12.0_1 578276202366.dkr.ecr.us-east-1.amazonaws.com/tf_s3:v1.12.0_1
sudo $(aws ecr get-login --no-include-email --region us-east-1)
sudo docker push 578276202366.dkr.ecr.us-east-1.amazonaws.com/tf_s3:v1.12.0_1

