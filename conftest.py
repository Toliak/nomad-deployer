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
        Name='^gitlab$',
        Type='^service$',
        TaskGroups=[dict(
            Name='^gitlab$',
            Tasks=[dict(
                Name='^gitlab$',
                Driver='^docker$',
                Config=dict(
                    network_mode='^custom-bridge$',
                    image='^gitlab/gitlab-ee',
                    network_aliases=['^gitlab$'],
                    port_map=[dict(ssh=22)],
                    volumes=['.+(gitlab|letsencrypt).+'],
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
def nomad_config_json():
    config = '''{
  "Stop": false,
  "Region": "global",
  "Namespace": "default",
  "ID": "gitlab",
  "ParentID": "",
  "Name": "gitlab",
  "Type": "service",
  "Priority": 85,
  "AllAtOnce": false,
  "Datacenters": [
    "dc1"
  ],
  "Constraints": null,
  "Affinities": null,
  "Spreads": null,
  "TaskGroups": [
    {
      "Name": "gitlab",
      "Count": 1,
      "Update": {
        "Stagger": 30000000000,
        "MaxParallel": 1,
        "HealthCheck": "checks",
        "MinHealthyTime": 10000000000,
        "HealthyDeadline": 300000000000,
        "ProgressDeadline": 600000000000,
        "AutoRevert": false,
        "AutoPromote": false,
        "Canary": 0
      },
      "Migrate": {
        "MaxParallel": 1,
        "HealthCheck": "checks",
        "MinHealthyTime": 10000000000,
        "HealthyDeadline": 300000000000
      },
      "Constraints": null,
      "Scaling": null,
      "RestartPolicy": {
        "Attempts": 2,
        "Interval": 1800000000000,
        "Delay": 15000000000,
        "Mode": "fail"
      },
      "Tasks": [
        {
          "Name": "gitlab",
          "Driver": "docker",
          "User": "",
          "Config": {
            "network_mode": "custom-bridge",
            "port_map": [
              {
                "ssh": 22
              }
            ],
            "volumes": [
              "/opt/gitlab/config:/etc/gitlab",
              "/var/log/gitlab:/var/log/gitlab",
              "/opt/gitlab/data:/var/opt/gitlab",
              "/opt/letsencrypt/data:/usr/share/letsencrypt:ro"
            ],
            "image": "gitlab/gitlab-ee:13.2.2-ee.0",
            "network_aliases": [
              "gitlab"
            ]
          },
          "Env": null,
          "Services": null,
          "Vault": null,
          "Templates": null,
          "Constraints": null,
          "Affinities": null,
          "Resources": {
            "CPU": 5000,
            "MemoryMB": 7144,
            "DiskMB": 0,
            "IOPS": 0,
            "Networks": [
              {
                "Mode": "",
                "Device": "",
                "CIDR": "",
                "IP": "",
                "MBits": 50,
                "DNS": null,
                "ReservedPorts": [
                  {
                    "Label": "ssh",
                    "Value": 9022,
                    "To": 0,
                    "HostNetwork": "default"
                  }
                ],
                "DynamicPorts": null
              }
            ],
            "Devices": null
          },
          "RestartPolicy": {
            "Attempts": 2,
            "Interval": 1800000000000,
            "Delay": 15000000000,
            "Mode": "fail"
          },
          "DispatchPayload": null,
          "Lifecycle": null,
          "Meta": null,
          "KillTimeout": 5000000000,
          "LogConfig": {
            "MaxFiles": 5,
            "MaxFileSizeMB": 40
          },
          "Artifacts": null,
          "Leader": false,
          "ShutdownDelay": 0,
          "VolumeMounts": null,
          "KillSignal": "",
          "Kind": "",
          "CSIPluginConfig": null
        }
      ],
      "EphemeralDisk": {
        "Sticky": true,
        "SizeMB": 500,
        "Migrate": true
      },
      "Meta": null,
      "ReschedulePolicy": {
        "Attempts": 0,
        "Interval": 0,
        "Delay": 30000000000,
        "DelayFunction": "exponential",
        "MaxDelay": 3600000000000,
        "Unlimited": true
      },
      "Affinities": null,
      "Spreads": null,
      "Networks": null,
      "Services": null,
      "Volumes": null,
      "ShutdownDelay": null,
      "StopAfterClientDisconnect": null
    }
  ],
  "Update": {
    "Stagger": 30000000000,
    "MaxParallel": 1,
    "HealthCheck": "",
    "MinHealthyTime": 0,
    "HealthyDeadline": 0,
    "ProgressDeadline": 0,
    "AutoRevert": false,
    "AutoPromote": false,
    "Canary": 0
  },
  "Multiregion": null,
  "Periodic": null,
  "ParameterizedJob": null,
  "Dispatched": false,
  "Payload": null,
  "Meta": null,
  "ConsulToken": "",
  "VaultToken": "",
  "Status": "running",
  "StatusDescription": "",
  "Stable": true,
  "Version": 60,
  "SubmitTime": 1596274877112575700,
  "CreateIndex": 3523,
  "ModifyIndex": 60702,
  "JobModifyIndex": 60691
}    
'''
    return json.loads(config)
