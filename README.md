# tortuga-bot
A bot for the Effectively Wild community Discord

## Configuration
This bot requires a `config.json` file, with the following configuration:

- `test_mode` - if this is set to "ON", it will instead use `test_channel_id` instead of `welcome_channel_id`
- `test_channel_id` - the channel id of the channel to be used for testing (integer)
- `welcome_channel_id` - this is the "production" channel identifier (integer)
- `bot_id` - the id of the bot ([e.g.](https://discordpy.readthedocs.io/en/stable/api.html#discord.RoleTags.bot_id)) (string)
- `discord_token` - the (secret) token for the bot (string)