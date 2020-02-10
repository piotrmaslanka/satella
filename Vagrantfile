# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "debian/contrib-jessie64"

  # Rabbit MQ management
  config.vm.network "forwarded_port", guest: 15672, host: 15672

  # HTTP for viewing coverage reports
  config.vm.network "forwarded_port", guest: 80, host: 8765

  config.vm.provision "shell", inline: <<-SHELL
     apt-get update

     # Python
     apt-get install -y htop curl build-essential python3 python3-pip python3-setuptools
     pip3 install --upgrade pip setuptools

     # Install deps
     pip3 install -r /vagrant/requirements.txt
     pip3 install nose2 mock coverage nose2[coverage_plugin] requests
     pip3 install pyyaml toml

     # HTTP server for viewing coverage reports
    apt-get -y install nginx
    rm -rf /var/www/html
    ln -s /vagrant/htmlcov /var/www/html

    # .bashrc for default user
    echo """# .bashrc
    cd /vagrant""" > /home/vagrant/.bashrc

  SHELL

end
