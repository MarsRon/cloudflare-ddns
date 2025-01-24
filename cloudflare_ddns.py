#!/usr/bin/env python3

# Python3 script to dynamically update Cloudflare DNS A records to current IP address
# https://github.com/MarsRon/cloudflare_ddns

# Libraries
import argparse, json, requests, re

# Arguments & --help setup 
parser = argparse.ArgumentParser("cloudflare_ddns.py")
parser.add_argument(
  "config",
  help="Optional configuration file path. Defaults to cloudflare_ddns_config.json",
  type=str,
  nargs="?",
  default="cloudflare_ddns_config.json"
)
args = parser.parse_args()

# Parse configuration file and set constants
try:
  with open(args.config, "r") as file:
    data = json.load(file)
    DNS_RECORDS = data["DNS_RECORDS"]
    CLOUDFLARE_ZONE_ID = data["CLOUDFLARE_ZONE_ID"]
    CLOUDFLARE_ZONE_API_TOKEN = data["CLOUDFLARE_ZONE_API_TOKEN"]
    DISCORD_WEBHOOK_URL = data["DISCORD_WEBHOOK_URL"]

    # HTTP requests Constants
    CLOUDFLARE_API_ENDPOINT = f"https://api.cloudflare.com/client/v4/zones/{CLOUDFLARE_ZONE_ID}/dns_records"
    CLOUDFLARE_API_HEADERS = {
      "Authorization": f"Bearer {CLOUDFLARE_ZONE_API_TOKEN}",
      "Content-Type": "application/json"
    }
except FileNotFoundError:
  print(f"DDNS Updater: Configuration file {args.config} not found")
  exit(1)
except (json.decoder.JSONDecodeError, KeyError) as e:
  print(f"DDNS Updater: Invalid configuration file {args.config}. Please refer to the documentation. {repr(e)}")
  exit(1)

# Functions
def get_external_ip() -> str:
  """Get external IP address from Cloudflare trace and Amazon"""
  ipv4_re = r"(?:(?:25[0-5]|(?:2[0-4]|1\d|[1-9]|)\d)\.?\b){4}"
  res = requests.get("https://cloudflare.com/cdn-cgi/trace", timeout=10)
  ip = None

  if res.status_code == 200:
    # https://stackoverflow.com/a/36760050/16259910
    re_match = re.search(f"^ip=({ipv4_re})$", res.text, re.MULTILINE)
    if re_match is not None:
      ip = re_match.group(1)

  if res.status_code != 200 or ip is None:
    # Cloudflare trace failed
    res = requests.get("https://checkip.amazonaws.com", timeout=10)
    if res.status_code == 200:
      ip = res.text

  if re.search(ipv4_re, ip) is None:
    raise ConnectionError(f"DDNS Updater: Cannot get external IPv4 address. The current IP address is {ip}")

  if ip is None:
    raise ConnectionError("DDNS Updater: Cannot get external IP address. Check the internet connection?")
  
  return ip

def get_dns_record_info(record: str) -> str:
  """Get the DNS record information from Cloudflare API"""
  res = requests.get(
    CLOUDFLARE_API_ENDPOINT,
    params={
      "type": "A",
      "name": record
    },
    headers=CLOUDFLARE_API_HEADERS,
    timeout=10
  )

  if res.status_code != 200:
    raise ConnectionError(f"DDNS Updater: Cannot get DNS record information of {record} from Cloudflare API: {res.text}")

  dns_record_info = res.json()["result"][0]
  return dns_record_info

def update_dns_record(dns_record_info: dict, new_ip: str):
  """Push new DNS record information to Cloudflare API"""
  dns_record_id = dns_record_info["id"]
  record = dns_record_info["name"]

  res = requests.patch(
    f"{CLOUDFLARE_API_ENDPOINT}/{dns_record_id}",
    headers=CLOUDFLARE_API_HEADERS,
    json={"content": new_ip},
    timeout=10
  )

  if res.status_code != 200:
    raise ConnectionError(f"DDNS Updater: Cannot update DNS record {record} to Cloudflare API: {res.text}")

def send_discord_webhook(message: str):
  """Send a Discord webhook"""
  if DISCORD_WEBHOOK_URL == "":
    return
  res = requests.post(
    DISCORD_WEBHOOK_URL,
    json={"content": message},
    timeout=10
  )
  if res.status_code != 204:
    raise ConnectionError(f"DDNS Updater: Cannot send Discord webhook: {res.text}")

# Main
try:
  current_ip = get_external_ip()
  for record in DNS_RECORDS:
    dns_record_info = get_dns_record_info(record)
    dns_record_ip = dns_record_info["content"]
    if current_ip == dns_record_ip:
      # DNS record is okay
      print(f"DDNS Updater: IP address of {record} is {dns_record_ip}, no changes needed")
      continue
    else:
      # DNS record and current IP address differ
      update_dns_record(dns_record_info, current_ip)
      message = f"DDNS Updater: Updated DNS record {record} from {dns_record_ip} to {current_ip}"
      print(message)
      send_discord_webhook(message)
except ConnectionError as error:
  message = str(error)
  print(message)
  send_discord_webhook(message)
