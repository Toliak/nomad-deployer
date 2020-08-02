import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy_aio import ASYNCIO_STRATEGY

from core import settings


@pytest.fixture
def db():
    return create_engine(settings.connection_uri, strategy=ASYNCIO_STRATEGY)


@pytest.fixture
async def prepare_db(db):
    async with db.connect() as conn:
        await conn.execute("DELETE FROM 'jwt_role'")
        await conn.execute("DELETE FROM 'jwt_config'")


@pytest.fixture
def nomad_validator():
    return dict(
        Name='^test-deployer$',
        Type='^service$',
        TaskGroups=[dict(
            Name='^test-deployer$',
            Tasks=[dict(
                Name='^test-deployer$',
                Driver='^docker$',
                Config=dict(
                    network_mode='^custom-bridge$',
                    image='^gitlab/gitlab-ee',
                    network_aliases=['^test-deployer$'],
                    port_map=[dict(ssh=22)],
                    volumes=['.+(test-deployer|letsencrypt).+'],
                ),
                Vault=dict(
                    Policies=['^NULL$']
                )
            )]
        )]
    )


@pytest.fixture
def ci_job_jwt():
    return """eyJhbGciOiJSUzI1NiIsImtpZCI6IkEzU2xjR3RIcjUwOHQ1WEEzQU5fV0wycjlZNHRkWG1wNHpBM3djUG44cE0iLCJ0eXAiOiJKV1QifQ.eyJuYW1lc3BhY2VfaWQiOiIyIiwibmFtZXNwYWNlX3BhdGgiOiJUb2xpYWsiLCJwcm9qZWN0X2lkIjoiNzYiLCJwcm9qZWN0X3BhdGgiOiJUb2xpYWsvZXNjYXBlX3RoZV9kb2NrZXIiLCJ1c2VyX2lkIjoiMiIsInVzZXJfbG9naW4iOiJUb2xpYWsiLCJ1c2VyX2VtYWlsIjoidG9saWFrcHVycGxlQGdtYWlsLmNvbSIsInBpcGVsaW5lX2lkIjoiMTgyOCIsImpvYl9pZCI6IjI3NTgiLCJyZWYiOiJzb21lLWJyYW5jaCIsInJlZl90eXBlIjoiYnJhbmNoIiwicmVmX3Byb3RlY3RlZCI6ImZhbHNlIiwianRpIjoiM2I5MDA0OTMtOTVhMy00Y2VkLTlhNzItMGMwMWJjMTVhYmVjIiwiaXNzIjoiZ2l0bGFiLnRvbGlhay5ydSIsImlhdCI6MTU5NjM3MjI4MSwibmJmIjoxNTk2MzcyMjc2LCJleHAiOjE1OTYzNzU4ODEsInN1YiI6ImpvYl8yNzU4In0.OHcQ9aDkIdINbX8m_LambvRqd5JEe0lzqZIHPf3bPQnd1fqS9Ety_iO1zPHVleQqHZZDj4chCYV48vO2sNty0GrRQE6bNDOztPMFevwoH255LLQYghSHJiYHXshUyGN3-jc2KoQBoWC7OPRs9Q4UEXiuM0d4Vz2CXLk92nW3VtFJHptcucS6BZGN6sDh8r2LBNh-psEKwfOBGlY6zaxgNEap8HmVrECu48YIeuo1D58S4hlzaCUMff91XEVJ2Nxf3dKBQQktDeIOJVTGEHvG4uWmqGAcLTq2oHQQWi_M2d1eLzb6QT0kSdV0cjP5e-WvPGAXkq4vncza8EuB3jiYk3CIQITGCydD1e-S5OH002oMj20jm59SY_nb6tNZ8pGn5ELZHFob7vHAEfmu4CRRWQWsqvDTJwpPGI6tMQMMztAgM2a7CLgWha5LQaYFnIG2kMD5pZAE1oG-2yC2cO2_3S3CaRdRWRJ7jBjcsWKpOY488yzSfkrhZvloWIOdk5gGYr7atQMWu-iYIf7EDnwBRKIw_I6XX2j1xQJEkRkzYAbhYtS71ZPxABUuC1oqM7PLau_alpP2uoXBm_e_txqKSFvqI5ABHe429GJnOjqgsAlnXP1KwA_-7q3MDW7isoXnFDZYqMLlpWsPN_gsVlFqhOJT9nEE-DYdEYjhMhcuJos"""


@pytest.fixture
def ci_job_jwt_body():
    return """{
  "namespace_id": "2",
  "namespace_path": "Toliak",
  "project_id": "76",
  "project_path": "Toliak/escape_the_docker",
  "user_id": "2",
  "user_login": "Toliak",
  "user_email": "xxxxxxxxxx@gmail.com",
  "pipeline_id": "1828",
  "job_id": "2758",
  "ref": "some-branch",
  "ref_type": "branch",
  "ref_protected": "false",
  "jti": "3b900493-95a3-4ced-9a72-0c01bc15abec",
  "iss": "gitlab.toliak.ru",
  "iat": 1596372281,
  "nbf": 1596372276,
  "exp": 1596375881,
  "sub": "job_2758"
}"""


