# Development

## Setup dev environment
```
uv env
uv sync
```

## Install npm dependencies
`npm --prefix frontend install`

## Edit vault file
`ansible-vault edit --vault-password-file ~/.ansible_vault_pass.txt .<app_mode>.secrets.yml`

## Build client docker image
`podman build -t localhost/codeborn-client:latest codeborn_client/`

## Generate migrations
```
aerich migrate --name <description>
aerich upgrade
```

## Run DB
`docker compose up`

## Run Api
`python -m codeborn.api`

## Run Frontend
`npm --prefix frontend run dev`


# Production

## Setup server
- Edit `infra/inventory.ini`: `91.107.225.178 ansible_user=root ansible_python_interpreter=/usr/bin/python3`
- Run: `ansible-playbook -i inventory.ini bootstrap.yml`
- Revert changes in `infra/inventory.ini`

## Setup app
`ansible-playbook -i inventory.ini setup.yml`