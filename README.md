## Config examples (and API docs)

#### *PUT* /config/

```json
{
    "jwks_url": "https://gitlab.com/-/jwks",
    "bound_issuer": "gitlab.com"
}
```

#### *GET* /role/

Returns list of roles

#### *GET* /role/{role-name}

Returns role data

#### *PUT* or *POST* /role/{role-name}

*Nomad claims validates via regexp*

```json
{
    "bound_claims": {
        "project_id": "77",
        "ref": "master"
    },
    "nomad_claims": {
        "Name": "^nomad-service$",
        "Type": "^service$",
        "TaskGroups": [
            {
                "Name": "^nomad-service$",
                "Tasks": [
                    {
                        "Name": "^nomad-service$",
                        "Driver": "^docker$",
                        "Config": {
                            "image": "^nomad-service",
                            "network_mode": "^custom-bridge$",
                            "network_aliases": [
                                "^nomad-service$"
                            ],
                            "port_map": [
                                {
                                    "http": 8080
                                }
                            ],
                            "volumes": [
                                "^NONE$"
                            ]
                        },
                        "Vault": {
                            "Policies": [
                                "^nomad-server$"
                            ]
                        }
                    }
                ]
            }
        ]
    }
}
```

#### *POST* /run/

```json
{
   "role":"{role-name}",
   "job_hcl":"{job-hcl}",
   "jwt":"${CI_JOB_JWT}"
}
```

## Ok some meme here 

![Meme](.misc/meme.jpg)