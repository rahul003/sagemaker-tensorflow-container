sudo groupadd docker
sudo gpasswd -a ubuntu docker
#logout login
sudo docker run hello-world
sudo chown -R $USER ~/.docker
