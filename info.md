# Sbanken Sensor Platform for Home Assistant

This sensor platform uses the open API of the norwegian bank Sbanken.

Every account the customer has in the bank is created as sensor, and updated every 20 minutes.

## Installation

### Installation with HACS (Home Assistant Community Store)

- Ensure that HACS is installed.
- In HACS / Integrations / menu / Custom repositories, add the url the this repository.
- Search for and install the Sbanken integration.
- Restart Home Assistant.

## Configuration

1. Start by signing up for the [Sbanken API program](https://sbanken.no/bruke/utviklerportalen/). This is free and the only requirement is that you are over 18.
2. Create an app in the developer portal.
3. Create the client id and a secret.
4. Configuration of the integration is done through Configuration > Integrations where you enter client id and the secret
