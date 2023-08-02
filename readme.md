# Configuration
Clone this repo into a folder of your choice (the folder must be kept into the system).  
Make sure to fill your info about your telegram bot and chat id into the notifier.py file.  
To create your bot and view his token you can use the @BotFather (follow this <a href="https://www.youtube.com/watch?v=aNmRNjME6mE">tutorial</a>); to see your chat id you can use the @RawDataBot (follow this <a href="https://www.youtube.com/watch?v=UPC5Ck1oU6k">tutorial</a>).  
Open a terminal inside the cloned folder and run the command  
```shell
sudo python3 setup.py develop
```

Now you're ready to go!

If you edit some files and want to build the application again, you have to locate the build first and delete it.

To locate the current build you can use the command  
```shell
whereis notify
```
then  
```shell
sudo rm /path/to/file/notify
```

Once you've done this, your ready to build again


# Use
After the configuration, you can call from command line the notify app using 1+ argumends as the text to be sent.  
Es:
```shell
notify Hello, this is an automated message
```
The message recieved on telegram shall be "Hello, this is an automated message"

You will also be able to import the notify lib into your python projects from anywhere in your computer:  
```python
import notify

notify.send("Hello, this is an automated message")
```
