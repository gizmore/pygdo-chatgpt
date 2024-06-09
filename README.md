# pygdo-chatgpt

ChatGPT bindings for the pygdo dog chatbot.


## Install

Install [pygdo](https://github.com/gizmore/pygdo). (Proprietary Software)


```
./gdo_admin.sh provide chatgpt
```

### Config

You can create a `gdo/chatgpt/secrets.toml` with the following contents.

```
chatgpt_api_key = "your-apikeyhere"
challenge_genome = ".... secret genome for a hacking challenge...."
```

### Module Config

- chatgpt_api_key
- chatgpt_chappy (GDO_User for chatgpt itself)
- chatgpt_lookback (Duration of lookback for assigning messages to Chappy: prompts


### User Settings

- chappy_temperature (chatgpt temperature for private chats)


### Channel Settings


#### LICENSE

Because this is using openai, this module is released under the
[Apache 2.0 LICENSE](./LICENSE)
No idea if that is required, else it would be proprietary software.
