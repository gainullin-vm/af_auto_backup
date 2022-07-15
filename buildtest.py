import os

os.system("docker build -t prod_backup:latest .")
os.system("docker run -d --name prod_backup --restart=always prod_backup:latest")
print("Done!")
