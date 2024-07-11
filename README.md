# onsenpi
SP-API -> spapi -> spa + pi -> onsen + pi -> onsenpi


## Configuration
onsenpi simplifies the use of the Amazon Selling Partner API for developers. The library enhances API interaction, making it more intuitive and less cumbersome.


## Useful Links
- [Amazon SP-API Developer Documentation](https://developer-docs.amazon.com/sp-api/)
- [Python Amazon SP-API Documentation](https://python-amazon-sp-api.readthedocs.io/)

## Usage
### Initialization
```
client = SPAPIClient(
    marketplace=Marketplaces.JP,
    refresh_token="your_refresh_token",
    lwa_app_id="your_lwa_app_id",
    lwa_client_secret="your_lwa_client_secret",
)
```


[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
