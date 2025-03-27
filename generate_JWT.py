import base64
import jwt
import yaml
import subprocess
import sys

try:
    # capture output from docker-compose config
    result = subprocess.run(
        ["docker-compose", "config"],
        capture_output=True,
        text=True,
        check=True,
    )
    config = yaml.safe_load(result.stdout)
except subprocess.CalledProcessError as e:
    print("Error calling `docker-compose config`:", e)
    sys.exit(1)

try:
    secret = config['services']['postgrest']['environment']['PGRST_JWT_SECRET']
except KeyError:
    print("Error, PGRST_JWT_SECRET not defined")
    sys.exit(1)

payload = {"role": "event_logger"}
token = jwt.encode(payload, secret, algorithm="HS256")

# echo JWT
print(token)

