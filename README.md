## VideoDownloader
First, install required libraries and frameworks with

```bash
pip install -r requirements.txt
´´´

Then setup some environment variables:
- ID = Your TG API id. You can get at my.telegram.org
- HASH = your TG API hash. You can get at my.telegram.org
- TOKEN = Your bot token. You can get at BotFather.

Edit app.py and setup admin id and modify the code as you like. It is already set up to be hosted at Heroku. If you wanna host in a VPS or other cloud, the current settings wont work. You will need to setup hosting configurations yourself.

# UNMAINTAINED APP
Because of low financial resources, this app will no longer be maintained by me(Bash). For those who still want to use the code, I have an advice: It's better if you refactor the code. It has many unknown bugs, it needs a proxy rotation script/API in order to access content that is blocked in the country where it will be hosted at, although it send the video WITH the thumbnail embedded in, it is not shown because the thumbnail is large(1080x1920, which could be something between 1mb, by default, Telegram wont show thumbnails greater than 100kb in size.). Thats all I remember at writinng moment. Thank you.
