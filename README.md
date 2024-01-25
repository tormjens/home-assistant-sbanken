# Sbanken Sensor Platform for Home Assistant

# Discontinued due to Sbanken closing their API after merging with DNB.

This sensor platform uses the open API of the norwegian bank Sbanken. 

Every account the customer has in the bank is created as sensor, and updated every 30 minutes.

## Installation

Clone this repository to the `custom_components/sensor/` directory in your Home Assistant config directory.

`git clone git@github.com:tormjens/home-assistant-sbanken.git sbanken`

Restart your Home Assistant instance to load the component.

## Configuration

1. Start by signing up for the [Sbanken API program](https://sbanken.no/bruke/utviklerportalen/). This is free and the only requirement is that you are over 18.
2. Create an app in the developer portal. Store your Client ID somewhere and create a new password (secret).
3. Configure the sensor in Home Assistant.

```yaml
sensor:
    - platform: sbanken
      customer_id: 01010012345
      client_id: yourClientId
      secret: yourSecret
```

That's it! You can now use your brand new Sbanken sensor.

