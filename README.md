[![Requirements Status](https://requires.io/github/maxim-mityutko/slack-bot/requirements.svg?branch=master)](https://requires.io/github/maxim-mityutko/slack-bot/requirements/?branch=master)
# Slack Extendable Bot (S.E.B)

The goal of this project is to create a flexible bot for Slack that can be integrated with various services via the API.
Extensibility of the solution is achieved by metadata driven plugins of two types: __connector__ and __payload__.

__Connector__ file has all the required data to pass the OAuth2 authentication (both 2-leg or 3-leg is supported) through
the OAuth wrapper class. The connectivity options can be added by also importing 3rd party modules that provide
custom authentication wrappers for the required services. One connector can be used by multiple payloads.

__Payload__ file specifies the service API interaction steps, which in the simplest scenario just calling the specific
API and retrieving the value, but can also be extended with custom functions. The response of the payload scenario is
wrapped in a JSON compatible with Slack API. 

Bot itself is headless but to facilitate the authentication process the simple Flask app is implemented. Both can and 
should be deployed in a separate containers.  

## Project Structure
```
    .
    ├── aws                 # AWS Cloudformation stack templates
    ├── bot                 # Bot files
    ├── common              # Common modules used across the project
    │   └── cls             # Classes used across the project
    ├── core                # Modules that facilitate bot and web server functionality
    ├── service             # Root for connectors and payloads
    │   ├── connector       # Available connector definitions
    │   └── payload         # Available payload definitions
    ├── web                 # Web server files
    └── README.md
```

## ToDo
*  Async execution

## Deployment
* Setup AWS stack with Cloudformation scripts provided in _/aws_ folder.
* Spin up docker containers. The easiest and fastest approach is to use provided _docker-compose_. 
  
  NOTE: Update __secrets.env__ before building the containers, 'access key' and 'key secret' are available as the output
  of Cloudformation stack.
    ```bash
    # Build container and start
    docker-compose up
    # Stop containers
    docker-compose stop
    ```

### Balena Cloud
Currently bot is running in Docker environment on Raspberry Pi v4 running BalenaOS. Their service handles deployment 
and the build in the cloud and the code is pushed via the Balena CLI, for more information go to:
[Balena CLI](https://github.com/balena-io/balena-cli/blob/master/INSTALL.md)
```bash
balena push <aplication_name>
```  
### Docker
Useful Docker commands:
```bash
# Check if Docker is installed
docker version
# Remove existing container
docker rm <container>
# Build
docker build --tag <tag> .
# Run
# Add -d to start as daemon
docker run --name <name> <container>
# or to expose Flask
docker run --name <name> -p 65010:65010 <container>

# Execute command in container
docker exec -it <name> /bin/sh
# View container logs
docker logs <container>
# Start container
docker start <container>
# Stop container
docker stop <container>
# View internal container IP address
docker inspect <container> | grep Address
```

## Development

AWS specific environment variables should be setup in development environment:
* AWS_REGION_NAME
* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY

Add persistent environment variables on Ubuntu dev box:
```bash
sudo -H gedit /etc/environment
```
Everything else is pulled from DynamoDb.

## Tokens
All tokens and secrets are stored in the DynamoDb tables: 'config' for Slack related settings, 'service' for connector
settings. Upon startup they are retrieved from the cloud and pushed to environment variables with names specified below.

### Bot
Generate token - [Slack Apps](https://api.slack.com/apps)
*  SLACK_BOT_TOKEN
*  SLACK_CLIENT_ID
*  SLACK_CLIENT_SECRET
*  SLACK_OAUTH_ACCESS_URL

### Services
*  <<SERVICE_NAME>>_CLIENT_ID
*  <<SERVICE_NAME>>_CLIENT_SECRET

#### Currently Available
[Discogs](https://www.discogs.com/settings/developers)\
[Twitter](https://developer.twitter.com/en/apps)\
[Mixcloud](https://www.mixcloud.com/developers/)


## Useful links
[Discogs API Client](https://github.com/discogs/discogs_client)

[Discogs OAuth Example](https://github.com/jesseward/discogs-oauth-example)

[Instagram Authentication](https://www.instagram.com/developer/authentication/)

[Slack - Block Kit Builder](https://api.slack.com/tools/block-kit-builder)

[Slack - Unfurling Links In Messages](https://api.slack.com/docs/message-link-unfurling#classic_unfurling)

[Slack API Home](https://api.slack.com/)

[Slack API - Python](https://python-slackclient.readthedocs.io/en/latest/index.html)

## License
[MIT](https://choosealicense.com/licenses/mit/)
