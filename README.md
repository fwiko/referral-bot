# Referral Management Bot

A referral System in the form of a Discord Bot built for the written in Python using the Discord.py framework.

Bot requires _'Manage Roles'_ Permission.

---

The bot token must be set within the `data/settings.json` file.
A number of other settings can also be changed within;

```json
{
  "bot": {
    "prefix": "!",
    "status": "online",
    "extensions": ["referrals", "events", "statistics"],
    "token": "NzY1NjY3Mjg0MTU2Njc4MjI0.X4YJOQ.d6K9orVfE2esy0GyGFTNKsQFHAw"
  },
  "embed": {
    "success_colour": 16568067,
    "error_colour": 16568067
  },
  "permissions": {
    "admin_roles": [699246036459192361],
    "verified_role": 804859662959640627,
    "reward_role": 766708026526269485
  }
}
```

---

All user data is stored within the `data/referral_data.json` file.
Here is an example of the stored data for a user;

```json
{
  "name": "Raff",
  "user_id": 264375928468013058,
  "referral_code": "6vtS4g",
  "points": 5,
  "referrals": [264375928468013058],
  "referred_by": 264375928466343058,
  "verified": true,
  "active": true
}
```

---

## Hosting with Docker

Build the Docker image

```console
docker build -t referral-system .
```

Creating and running the Docker container

```console
docker run -d -v "$PWD":/usr/src/app --name <name> referral-system:latest
```
