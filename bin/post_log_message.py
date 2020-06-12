#!/usr/bin/env python3
import argparse
import json
from os import getenv
import requests
import sys


def exit_verbosely(message, code=2):
    """Call with message to exit with details echoed to stderr"""
    print(message, file=sys.stderr)
    sys.exit(code)


def envvar(var_name):
    value = getenv(var_name)
    if not value:
        exit_verbosely(
            f"environment var `{var_name}` not defined; can't continue")
    return value


def validate_json(event, column_name):
    """Validate the given parameter is valid json and nest if necessary

    A cheap guard against attempted injections - exit if not valid JSON.
    The log server API requires the top level field is named to match
    a column in given table for insertion. Nest the given JSON unless
    already well formed.

    :returns: validated JSON including nesting under expected database
     column name if not already present.

    """
    try:
        data = json.loads(event)
    except ValueError as e:
        # couldn't parse, exit
        exit_verbosely("event is not valid JSON: {}\n".format(e))

    if column_name in data and len(data) == 1:
        return data
    return {column_name: data}


class BearerAuth(requests.auth.AuthBase):
    """requests auth and headers collide - extend for Bearer token"""
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


def post_event(event):
    """Transmit given event to logserver via POST

    NB: makes use of several os environment variables including:
    - LOGSERVER_JWT: a json web token with claims including necessary role
    - LOGSERVER_URI: fully qualified path to logserver for POST

    """

    jwt = envvar('LOGSERVER_JWT')
    uri = envvar('LOGSERVER_URI')
    response = requests.post(url=uri, auth=BearerAuth(jwt), json=event)
    response.raise_for_status()


usage = """Upload JSON event to log server via HTTP POST

  Environment variables required:
  - LOGSERVER_JWT: valid json web token with claims including necessary role
  - LOGSERVER_URI: fully qualified path to log server for POST """

parser = argparse.ArgumentParser(usage=usage)
parser.add_argument("event", help="JSON structured event to POST")
args = parser.parse_args()
event = validate_json(args.event, "event")
post_event(event)

