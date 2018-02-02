sudo service mysqld start
cd /home/ec2-user/data-process/
screen -S portal -d -m python /home/ec2-user/data-process/portal.py 8888 &> /home/ec2-user/data-process/web.log
screen -S min -d -m python /home/ec2-user/data-process/real_time_data_collector.py
