import os

os.system("docker stop prod_backup")
os.system("docker rm prod_backup")
os.system("docker rmi prod_backup:latest")
print("Done!")
