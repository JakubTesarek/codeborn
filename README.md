# Development

## Build client docker image
`podman build -t localhost/codeborn-client:latest codeborn_client/`

## Generate migrations
```
aerich migrate --name <description>
aerich upgrade
```

# TODO
- Encrypt Github token