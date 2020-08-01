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
                    Policies=['NULL']
                )
            )]
        )]
    )

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
