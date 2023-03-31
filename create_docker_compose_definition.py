import sys

if len(sys.argv) < 2:
	print("Ingrese el numero de clientes a generar")
	exit()

n_clients = int(sys.argv[1])

compose = "" + \
"version: '3.9'\n" + \
"name: tp0\n" + \
"services:\n" + \
"  server:\n" + \
"    container_name: server\n" + \
"    image: server:latest\n" + \
"    entrypoint: python3 /main.py\n" + \
"    environment:\n" + \
"      - PYTHONUNBUFFERED=1\n" + \
"      - LOGGING_LEVEL=DEBUG\n" + \
"    networks:\n" + \
"      - testing_net\n"

for i in range(1, n_clients + 1):
	compose += "\n" + \
	"  client{}:\n".format(i) + \
	"    container_name: client{}\n".format(i) + \
	"    image: client:latest\n" + \
	"    entrypoint: /client\n" + \
	"    environment:\n" + \
	"      - CLI_ID={}\n".format(i) + \
	"      - CLI_LOG_LEVEL=DEBUG\n" + \
	"    networks:\n" + \
	"      - testing_net\n" + \
	"    depends_on:\n" + \
	"      - server\n" + \
	"    volumes:\n" + \
	"      - ./client/.data:/data\n"

compose += "\n" + \
"networks:\n" + \
"  testing_net:\n" + \
"    ipam:\n" + \
"      driver: default\n" + \
"      config:\n" + \
"        - subnet: 172.25.125.0/24\n"

compose += "\n" + \
"volumes:\n" + \
"  client:\n"

with open('docker-compose-dev.yaml', 'w') as f:
	f.write(compose)