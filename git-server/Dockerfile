# TODO: GIT version must be specified! best solution - install from source
FROM ubuntu:latest

RUN apt update && apt install  openssh-server sudo -y
RUN useradd -rm -d /home/gituser -s /bin/bash -g root -G sudo -u 1000 gituser
RUN  echo 'gituser:gituser' | chpasswd
RUN service ssh start
EXPOSE 22

CMD ["/usr/sbin/sshd","-D"]