@pytest.fixture
def jwks_response():
    return """{
    "keys": [
        {
            "kty": "RSA",
            "kid": "A3SlcGtHr508t5XA3AN_WL2r9Y4tdXmp4zA3wcPn8pM",
            "e": "AQAB",
            "n": "shlGup6OnIWlVblZvdIM4o_48jY_vURPJm8mO2xUaENVCIVn2hXc-iSQnsThSOg7l_Sxi-StMprUi0MnP0UpICwfliGLQG28nsG6UYXWWB7CjEAhL6uWmT6SuMqIP9FzNresTkLrt-5WxNuCuHoKE5fl_MjGy9ps9tAMLYF1Bc9tlwJb5zpvZ7-cKl3bU8lavMxjCh2DSruIsfoAiCUvaef2ZQazAVN_o2euqV9QgYSjZUYLst_ZMDj_VtrXMSug8B7Qf3ZTkcEtTKwBd0Iy5q2RJWFDuRjCxa6WDt8iFr10N8XcpdJ_o9I7-AJo70_5JIkO9xAaSi7w1WPP5CLBmMPOOUUC_yRSg7nDMEfBljDkByPJese5VmNLNe5kusv3KK8a5s1kf16NFfCPHbX92MCS2wiM6SITXmmw6pvsOPhR5mqWX0xAewHQhnMF5MiqLLlEDrcEuvGlFVsy3TszjcPTt8ifsfVBto_6PA1i_xdf2D-6bU_1b4xxplg0uaAoNWo1py04MjMPRcYNnipl0qhuVvZLyd6sTD9E-GZLB33JLdMCDI2Citg3vG0zGVYfntfrkWExWRsemeHjTTRGBw_GvpkPAPkJipRZ0m9gkHdavQbgvWq1O07xbLPfUVhvlZXyJKBcHmxnYExeMjL0ac1BLo2YAiype1yzgWlFSoU",
            "use": "sig",
            "alg": "RS256"
        }
    ]
}"""


@pytest.fixture
def nomad_hcl_job():
    return """job "test-deployer" {
  datacenters = ["dc1"]
  
  priority = 8

  group "test-deployer" {
    count = 1

    task "test-deployer" {
      driver = "docker"

      config {
        image = "gitlab/gitlab-ee:not-existing-image"

        network_mode = "custom-bridge"
        network_aliases = [
          "test-deployer",
        ]
      }

      resources {
        cpu = 100
        memory = 200
      }
    }
  
  restart {
    attempts = 0
    mode = "fail"
  }
  
  }
}
"""


@pytest.fixture
def nomad_config_json():
    config = '''{
    "Affinities": null,
    "AllAtOnce": null,
    "Constraints": null,
    "ConsulToken": null,
    "CreateIndex": null,
    "Datacenters": [
        "dc1"
    ],
    "Dispatched": false,
    "ID": "test-deployer",
    "JobModifyIndex": null,
    "Meta": null,
    "Migrate": null,
    "ModifyIndex": null,
    "Multiregion": null,
    "Name": "test-deployer",
    "Namespace": null,
    "NomadTokenID": null,
    "ParameterizedJob": null,
    "ParentID": null,
    "Payload": null,
    "Periodic": null,
    "Priority": 8,
    "Region": null,
    "Reschedule": null,
    "Spreads": null,
    "Stable": null,
    "Status": null,
    "StatusDescription": null,
    "Stop": null,
    "SubmitTime": null,
    "TaskGroups": [
        {
            "Affinities": null,
            "Constraints": null,
            "Count": 1,
            "EphemeralDisk": null,
            "Meta": null,
            "Migrate": null,
            "Name": "test-deployer",
            "Networks": null,
            "ReschedulePolicy": null,
            "RestartPolicy": {
                "Attempts": 0,
                "Delay": null,
                "Interval": null,
                "Mode": "fail"
            },
            "Scaling": null,
            "Services": null,
            "ShutdownDelay": null,
            "Spreads": null,
            "StopAfterClientDisconnect": null,
            "Tasks": [
                {
                    "Affinities": null,
                    "Artifacts": null,
                    "Config": {
                        "network_aliases": [
                            "test-deployer"
                        ],
                        "image": "gitlab/gitlab-ee:not-existing-image",
                        "network_mode": "custom-bridge"
                    },
                    "Constraints": null,
                    "DispatchPayload": null,
                    "Driver": "docker",
                    "Env": null,
                    "KillSignal": "",
                    "KillTimeout": null,
                    "Kind": "",
                    "Leader": false,
                    "Lifecycle": null,
                    "LogConfig": null,
                    "Meta": null,
                    "Name": "test-deployer",
                    "Resources": {
                        "CPU": 100,
                        "Devices": null,
                        "DiskMB": null,
                        "IOPS": null,
                        "MemoryMB": 200,
                        "Networks": null
                    },
                    "RestartPolicy": null,
                    "Services": null,
                    "ShutdownDelay": 0,
                    "Templates": null,
                    "User": "",
                    "Vault": null,
                    "VolumeMounts": null
                }
            ],
            "Update": null,
            "Volumes": null
        }
    ],
    "Type": null,
    "Update": null,
    "VaultToken": null,
    "Version": null
}'''
    return json.loads(config)
