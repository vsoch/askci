---
title: Deployment - setting up https
description: How to configure https to work with your node
tags: 
 - https
 - lets-encrypt
---

# Generating Certificates

We will use [Let's Encrypt](https://letsencrypt.org/) to generate certificates for the server.
They expire about every 3 months, but the service asks for an email that will
send you a reminder to re-generate them. There are services that will handle this
for you, but I've never wanted to pay for them.

Specifically, we have provided [a script]({{ site.repo }}/blob/master/scripts/generate_cert.sh)
that can be used to generate the needed certificates. **It is recommended to look at the script
and run this manually to be careful of the steps**. But if you want, it takes an email and domain (without wwww)
as the first two arguments:

```bash
$ /bin/bash scripts/generate_cert.sh myemail@domain.com askci.dev
```

And it requires nginx to be installed on the host machine (done with the [prepare instance script]({{ site.repo }}/blob/master/scripts/prepare_instance.sh). I usually walk through the steps
manually to make sure that each works as expected, instead of running the entire thing with arguments.
To give you a preview of the content, after installing dependencies we use certbot to
get certificates (both for www and without):

```bash
# Get certificates (might need sudo)
certbot certonly --nginx -d "${DOMAIN}" -d "www.${DOMAIN}" --email "${EMAIL}" --agree-tos --redirect
```

And the prompt will continue interactively to ask for more details. When it finishes,
you should see that the generation was successful:

```bash
# Obtaining a new certificate
# Performing the following challenges:
# http-01 challenge for containers.page
# http-01 challenge for www.containers.page
# Waiting for verification...
# Cleaning up challenges

# IMPORTANT NOTES:
# - Congratulations! Your certificate and chain have been saved at:
#   /etc/letsencrypt/live/containers.page/fullchain.pem
#   Your key file has been saved at:
#   /etc/letsencrypt/live/containers.page/privkey.pem
#   Your cert will expire on 2019-09-04. To obtain a new or tweaked
#   version of this certificate in the future, simply run certbot
#   again. To non-interactively renew *all* of your certificates, run
#   "certbot renew"
# - Your account credentials have been saved in your Certbot
#   configuration directory at /etc/letsencrypt. You should make a
#   secure backup of this folder now. This configuration directory will
#   also contain certificates and private keys obtained by Certbot so
#   making regular backups of this folder is ideal.
# - If you like Certbot, please consider supporting our work by:

#   Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
#   Donating to EFF:                    https://eff.org/donate-le
```

We then copy files on the host into /etc/ssl (where the container expects them to
be) and create backups. Finally, we generate a dhparam.pem for extra security,
and stop nginx. The next step would be to ensure that your domain name has an A record for the
ip address, and then (for Google Cloud and similar) to create a networking interface
that uses the A record, along with CNAMEs, both using the nameservers specified by
the domain registrar. When you are finished, [return to the setup](setup).
