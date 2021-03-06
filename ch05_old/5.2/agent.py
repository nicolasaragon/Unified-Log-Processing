#!/usr/bin/env python

import os, datetime, socket, json, uuid, time
from boto import kinesis

def get_filesystem_metrics(path):
  stats = os.statvfs(path)
  block_size = stats.f_frsize
  return (block_size * stats.f_blocks, # Filesystem size in bytes
    block_size * stats.f_bfree,        # Free bytes
    block_size * stats.f_bavail)       # Free bytes excluding reserved space

def get_agent_version():
  return "0.1.0"

def get_hostname():
  return socket.gethostname()

def get_event_time():
  return datetime.datetime.now().isoformat()

def get_event_id():
  return str(uuid.uuid4())

def create_event():
  size, free, avail = get_filesystem_metrics("/")
  event_id = get_event_id()
  return (event_id, {
    "id": event_id,
    "subject": {
      "agent": {
        "version": get_agent_version()
      }
    },
    "verb": "read",
    "direct_object": {
      "filesystem_metrics": {
        "size": size,
        "free": free,
        "available": avail
      }
    },
    "at": get_event_time(),
    "on": {
      "server": {
        "hostname": get_hostname()
      }
    }
  })

def write_event(conn, stream_name):
  event_id, event_payload = create_event()
  event_json = json.dumps(event_payload)
  conn.put_record(stream_name, event_json, event_id)
  return event_id

if __name__ == '__main__':                                        # a
  conn = kinesis.connect_to_region(region_name="us-east-1",
    profile_name="ulp")
  while True:                                                     # b
    event_id = write_event(conn, "events")
    print "Wrote event: {}".format(event_id)
    time.sleep(10)                                                # c
