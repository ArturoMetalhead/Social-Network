sudo docker build -f docker_server.dockerfile -t servidor .
sudo docker run -p 8000:8000 servidor