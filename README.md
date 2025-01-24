# Cloudflare DDNS Python Script

Python3 script to dynamically update Cloudflare DNS A records to current IP address.

## Requirements

- Python3
- [`requests`](https://requests.readthedocs.io) Python package
- Cloudflare API token with Zone:DNS:Edit permissions
- DNS A record must be already exist (API token should only edit the DNS records)

### Creating Cloudflare API Token

To create a CloudFlare API token for your DNS zone go to https://dash.cloudflare.com/profile/api-tokens and follow these steps:

1. Click Create Token
2. Select Edit Zone DNS (Use template)
3. Provide the token a name, for example, `Cloudflare DDNS Script`
4. Grant the token the following permissions:
   - Zone - DNS - Edit
5. Optionally, set the zone resources to:
   - Include - Specific Zone - `example.com`
6. Complete the wizard and use the generated token at the [`CLOUDFLARE_ZONE_API_TOKEN`](#cloudflare_zone_api_token) configuration

## Usage

Clone the project

```shell
git clone git@github.com:MarsRon/cloudflare-ddns.git
cd cloudflare-ddns
```

Create and edit a configuration file. Refer to [Configuration](#Configuration) for more information.

```shell
cp cloudflare_ddns_config.example.json cloudflare_ddns_config.json
chmod 600 cloudflare_ddns_config.json # Protected file permission
nano cloudflare_ddns_config.json
```

Run the script

```shell
python3 cloudflare_ddns.py cloudflare_ddns_config.json
```

### System Install

After verifying that the script works, you may want to setup for root user usage.
The following commands will install the script in `/usr/local/bin`.

```shell
sudo chown root:root {cloudflare_ddns.py,cloudflare_ddns_config.json}
sudo mv {cloudflare_ddns.py,cloudflare_ddns_config.json} /usr/local/bin
```

Setup a cron job (preferably in 1 hour intervals).
[crontab.guru](https://crontab.guru) is a useful site for this.

```shell
0 * * * * python3 /usr/local/bin/cloudflare_ddns.py /usr/local/bin/cloudflare_ddns_config.json
```

## Configuration

The configuration file is in JSON format. An example configuration file is provided in [`cloudflare_ddns_config.example.json`](./cloudflare_ddns_config.example.json) (as seen below)

```json
{
  "DNS_RECORDS": ["example.com", "www.example.com"],
  "CLOUDFLARE_ZONE_ID": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "CLOUDFLARE_ZONE_API_TOKEN": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/000000000000000000/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

#### `DNS_RECORDS`

List of DNS A records to be updated.

#### `CLOUDFLARE_ZONE_ID`

Cloudflare Zone ID.
Can be found on the landing/overview page of your domain on Cloudflare Dashboard.

#### `CLOUDFLARE_ZONE_API_TOKEN`

Cloudflare Zone API Token.
Create one with Zone:DNS:Edit permissions from https://dash.cloudflare.com/profile/api-tokens.
You may specify the Zone Resources.

#### `DISCORD_WEBHOOK_URL`

Discord WebHook URL.
Optionally enable Discord notifications (only sent if DNS is updated / error occured).
Leave empty "" if you do not want notifications.

## Limitations

- Does not support IPv6

## References

- [fire1ce/DDNS-Cloudflare-Bash](https://github.com/fire1ce/DDNS-Cloudflare-Bash)

## License

[MIT License](./LICENSE.md)
