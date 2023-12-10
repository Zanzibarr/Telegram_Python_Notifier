import requests, time, subprocess, os, json
import numpy as np

#TODO TEST ALL AND THEN REMOVE TESTED COMMENTS

#region -------------------- CONFIGURATIONS -------------------- #

config_path = f"{os.path.expanduser('~')}/.zanz_notify_profiles"

def write_conf_profile(name, token, from_chat_id="", to_chat_id="", disable_web_page_preview="", disable_notification="", protect_content="", allow_sending_without_reply="", parse_mode=""): #TESTED

	'''Method to set a profile in the configuration file for future use
	
	- name : str -> Unique name of the profile, can't have more profiles with the same name. If passed a name of a profile already in the configuration, that profile is gonna be modified with this parameters
	- token : str -> The token associated to the bot to use in this profile
	- from_chat_id : int/str (optional) -> Chat id to use when searching for a message to copy/forward/...
	- to_chat_id : int/str (optional) -> Chat id to use when sending/editing messages
	- disable_web_page_preview : bool (optional) -> Disables link previews for links in this message
	- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
	- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving
	- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found
	- parse_mode : str (optional) -> Mode for parsing entities in the message text. See the site for more details.'''

	if not requests.post(f"https://api.telegram.org/bot{token}/getMe").json()["ok"]: raise Exception("EXCEPTION: Invalid token.")

	if not os.path.exists(config_path):
		subprocess.run(["touch", config_path])
		with open(config_path, "w") as f:
			f.write(json.dumps({"def":"default", "profiles":{}}, indent=4))

	with open(config_path, "r") as f:
		configuration = json.loads(f.read())
	
	profile = configuration["profiles"][name] = {}
	profile["token"] = token
	profile["from_chat_id"] = from_chat_id
	profile["to_chat_id"] = to_chat_id
	profile["disable_web_page_preview"] = disable_web_page_preview
	profile["disable_notification"] = disable_notification
	profile["protect_content"] = protect_content
	profile["allow_sending_without_reply"] = allow_sending_without_reply
	profile["parse_mode"] = parse_mode

	with open(config_path, "w") as f:
		f.write(json.dumps(configuration, indent=4))

def write_conf_profile_from_dict(name, profile): #TESTED

	'''Method to set a profile in the configuration file for future use
	
	- name : str -> Unique name of the profile, can't have more profiles with the same name. If passed a name of a profile already in the configuration, that profile is gonna be modified with this parameters
	- profile : dict -> Dictionary of the profile to write. The profile must have the following fields:
		- "token" : str
		- "from_chat_id" : int/str (optional)
		- "to_chat_id" : int/str (optional)
		- "disable_web_page_preview" : bool (optional)
		- "disable_notification" : bool (optional)
		- "protect_content" : bool (optional)
		- "allow_sending_without_reply" : bool (optional)
		- "parse_mode" : str (optional)
	'''

	if "token" not in profile: raise Exception("EXCEPTION: Missing 'token' in the profile.")
	if not requests.post(f"https://api.telegram.org/bot{profile['token']}/getMe").json()["ok"]: raise Exception("EXCEPTION: Invalid token.")

	if not os.path.exists(config_path):
		subprocess.run(["touch", config_path])
		with open(config_path, "w") as f:
			f.write({"def":"default", "profiles":{}})
	
	with open(config_path, "r") as f:
		configuration = json.loads(f.read())

	if "from_chat_id" not in profile: raise Exception("EXCEPTION: Missing 'from_chat_id' in the profile.")
	if "to_chat_id" not in profile: raise Exception("EXCEPTION: Missing 'to_chat_id' in the profile.")
	if "disable_web_page_preview" not in profile: raise Exception("EXCEPTION: Missing 'disable_web_page_preview' in the profile.")
	if "disable_notification" not in profile: raise Exception("EXCEPTION: Missing 'disable_notification' in the profile.")
	if "protect_content" not in profile: raise Exception("EXCEPTION: Missing 'protect_content' in the profile.")
	if "allow_sending_without_reply" not in profile: raise Exception("EXCEPTION: Missing 'allow_sending_without_reply' in the profile.")
	if "parse_mode" not in profile: raise Exception("EXCEPTION: Missing 'parse_mode' in the profile.")

	configuration["profiles"][name] = profile

	with open(config_path, "w") as f:
		f.write(json.dumps(configuration, indent=4))

def remove_profile(name): #TESTED

	'''Method to remove a profile from the configuration file
	
	- name : str -> name of the profile to remove. If the profile isn't found, nothing happens'''

	with open(config_path, "r") as f:
		configuration = json.loads(f.read())

	if name in configuration["profiles"]:
		configuration["profiles"].pop(name)
	else:
		return

	with open(config_path, "w") as f:
		f.write(json.dumps(configuration, indent=4))

def get_profiles(): #TESTED

	'''Method to get the dict of the profiles saved in the configuration file'''

	with open(config_path, "r") as f:
		return json.loads(f.read())["profiles"]

#endregion

class bot:

	class __progress_bar:
	
		active = False
		title = ""
		text = ""
		time = 0
		time_elapsed = 0
		time_per_step = [0]
		steps = 0
		missing_steps = 0
		chat_id = ""
		message_id = ""

	__def_url = ""
	__env = False
	__send = True
	__profile = {
        "token": "",
        "from_chat_id": "",
        "to_chat_id": "",
        "disable_web_page_preview": "",
        "disable_notification": "",
        "protect_content": "",
        "allow_sending_without_reply": "",
		"parse_mode": ""
		}
	
	__pb = __progress_bar()

	def __init__(self, token="", profile="", set_on=True): #TESTED

		'''Set the environment for the bot
		
		- token : str (limited) -> token of the bot to use. Either the token or the profile must be specified. If both are specified, the token will overrite the one in the profile.
		- profile : str (limited) -> The name of the profile (in the configuration file) to associate to the bot. Either the token or the profile must be specified
		- set_on : bool (optional) -> True to keep/turn the bot on after this operation, False to keep/turn off the bot after this operation'''

		self.load_profile(token=token, name=profile)

		self.__def_url = f"https://api.telegram.org/bot{self.__profile['token']}"
		self.__env = True

		if set_on:
			self.on()
		else:
			self.off()

	#region --------------------------- PROFILES -------------------------- #

	def edit_profile(self, token="", from_chat_id="", to_chat_id="", disable_web_page_preview="", disable_notification="", protect_content="", allow_sending_without_reply="", parse_mode=""): #TESTED

		'''Method to edit the profile of this bot
		
		- token : str (optional) -> The token associated to the bot to use in this profile
		- from_chat_id : int/str (optional) -> Chat id to use when searching for a message to copy/forward/...
		- to_chat_id : int/str (optional) -> Chat id to use when sending/editing messages
		- disable_web_page_preview : bool (optional) -> Disables link previews for links in this message
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found'''

		if not requests.post(f"https://api.telegram.org/bot{token}/getMe").json()["ok"]: raise Exception("EXCEPTION: Invalid token.")

		if token != "":
			self.__profile["token"] = token
			self.__def_url = f"https://api.telegram.org/bot{self.__profile['token']}"
		if from_chat_id != "":
			self.__profile["from_chat_id"] = from_chat_id
		if to_chat_id != "":
			self.__profile["to_chat_id"] = to_chat_id
		if disable_web_page_preview != "":
			self.__profile["disable_web_page_preview"] = disable_web_page_preview
		if disable_notification != "":
			self.__profile["disable_notification"] = disable_notification
		if protect_content != "":
			self.__profile["protect_content"] = protect_content
		if allow_sending_without_reply != "":
			self.__profile["allow_sending_without_reply"] = allow_sending_without_reply
		if parse_mode != "":
			self.__profile["parse_mode"] = parse_mode

	def set_profile_from_dict(self, profile): #TESTED

		'''Method to set the profile of thie bot
		
		- profile : dict -> Dictionary of the profile to set. The profile must have the following fields:
			- "token" : str
			- "from_chat_id" : int/str (optional)
			- "to_chat_id" : int/str (optional)
			- "disable_web_page_preview" : bool (optional)
			- "disable_notification" : bool (optional)
			- "protect_content" : bool (optional)
			- "allow_sending_without_reply" : bool (optional)
			- "parse_mode" : str (optional) -> Mode for parsing entities in the message text. See the site for more details.'''

		if "token" not in profile: raise Exception("EXCEPTION: Missing 'token' in the profile.")
		if profile["token"]=="": raise Exception("EXCEPTION: Missing/Invalid token in the profile.")

		if "from_chat_id" not in profile: raise Exception("EXCEPTION: Missing 'from_chat_id' in the profile.")
		if "to_chat_id" not in profile: raise Exception("EXCEPTION: Missing 'to_chat_id' in the profile.")
		if "disable_web_page_preview" not in profile: raise Exception("EXCEPTION: Missing 'disable_web_page_preview' in the profile.")
		if "disable_notification" not in profile: raise Exception("EXCEPTION: Missing 'disable_notification' in the profile.")
		if "protect_content" not in profile: raise Exception("EXCEPTION: Missing 'protect_content' in the profile.")
		if "allow_sending_without_reply" not in profile: raise Exception("EXCEPTION: Missing 'allow_sending_without_reply' in the profile.")
		if "parse_mode" not in profile: raise Exception("EXCEPTION: Missing 'parse_mode' in the profile.")

		self.__profile["token"] = profile["token"]
		self.__profile["from_chat_id"] = profile["from_chat_id"]
		self.__profile["to_chat_id"] = profile["to_chat_id"]
		self.__profile["disable_web_page_preview"] = profile["disable_web_page_preview"]
		self.__profile["disable_notification"] = profile["disable_notification"]
		self.__profile["protect_content"] = profile["protect_content"]
		self.__profile["allow_sending_without_reply"] = profile["allow_sending_without_reply"]
		self.__profile["parse_mode"] = profile["parse_mode"]

		self.__def_url = f"https://api.telegram.org/bot{self.__profile['token']}"

	def load_profile(self, token="", name=""): #TESTED

		'''Method to associate a bot to a profile for faster configuration
		
		- token : str (limited) -> The token to use. Either the token or the name must be specified. If both are specified, the token will overrite the one in the profile.
		- name : str (limited) -> Unique name of the profile to use. Either the token or the name must be specified.'''

		with open(config_path, "r") as f:
			configuration = json.loads(f.read())["profiles"]

		if token == "" and name == "":
			raise Exception("EXCEPTION: Either the token or the name of the profile must be specified.") #---/---
		
		elif token == "" and name != "":
			if name not in configuration:
				print(f"Warning: the name {name} of the profile to load isn't associated to any profile.\nNo profile loaded.")
				return #---/no match
			if "token" not in configuration[name]:
				raise Exception("EXCEPTION: Configuration file corrupted.")
			self.set_profile_from_dict(profile=configuration[name]) #---/valid
			if not requests.post(f"https://api.telegram.org/bot{self.__profile['token']}/getMe").json()["ok"]:
				print(f"Warning: the token inside the profile {name} is invalid, profile loaded anyways.\nConsider changing it or specify a new token.") #---/invalid

		elif name == "":
			if not requests.post(f"https://api.telegram.org/bot{token}/getMe").json()["ok"]:
				raise Exception("EXCEPTION: Invalid token.") #invalid/---
			self.__profile["token"] = token #valid/---
		
		elif name != "":
			valid_token = requests.post(f"https://api.telegram.org/bot{token}/getMe").json()["ok"]
			if name not in configuration:
				print(f"Warning: the name {name} of the profile to load isn't associated to any profile. Loading only the token specified.")
				if not valid_token:
					raise Exception("EXCEPTION: Invalid token.") #invalid/no match
				self.__profile["token"] = token #valid/no match
			else:
				if "token" not in configuration[name]:
					raise Exception("EXCEPTION: Configuration file corrupted.")
				self.set_profile_from_dict(profile=configuration[name])
				valid_profile = requests.post(f"https://api.telegram.org/bot{self.__profile['token']}/getMe").json()["ok"]
				if not valid_token:
					if not valid_profile:
						raise Exception("EXCEPTION: Both tokens (the one specified and the one in the profile) are invalid.") #invalid/invalid
					print(f"Warning: the token specified is invalid.\nUsing the {name} profile token.") #invalid/valid
				else:
					if not valid_profile:
						print(f"Warning: the token inside the profile {name} is invalid.\nRest of the profile loaded successfully, used token specified.")
					self.__profile["token"] = token #valid/valid or invalid

	def save_profile(self, name): #TESTED

		'''Method to save on the configuration file the profile associated to this bot
		
		- name : str -> The name to give to the profile'''
		
		write_conf_profile_from_dict(name, self.__profile)

	#endregion

	#region -------------------------- UTILITIES -------------------------- #

	def send_exception(self, text="", chat_id=""): #TESTED

		'''Sends a text message in the exception format
		
		- text : str (optional) -> Additional text to write in the message
		- chat_id : int/str (optional) -> chat_id to send the message to (If not specified, using the default one)'''

		message = "\U00002757 *EXCEPTION CAPTURED* \U00002757"
		if len(text) > 0: message = message + "\n" + text

		return self.send_message_by_text(message, chat_id=chat_id, disable_notification=False, parse_mode="Markdown")

	def create_progress_bar(self, steps, title="", text="", chat_id=""): #ŦESTED

		'''Creates and send the initial progress bar (works only on for loops with a known number of steps)
		
		- steps : int -> Number of steps of the progress bar
		- title : str (optional) -> Title of the progress bar
		- text : str (optional) -> Additional text of the progress bar
		- chat_id : int/str (optional) -> chat_id to send the message to (If not specified, using the default one)'''

		message = f"*{title}*"+"\n"+text+"\n"
		message = message + "\[" + '\u2581'*steps + "]\n"
		message = message + f"Time elapsed: 0s/0s"

		r = self.send_message_by_text(message, chat_id=chat_id, parse_mode="Markdown")

		self.__pb.active = True
		self.__pb.title = title
		self.__pb.text = text
		self.__pb.time = time.time()
		self.__pb.time_elapsed = 0
		self.__pb.time_per_step = [0]
		self.__pb.steps = steps
		self.__pb.missing_steps = steps
		self.__pb.chat_id = chat_id
		self.__pb.message_id = r["result"]["message_id"]

		return r

	def update_progress_bar(self): #TESTED

		'''Updates of 1 step the progress bar (works only on for loops with a known number of steps)'''

		if not self.__pb.active: raise Exception("EXCEPTION: Progress bar hasn't been created or has already terminated.")

		self.__pb.missing_steps = self.__pb.missing_steps - 1

		self.__pb.time_per_step.append(time.time() - self.__pb.time - self.__pb.time_elapsed)
		self.__pb.time_elapsed = time.time() - self.__pb.time

		message = f"*{self.__pb.title}*"+"\n"+self.__pb.text+"\n"
		message = message + "\[" + '\u2588'*(self.__pb.steps-self.__pb.missing_steps) + '\u2581'*self.__pb.missing_steps + "]\n"
		message = message + f"Time elapsed: {round(self.__pb.time_elapsed, 2)}s/{round(self.__pb.time_elapsed + self.__pb.missing_steps * np.average(self.__pb.time_per_step), 2)}s"

		r = self.edit_message_text(message, message_id=self.__pb.message_id, chat_id=self.__pb.chat_id, parse_mode="Markdown")

		if self.__pb.missing_steps == 0:
			self.__pb.active = False

		return r

	def conclude_progress_bar(self): #TESTED

		'''Concludes a progress bar (use it after the end of the for loop)'''

		message = f"*{self.__pb.title}*"+"\n"+self.__pb.text+"\n"
		message = message + "\nCompleted in " + str(round(self.__pb.time_elapsed, 2)) + "s."

		self.__pb.active = False

		return self.edit_message_text(message, message_id=self.__pb.message_id, chat_id=self.__pb.chat_id)

	#endregion

	#region ------------------------ TELEGRAM API ------------------------- #

	def on(self): #TESTED
		
		'''Turns on the bot'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")

		self.__send = True

	def off(self): #TESTED

		'''Turns off the bot'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")

		self.__send = False

	def get_me(self): #TESTED
		
		'''A simple method for testing your bot's authentication token. Requires no parameters. Returns basic information about the bot in form of a User object.'''

		return self.__request_format("getMe").json()

	def log_out(self):

		'''Use this method to log out from the cloud Bot API server before launching the bot locally. You must log out the bot before running it locally, otherwise there is no guarantee that the bot will receive updates. After a successful call, you can immediately log in on a local server, but will not be able to log in back to the cloud Bot API server for 10 minutes. Returns True on success. Requires no parameters.'''

		return self.__request_format("logOut").json()

	def close(self):

		'''Use this method to close the bot instance before moving it from one local server to another. You need to delete the webhook before calling this method to ensure that the bot isn't launched again after server restart. The method will return error 429 in the first 10 minutes after the bot is launched. Returns True on success. Requires no parameters.'''
		
		return self.__request_format("close").json()

	def send_message_by_text(self, text, chat_id="", message_thread_id="", parse_mode="", entities="", disable_web_page_preview="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send text messages. On success, the sent Message is returned.
		
		- text : str -> the text to write (can be formatted with MD, see the site for more info)
		- chat_id : int/str (optional) -> chat to send the message to. The default one is the one specified by the profile
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only
		- parse_mode : str (optional) -> Mode for parsing entities in the message text. See site for more details.
		- entities : List[MessageEntity] (optional) -> A JSON-serialized list of special entities that appear in message text, which can be specified instead of parse_mode
		- disable_web_page_preview : bool (optional) -> Disables link previews for links in this message
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
		
		See the site for formatting options.
		Refer to https://core.telegram.org/bots/api (sendMessage) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_web_page_preview == "":
			disable_web_page_preview = self.__profile["disable_web_page_preview"]
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]
		if parse_mode == "":
			parse_mode = self.__profile["parse_mode"]

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"text" : text,
			"parse_mode" : parse_mode,
			"entities" : json.dumps(entities),
			"disable_web_page_preview" : disable_web_page_preview,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup
		}

		return self.__request_format("sendMessage", data=data).json()

	def send_message_by_file(self, file_path, chat_id="", message_thread_id="", parse_mode="", entities="", disable_web_page_preview="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send text messages. On success, the sent Message is returned.
		
		- file_path : str -> path to the text file to read
		- chat_id : int/str (optional) -> chat to send the message to. The default one is the one specified by the profile
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only
		- parse_mode : str (optional) -> Mode for parsing entities in the message text. See site for more details.
		- entities : List[MessageEntity] (optional) -> A JSON-serialized list of special entities that appear in message text, which can be specified instead of parse_mode
		- disable_web_page_preview : bool (optional) -> Disables link previews for links in this message
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
		
		See the site for formatting options
		Refer to https://core.telegram.org/bots/api (sendMessage) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_web_page_preview == "":
			disable_web_page_preview = self.__profile["disable_web_page_preview"]
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]
		if parse_mode == "":
			parse_mode = self.__profile["parse_mode"]

		with open(file_path, "r") as f:
			text = f.read()

		return self.send_message_by_text(text=text, chat_id=chat_id, message_thread_id=message_thread_id, parse_mode=parse_mode, entities=entities, disable_web_page_preview=disable_web_page_preview, disable_notification=disable_notification, protect_content=protect_content, reply_to_message_id=reply_to_message_id, allow_sending_without_reply=allow_sending_without_reply, reply_markup=reply_markup)

	def forward_message(self, message_id, chat_id, from_chat_id="", message_thread_id="", disable_notification="", protect_content=""):

		'''Use this method to forward messages of any kind. Service messages can't be forwarded. On success, the sent Message is returned.
		
		- message_id : int -> the message to forward
		- chat_id : int/str -> chat_id recieving the message
		- from_chat_id : int/str (optional) -> chat_id of the message to forward. The default one is the one specified by the profile
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the forwarded message from forwarding and saving
		
		Refer to https://core.telegram.org/bots/api (forwardMessage) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if from_chat_id == "":
			from_chat_id = self.__profile["from_chat_id"]
		if from_chat_id == "":
			raise Exception("EXCEPTION: Either set a from_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"from_chat_id" : from_chat_id,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"message_id" : message_id,
		}

		return self.__request_format("forwardMessage", data=data).json()

	def copy_message(self, message_id, chat_id, from_chat_id="", message_thread_id="", caption="", parse_mode="", caption_entities="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to copy messages of any kind. Service messages and invoice messages can't be copied. A quiz poll can be copied only if the value of the field correct_option_id is known to the bot. The method is analogous to the method forwardMessage, but the copied message doesn't have a link to the original message. Returns the MessageId of the sent message on success.
		
		- message_id : int -> the message to copy
		- chat_id : int/str -> chat id recieving the message
		- from_chat_id : int/str (optional) -> chat_id of the message to forward. The default one is the one specified by the profile
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only
		- caption : str (optional) -> New caption for media, 0-1024 characters after entities parsing. If not specified, the original caption is kept
		- parse_mode : str (optional) -> Mode for parsing entities in the new caption. See site for more details.
		- caption_entities : List[MessageEntity] (optional) -> A JSON-serialized list of special entities that appear in the new caption, which can be specified instead of parse_mode
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the forwarded message from forwarding and saving
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (copyMessage) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if from_chat_id == "":
			from_chat_id = self.__profile["from_chat_id"]
		if from_chat_id == "":
			raise Exception("EXCEPTION: Either set a from_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]
		if parse_mode == "":
			parse_mode = self.__profile["parse_mode"]

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"from_chat_id" : from_chat_id,
			"message_id" : message_id,
			"caption" : caption,
			"parse_mode" : parse_mode,
			"caption_entities" : json.dumps(caption_entities),
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("copyMessage", data=data).json()
	
	def send_photo_by_path(self, file_path, chat_id = "", message_thread_id="", caption="", parse_mode="", caption_entities="", has_spoiler="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send photos. On success, the sent Message is returned.
	
		- file_path : str -> Path to the photo to send
		- chat_id : int/str (optional) -> chat_id of the chat to send the photo to. The default one is the one specified by the profile
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only
		- caption : str (optional) -> Photo caption (may also be used when resending photos by file_id), 0-1024 characters after entities parsing
		- parse_mode : str (optional) -> Mode for parsing entities in the photo caption. See the site for more details.
		- caption_entities : List[MessageEntity] (optional) -> A JSON-serialized list of special entities that appear in the caption, which can be specified instead of parse_mode
		- has_spoiler : bool (optional) -> Pass True if the photo needs to be covered with a spoiler animation
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendPhoto) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]
		if parse_mode == "":
			parse_mode = self.__profile["parse_mode"]

		if not os.path.exists(file_path):
			raise Exception(f"EXCEPTION: The file_path {file_path} doesn't lead to any file.")

		files = {"photo" : open(file_path, "rb")}

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"caption" : caption,
			"parse_mode" : parse_mode,
			"caption_entities" : json.dumps(caption_entities),
			"has_spoiler" : has_spoiler,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendPhoto", data=data, files=files).json()
	
	def send_photo(self, photo, chat_id = "", message_thread_id="", caption="", parse_mode="", caption_entities="", has_spoiler="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send photos. On success, the sent Message is returned.
	
		- photo : InputFile/str -> Photo to send. Pass a file_id as String to send a photo that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a photo from the Internet, or upload a new photo using multipart/form-data. The photo must be at most 10 MB in size. The photo's width and height must not exceed 10000 in total. Width and height ratio must be at most 20. More information on the site
		- chat_id : int/str (optional) -> chat_id of the chat to send the photo to. The default one is the one specified by the profile
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only
		- caption : str (optional) -> Photo caption (may also be used when resending photos by file_id), 0-1024 characters after entities parsing
		- parse_mode : str (optional) -> Mode for parsing entities in the photo caption. See the site for more details.
		- caption_entities : List[MessageEntity] (optional) -> A JSON-serialized list of special entities that appear in the caption, which can be specified instead of parse_mode
		- has_spoiler : bool (optional) -> Pass True if the photo needs to be covered with a spoiler animation
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendPhoto) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]
		if parse_mode == "":
			parse_mode = self.__profile["parse_mode"]

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"photo" : photo,
			"caption" : caption,
			"parse_mode" : parse_mode,
			"caption_entities" : json.dumps(caption_entities),
			"has_spoiler" : has_spoiler,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendPhoto", data=data).json()
	
	def send_audio_by_path(self, file_path, chat_id="", message_thread_id="", caption="", parse_mode="", caption_entities="", duration="", performer="", title="", thumbnail="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send audio files, if you want Telegram clients to display them in the music player. Your audio must be in the .MP3 or .M4A format. On success, the sent Message is returned. Bots can currently send audio files of up to 50 MB in size, this limit may be changed in the future.
		
		For sending voice messages, use the sendVoice method instead.
		
		- file_path : str -> Path to the audio to send
		- chat_id : int/str (optional) -> chat_id of the chat to send the audio to. The default one is the one specified by the profile
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only
		- caption : str (optional) -> Audio caption (may also be used when resending audios by file_id), 0-1024 characters after entities parsing
		- parse_mode : str (optional) -> Mode for parsing entities in the audio caption. See the site for more details.
		- caption_entities : List[MessageEntity] (optional) -> A JSON-serialized list of special entities that appear in the caption, which can be specified instead of parse_mode
		- duration : int (optional) -> Duration of the audio in seconds
		- performer : str (optional) -> Performer
		- title : str (optional) -> Track name
		- thumbnail : str (optional) -> Path of the Thumbnail of the file sent; can be ignored if thumbnail generation for the file is supported server-side. The thumbnail should be in JPEG format and less than 200 kB in size. A thumbnail's width and height should not exceed 320. More information in the site.
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendAudio) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]
		if parse_mode == "":
			parse_mode = self.__profile["parse_mode"]

		if not os.path.exists(file_path):
			raise Exception(f"EXCEPTION: The file_path {file_path} doesn't lead to any file.")
		if not os.path.exists(thumbnail):
			raise Exception(f"EXCEPTION: The file_path {thumbnail} doesn't lead to any file.")

		files = {"audio" : open(file_path, "rb")}
		if thumbnail != "":
			files["thumbnail"] = open(thumbnail, "rb")

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"caption" : caption,
			"parse_mode" : parse_mode,
			"caption_entities" : json.dumps(caption_entities),
			"duration" : duration,
			"performer" : performer,
			"title" : title,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendAudio", data=data, files=files).json()
	
	def send_audio(self, audio, chat_id="", message_thread_id="", caption="", parse_mode="", caption_entities="", duration="", performer="", title="", thumbnail="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send audio files, if you want Telegram clients to display them in the music player. Your audio must be in the .MP3 or .M4A format. On success, the sent Message is returned. Bots can currently send audio files of up to 50 MB in size, this limit may be changed in the future.
		
		For sending voice messages, use the send_voice method instead.
		
		- audio : InputFile/str -> Audio file to send. Pass a file_id as String to send an audio file that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get an audio file from the Internet, or upload a new one using multipart/form-data. More information on the site
		- chat_id : int/str (optional) -> chat_id of the chat to send the audio to. The default one is the one specified by the profile
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only
		- caption : str (optional) -> Audio caption (may also be used when resending audios by file_id), 0-1024 characters after entities parsing
		- parse_mode : str (optional) -> Mode for parsing entities in the audio caption. See the site for more details.
		- caption_entities : List[MessageEntity] (optional) -> A JSON-serialized list of special entities that appear in the caption, which can be specified instead of parse_mode
		- duration : int (optional) -> Duration of the audio in seconds
		- performer : str (optional) -> Performer
		- title : str (optional) -> Track name
		- thumbnail : str (optional) -> Path of the Thumbnail of the file sent; can be ignored if thumbnail generation for the file is supported server-side. The thumbnail should be in JPEG format and less than 200 kB in size. A thumbnail's width and height should not exceed 320. More information in the site.
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendAudio) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]
		if parse_mode == "":
			parse_mode = self.__profile["parse_mode"]

		if not os.path.exists(thumbnail):
			raise Exception(f"EXCEPTION: The file_path {thumbnail} doesn't lead to any file.")

		files = {}
		if thumbnail != "":
			files["thumbnail"] = open(thumbnail, "rb")

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"audio" : audio,
			"caption" : caption,
			"parse_mode" : parse_mode,
			"caption_entities" : json.dumps(caption_entities),
			"duration" : duration,
			"performer" : performer,
			"title" : title,
			"thumbnail" : thumbnail,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendAudio", data=data, files=files).json()
	
	def send_document_by_path(self, file_path, chat_id="", message_thread_id="", thumbnail="", caption="", parse_mode="", caption_entities="", disable_content_type_detection="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send general files. On success, the sent Message is returned. Bots can currently send files of any type of up to 50 MB in size, this limit may be changed in the future.
		
		- file_path : str -> Path to the document to send
		- chat_id : int/str (optional) -> chat_id of the chat to send the document to. The default one is the one specified by the profile
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only
		- thumbnail : str (optional) -> Path of the Thumbnail of the file sent; can be ignored if thumbnail generation for the file is supported server-side. The thumbnail should be in JPEG format and less than 200 kB in size. A thumbnail's width and height should not exceed 320. More information in the site.
		- caption : str (optional) -> Document caption (may also be used when resending documents by file_id), 0-1024 characters after entities parsing
		- parse_mode : str (optional) -> Mode for parsing entities in the document caption. See the site for more details.
		- caption_entities : List[MessageEntity] (optional) -> A JSON-serialized list of special entities that appear in the caption, which can be specified instead of parse_mode
		- disable_content_type_detection : bool (optional) -> Disables automatic server-side content type detection for files uploaded using multipart/form-data
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendDocument) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]
		if parse_mode == "":
			parse_mode = self.__profile["parse_mode"]

		if not os.path.exists(file_path):
			raise Exception(f"EXCEPTION: The file_path {file_path} doesn't lead to any file.")
		if not os.path.exists(thumbnail):
			raise Exception(f"EXCEPTION: The file_path {thumbnail} doesn't lead to any file.")

		files = {"document" : open(file_path, "rb")}
		if thumbnail != "":
			files["thumbnail"] = open(thumbnail, "rb")

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"caption" : caption,
			"parse_mode" : parse_mode,
			"caption_entities" : json.dumps(caption_entities),
			"disable_content_type_detection" : disable_content_type_detection,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendDocument", data=data, files=files).json()
	
	def send_document(self, document, chat_id="", message_thread_id="", thumbnail="", caption="", parse_mode="", caption_entities="", disable_content_type_detection="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send general files. On success, the sent Message is returned. Bots can currently send files of any type of up to 50 MB in size, this limit may be changed in the future.
	
		- document : InputFile/str -> File to send. Pass a file_id as String to send a file that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a file from the Internet, or upload a new one using multipart/form-data. More information in the site
		- chat_id : int/str (optional) -> chat_id of the chat to send the document to. The default one is the one specified by the profile
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only
		- thumbnail : str (optional) -> Path of the Thumbnail of the file sent; can be ignored if thumbnail generation for the file is supported server-side. The thumbnail should be in JPEG format and less than 200 kB in size. A thumbnail's width and height should not exceed 320. More information in the site.
		- caption : str (optional) -> Document caption (may also be used when resending documents by file_id), 0-1024 characters after entities parsing
		- parse_mode : str (optional) -> Mode for parsing entities in the document caption. See the site for more details.
		- caption_entities : List[MessageEntity] (optional) -> A JSON-serialized list of special entities that appear in the caption, which can be specified instead of parse_mode
		- disable_content_type_detection : bool (optional) -> Disables automatic server-side content type detection for files uploaded using multipart/form-data
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendDocument) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]
		if parse_mode == "":
			parse_mode = self.__profile["parse_mode"]

		if not os.path.exists(thumbnail):
			raise Exception(f"EXCEPTION: The file_path {thumbnail} doesn't lead to any file.")

		files = {}
		if thumbnail != "":
			files["thumbnail"] = open(thumbnail, "rb")

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"document" : document,
			"thumbnail" : thumbnail,
			"caption" : caption,
			"parse_mode" : parse_mode,
			"caption_entities" : json.dumps(caption_entities),
			"disable_content_type_detection" : disable_content_type_detection,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendDocument", data=data, files=files).json()
	
	def send_video_by_path(self, file_path, chat_id="", message_thread_id="", duration="", width="", height="", thumbnail="", caption="", parse_mode="", caption_entities="", has_spoiler="", supports_streaming="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send video files, Telegram clients support MPEG4 videos (other formats may be sent as Document). On success, the sent Message is returned. Bots can currently send video files of up to 50 MB in size, this limit may be changed in the future.
	
		- file_path : str -> The path to the video to send
		- chat_id : int/str (optional) -> chat_id of the chat to send the video to. The default one is the one specified by the profile
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only
		- duration : int (optional) -> Duration of sent video in seconds
		- width : int (optional) -> Video width
		- height : int (optional) -> Video height
		- thumbnail : str (optional) -> Path of the Thumbnail of the file sent; can be ignored if thumbnail generation for the file is supported server-side. The thumbnail should be in JPEG format and less than 200 kB in size. A thumbnail's width and height should not exceed 320. More information in the site.
		- caption : str (optional) -> Video caption (may also be used when resending videos by file_id), 0-1024 characters after entities parsing
		- parse_mode : str (optional) -> Mode for parsing entities in the video caption. See the site for more details.
		- caption_entities : List[MessageEntity] (optional) -> A JSON-serialized list of special entities that appear in the caption, which can be specified instead of parse_mode
		- has_spoiler : bool (optional) -> Pass True if the video needs to be covered with a spoiler animation
		- supports_streaming : bool (optional) -> Pass True if the uploaded video is suitable for streaming
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendVideo) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]
		if parse_mode == "":
			parse_mode = self.__profile["parse_mode"]

		if not os.path.exists(file_path):
			raise Exception(f"EXCEPTION: The file_path {file_path} doesn't lead to any file.")
		if not os.path.exists(thumbnail):
			raise Exception(f"EXCEPTION: The file_path {thumbnail} doesn't lead to any file.")

		files = {"video" : open(file_path, "rb")}
		if thumbnail != "":
			files["thumbnail"] = open(thumbnail, "rb")

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"duration" : duration,
			"width" : width,
			"height" : height,
			"caption" : caption,
			"parse_mode" : parse_mode,
			"caption_entities" : json.dumps(caption_entities),
			"has_spoiler" : has_spoiler,
			"supports_streaming" : supports_streaming,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendVideo", data=data, files=files).json()
	
	def send_video(self, video, chat_id="", message_thread_id="", duration="", width="", height="", thumbnail="", caption="", parse_mode="", caption_entities="", has_spoiler="", supports_streaming="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send video files, Telegram clients support MPEG4 videos (other formats may be sent as Document). On success, the sent Message is returned. Bots can currently send video files of up to 50 MB in size, this limit may be changed in the future.
	
		- video : InputFile/str -> Video to send. Pass a file_id as String to send a video that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a video from the Internet, or upload a new video using multipart/form-data. More information in the site.
		- chat_id : int/str (optional) -> chat_id of the chat to send the video to. The default one is the one specified by the profile
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only
		- duration : int (optional) -> Duration of sent video in seconds
		- width : int (optional) -> Video width
		- height : int (optional) -> Video height
		- thumbnail : str (optional) -> Path of the Thumbnail of the file sent; can be ignored if thumbnail generation for the file is supported server-side. The thumbnail should be in JPEG format and less than 200 kB in size. A thumbnail's width and height should not exceed 320. More information in the site.
		- caption : str (optional) -> Video caption (may also be used when resending videos by file_id), 0-1024 characters after entities parsing
		- parse_mode : str (optional) -> Mode for parsing entities in the video caption. See the site for more details.
		- caption_entities : List[MessageEntity] (optional) -> A JSON-serialized list of special entities that appear in the caption, which can be specified instead of parse_mode
		- has_spoiler : bool (optional) -> Pass True if the video needs to be covered with a spoiler animation
		- supports_streaming : bool (optional) -> Pass True if the uploaded video is suitable for streaming
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendVideo) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]
		if parse_mode == "":
			parse_mode = self.__profile["parse_mode"]

		if not os.path.exists(thumbnail):
			raise Exception(f"EXCEPTION: The file_path {thumbnail} doesn't lead to any file.")

		files = {}
		if thumbnail != "":
			files["thumbnail"] = open(thumbnail, "rb")

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"video" : video,
			"duration" : duration,
			"width" : width,
			"height" : height,
			"caption" : caption,
			"parse_mode" : parse_mode,
			"caption_entities" : json.dumps(caption_entities),
			"has_spoiler" : has_spoiler,
			"supports_streaming" : supports_streaming,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendVideo", data=data, files=files).json()
	
	def send_animation_by_path(self, file_path, chat_id="", message_thread_id="", duration="", width="", height="", thumbnail="", caption="", parse_mode="", caption_entities="", has_spoiler="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send animation files (GIF or H.264/MPEG-4 AVC video without sound). On success, the sent Message is returned. Bots can currently send animation files of up to 50 MB in size, this limit may be changed in the future.
	
		- file_path : str -> The path to the animation to send
		- chat_id : int/str (optional) -> chat_id of the chat to send the animation to. The default one is the one specified by the profile
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only
		- duration : int (optional) -> Duration of the animation in seconds
		- width : int (optional) -> Width of the animation
		- height : int (optional) -> Height of the animation
		- thumbnail : str (optional) -> Path of the Thumbnail of the file sent; can be ignored if thumbnail generation for the file is supported server-side. The thumbnail should be in JPEG format and less than 200 kB in size. A thumbnail's width and height should not exceed 320. More information in the site.
		- caption : str (optional) -> Caption for the animation (may also be used when resending animations by file_id). Should be between 0 to 1024 characters after entities parsing.
		- parse_mode : str (optional) -> Mode for parsing entities in the animation caption. See the site for more details.
		- caption_entities : List[MessageEntity] (optional) -> A JSON-serialized list of special entities that appear in the caption, which can be specified instead of parse_mode.
		- has_spoiler : bool (optional) -> Specifies whether the animation has a spoiler.
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving.
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message.
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found.
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove the reply keyboard, or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendAnimation) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]
		if parse_mode == "":
			parse_mode = self.__profile["parse_mode"]

		if not os.path.exists(file_path):
			raise Exception(f"EXCEPTION: The file_path {file_path} doesn't lead to any file.")
		if not os.path.exists(thumbnail):
			raise Exception(f"EXCEPTION: The file_path {thumbnail} doesn't lead to any file.")

		files = {"animation" : open(file_path, "rb")}
		if thumbnail != "":
			files["thumbnail"] = open(thumbnail, "rb")

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"duration" : duration,
			"width" : width,
			"height" : height,
			"caption" : caption,
			"parse_mode" : parse_mode,
			"caption_entities" : json.dumps(caption_entities),
			"has_spoiler" : has_spoiler,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendAnimation", data=data, files=files).json()
	
	def send_animation(self, animation, chat_id="", message_thread_id="", duration="", width="", height="", thumbnail="", caption="", parse_mode="", caption_entities="", has_spoiler="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send animation files (GIF or H.264/MPEG-4 AVC video without sound). On success, the sent Message is returned. Bots can currently send animation files of up to 50 MB in size, this limit may be changed in the future.
	
		- animation : InputFile/str -> Animation to send. Pass an animation file_id as a String to send an animation that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get an animation from the Internet, or upload a new one using multipart/form-data. More information on supported formats and limitations on the site.
		- chat_id : int/str (optional) -> chat_id of the chat to send the animation to. The default one is the one specified by the profile
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only
		- duration : int (optional) -> Duration of the animation in seconds
		- width : int (optional) -> Width of the animation
		- height : int (optional) -> Height of the animation
		- thumbnail : str (optional) -> Path of the Thumbnail of the file sent; can be ignored if thumbnail generation for the file is supported server-side. The thumbnail should be in JPEG format and less than 200 kB in size. A thumbnail's width and height should not exceed 320. More information in the site.
		- caption : str (optional) -> Caption for the animation (may also be used when resending animations by file_id). Should be between 0 to 1024 characters after entities parsing.
		- parse_mode : str (optional) -> Mode for parsing entities in the animation caption. See the site for more details.
		- caption_entities : List[MessageEntity] (optional) -> A JSON-serialized list of special entities that appear in the caption, which can be specified instead of parse_mode.
		- has_spoiler : bool (optional) -> Specifies whether the animation has a spoiler.
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving.
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message.
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found.
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove the reply keyboard, or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendAnimation) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]
		if parse_mode == "":
			parse_mode = self.__profile["parse_mode"]

		if not os.path.exists(thumbnail):
			raise Exception(f"EXCEPTION: The file_path {thumbnail} doesn't lead to any file.")

		files = {}
		if thumbnail != "":
			files["thumbnail"] = open(thumbnail, "rb")

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"animation" : animation,
			"duration" : duration,
			"width" : width,
			"height" : height,
			"caption" : caption,
			"parse_mode" : parse_mode,
			"caption_entities" : json.dumps(caption_entities),
			"has_spoiler" : has_spoiler,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendAnimation", data=data, files=files).json()
	
	def send_voice_by_path(self, file_path, chat_id="", message_thread_id="", caption="", parse_mode="", caption_entities="", duration="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send audio files, if you want Telegram clients to display the file as a playable voice message. For this to work, your audio must be in an .OGG file encoded with OPUS (other formats may be sent as Audio or Document). On success, the sent Message is returned. Bots can currently send voice messages of up to 50 MB in size, this limit may be changed in the future.
	
		- file_path : str -> The path to the voice to send
		- chat_id : int/str (optional) -> Chat ID of the chat to send the voice message to. The default one is specified by the profile.
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only.
		- caption : str (optional) -> Caption for the voice message (may also be used when resending voice messages by file_id). Should be between 0 to 1024 characters after entities parsing.
		- parse_mode : str (optional) -> Mode for parsing entities in the voice message caption. See the site for more details.
		- caption_entities : List[MessageEntity] (optional) -> A JSON-serialized list of special entities that appear in the caption, which can be specified instead of parse_mode.
		- duration : int (optional) -> Duration of the voice message in seconds.
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving.
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message.
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found.
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove the reply keyboard, or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendVoice) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]
		if parse_mode == "":
			parse_mode = self.__profile["parse_mode"]

		if not os.path.exists(file_path):
			raise Exception(f"EXCEPTION: The file_path {file_path} doesn't lead to any file.")

		files = {"voice" : open(file_path, "rb")}

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"caption" : caption,
			"parse_mode" : parse_mode,
			"caption_entities" : json.dumps(caption_entities),
			"duration" : duration,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendVoice", data=data, files=files).json()
	
	def send_voice(self, voice, chat_id="", message_thread_id="", caption="", parse_mode="", caption_entities="", duration="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send audio files, if you want Telegram clients to display the file as a playable voice message. For this to work, your audio must be in an .OGG file encoded with OPUS (other formats may be sent as Audio or Document). On success, the sent Message is returned. Bots can currently send voice messages of up to 50 MB in size, this limit may be changed in the future.
	
		- voice : InputFile/str -> Voice message to send. Pass a voice file_id as a String to send a voice message that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a voice message from the Internet, or upload a new one using multipart/form-data.
		- chat_id : int/str (optional) -> Chat ID of the chat to send the voice message to. The default one is specified by the profile.
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only.
		- caption : str (optional) -> Caption for the voice message (may also be used when resending voice messages by file_id). Should be between 0 to 1024 characters after entities parsing.
		- parse_mode : str (optional) -> Mode for parsing entities in the voice message caption. See the site for more details.
		- caption_entities : List[MessageEntity] (optional) -> A JSON-serialized list of special entities that appear in the caption, which can be specified instead of parse_mode.
		- duration : int (optional) -> Duration of the voice message in seconds.
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving.
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message.
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found.
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove the reply keyboard, or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendVoice) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]
		if parse_mode == "":
			parse_mode = self.__profile["parse_mode"]

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"voice" : voice,
			"caption" : caption,
			"parse_mode" : parse_mode,
			"caption_entities" : json.dumps(caption_entities),
			"duration" : duration,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendVoice", data=data).json()
	
	def send_videonote_by_path(self, file_path, chat_id="", message_thread_id="", duration="", length="", thumbnail="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''As of v.4.0, Telegram clients support rounded square MPEG4 videos of up to 1 minute long. Use this method to send video messages. On success, the sent Message is returned.
		
		- file_path : str -> The path to the videonote to send
		- chat_id : int/str (optional) -> chat_id of the chat to send the video note to. The default one is the one specified by the profile.
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only.
		- duration : int (optional) -> Duration of the video note in seconds.
		- length : int (optional) -> Length of the video note.
		- thumbnail : str (optional) -> Path of the Thumbnail of the file sent; can be ignored if thumbnail generation for the file is supported server-side. The thumbnail should be in JPEG format and less than 200 kB in size. A thumbnail's width and height should not exceed 320. More information in the site.
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving.
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message.
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found.
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove the reply keyboard, or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendVideoNote) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]

		if not os.path.exists(file_path):
			raise Exception(f"EXCEPTION: The file_path {file_path} doesn't lead to any file.")

		files = {"video_note" : open(file_path, "rb")}
		if thumbnail != "":
			files["thumbnail"] = open(thumbnail, "rb")

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"duration" : duration,
			"length" : length,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendVideoNote", data=data, files = files).json()
	
	def send_videonote(self, video_note, chat_id="", message_thread_id="", duration="", length="", thumbnail="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''As of v.4.0, Telegram clients support rounded square MPEG4 videos of up to 1 minute long. Use this method to send video messages. On success, the sent Message is returned.
		
		- video_note : InputFile/str -> Video note to send. Pass a file_id as String to send a video note that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a video note from the Internet, or upload a new video note using multipart/form-data. The video note must be at most 10 MB in size. More information on supported formats and limitations on the site.
		- chat_id : int/str (optional) -> chat_id of the chat to send the video note to. The default one is the one specified by the profile.
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only.
		- duration : int (optional) -> Duration of the video note in seconds.
		- length : int (optional) -> Length of the video note.
		- thumbnail : str (optional) -> Path of the Thumbnail of the file sent; can be ignored if thumbnail generation for the file is supported server-side. The thumbnail should be in JPEG format and less than 200 kB in size. A thumbnail's width and height should not exceed 320. More information in the site.
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving.
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message.
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found.
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove the reply keyboard, or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendVideoNote) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]

		files = {}
		if thumbnail != "":
			files["thumbnail"] = open(thumbnail, "rb")

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"video_note" : video_note,
			"duration" : duration,
			"length" : length,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendVideoNote", data=data, files = files).json()
	
	def send_mediagroup_by_path(self, media, chat_id="", message_thread_id="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply=""): # TODO

		'''Use this method to send a group of photos, videos, documents or audios as an album. Documents and audio files can be only grouped in an album with messages of the same type. On success, an array of Messages that were sent is returned.
		
		- media : List[InputMediaAudio/InputMediaDocument/InputMediaPhoto/InputMediaVideo] -> A JSON-serialized array describing photos and videos to be sent, must include 2-10 items.
		- chat_id : int/str (optional) -> chat_id of the chat to send the media group to. The default one is the one specified by the profile.
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only.
		- disable_notification : bool (optional) -> Sends the messages in the group silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent messages from forwarding and saving.
		- reply_to_message_id : int (optional) -> If the messages are a reply, ID of the original message.
		- allow_sending_without_reply : bool (optional) -> Pass True if the messages should be sent even if the specified replied-to message is not found.
		
		Refer to https://core.telegram.org/bots/api (sendMediaGroup) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"media" : media,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
		}

		return self.__request_format("sendMediaGroup", data=data).json()
	
	def send_location(self, latitude, longitude, chat_id="", message_thread_id="", horizontal_accuracy="", live_period="", heading="", proximity_alert_radius="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send point on the map. On success, the sent Message is returned.
	
		- latitude : float -> Latitude of the location.
		- longitude : float -> Longitude of the location.
		- chat_id : int/str (optional) -> chat_id of the chat to send the location to. The default one is the one specified by the profile.
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only.
		- horizontal_accuracy : float (optional) -> The radius of uncertainty for the location, measured in meters; 0-1500.
		- live_period : int (optional) -> Period in seconds for which the location will be updated, should be between 60 and 86400.
		- heading : int (optional) -> For live locations, a direction in which the user is moving, in degrees. Must be between 1 and 360 if specified.
		- proximity_alert_radius : int (optional) -> For live locations, a maximum distance for proximity alerts about approaching another chat member, in meters. Must be between 1 and 100000 if specified.
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving.
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message.
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found.
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove the reply keyboard, or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendLocation) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"latitude" : latitude,
			"longitude" : longitude,
			"horizontal_accuracy" : horizontal_accuracy,
			"live_period" : live_period,
			"heading" : heading,
			"proximity_alert_radius" : proximity_alert_radius,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendLocation", data=data).json()
	
	def send_venue(self, latitude, longitude, title, address, chat_id="", message_thread_id="", foursquare_id="", foursquare_type="", google_place_id="", google_place_type="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send information about a venue. On success, the sent Message is returned.
		
		- latitude : float -> Latitude of the venue.
		- longitude : float -> Longitude of the venue.
		- title : str -> Name of the venue.
		- address : str -> Address of the venue.
		- chat_id : int/str (optional) -> chat_id of the chat to send the venue to. The default one is the one specified by the profile.
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only.
		- foursquare_id : str (optional) -> Foursquare identifier of the venue, if known.
		- foursquare_type : str (optional) -> Foursquare type of the venue, if known.
		- google_place_id : str (optional) -> Google Places identifier of the venue.
		- google_place_type : str (optional) -> Google Places type of the venue.
		- disable_notification : bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving.
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message.
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found.
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove the reply keyboard, or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendVenue) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"latitude" : latitude,
			"longitude" : longitude,
			"title" : title,
			"address" : address,
			"foursquare_id" : foursquare_id,
			"foursquare_type" : foursquare_type,
			"google_place_id" : google_place_id,
			"google_place_type" : google_place_type,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendVenue", data=data).json()
	
	def send_contact(self, phone_number, first_name, chat_id="", message_thread_id="", last_name="", vcard="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send phone contacts. On success, the sent Message is returned.
	
		- phone_number: str -> Contact's phone number.
		- first_name: str -> Contact's first name.
		- chat_id: int/str (optional) -> Chat ID of the chat to send the contact to. The default one is the one specified by the profile.
		- message_thread_id: int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only.
		- last_name: str (optional) -> Contact's last name.
		- vcard: str (optional) -> Additional data about the contact in the form of a vCard.
		- disable_notification: bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content: bool (optional) -> Protects the contents of the sent message from forwarding and saving.
		- reply_to_message_id: int (optional) -> If the message is a reply, ID of the original message.
		- allow_sending_without_reply: bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found.
		- reply_markup: see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard, or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendContact) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"phone_number" : phone_number,
			"first_name" : first_name,
			"last_name" : last_name,
			"vcard" : vcard,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendContact", data=data).json()
	
	def send_poll(self, question, options, chat_id="", message_thread_id="", is_anonymous="", type="", allows_multiple_answers="", correct_option_id="", explanation="", explanation_parse_mode="", explanation_entities="", open_period="", close_date="", is_closed="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send a native poll. On success, the sent Message is returned.
	
		- question: str -> Poll question.
		- options: List[str] -> List of answer options.
		- chat_id: int/str (optional) -> Chat ID of the chat to send the poll to. The default one is the one specified by the profile.
		- message_thread_id: int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only.
		- is_anonymous: bool (optional) -> True, if the poll needs to be anonymous.
		- type: str (optional) -> Poll type, e.g., "quiz".
		- allows_multiple_answers: bool (optional) -> Allows multiple answers if True.
		- correct_option_id: int (optional) -> ID of the correct answer for quizzes.
		- explanation: str (optional) -> Explanation for the correct answer.
		- explanation_parse_mode: str (optional) -> Mode for parsing entities in the explanation.
		- explanation_entities: List[MessageEntity] (optional) -> Special entities in the explanation.
		- open_period: int (optional) -> Time in seconds for which the poll will be active.
		- close_date: int (optional) -> UNIX timestamp for the poll's closing date.
		- is_closed: bool (optional) -> Closes the poll if True.
		- disable_notification: bool (optional) -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content: bool (optional) -> Protects the contents of the sent message from forwarding and saving.
		- reply_to_message_id: int (optional) -> If the message is a reply, ID of the original message.
		- allow_sending_without_reply: bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found.
		- reply_markup: see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard, or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendPoll) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"question" : question,
			"options" : json.dumps(options),
			"is_anonymous" : is_anonymous,
			"type" : type,
			"allows_multiple_answers" : allows_multiple_answers,
			"correct_option_id" : correct_option_id,
			"explanation" : explanation,
			"explanation_parse_mode" : explanation_parse_mode,
			"explanation_entities" : json.dumps(explanation_entities),
			"open_period" : open_period,
			"close_date" : close_date,
			"is_closed" : is_closed,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendPoll", data=data).json()
	
	def send_dice(self, chat_id="", message_thread_id="", emoji="", disable_notification="", protect_content="", reply_to_message_id="", allow_sending_without_reply="", reply_markup=""):

		'''Use this method to send an animated emoji that will display a random value. On success, the sent Message is returned.
	
		- chat_id : int/str (optional) -> Chat ID of the chat to send the dice to. The default one is the one specified by the profile.
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only.
		- emoji : str (optional) -> Emoji symbolizing the dice throw animation (see the site).
		- disable_notification : bool -> Sends the message silently. Users will receive a notification with no sound.
		- protect_content : bool (optional) -> Protects the contents of the sent message from forwarding and saving.
		- reply_to_message_id : int (optional) -> If the message is a reply, ID of the original message.
		- allow_sending_without_reply : bool (optional) -> Pass True if the message should be sent even if the specified replied-to message is not found.
		- reply_markup : see the site (optional) -> Additional interface options. A JSON-serialized object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard, or to force a reply from the user.
		
		Refer to https://core.telegram.org/bots/api (sendDice) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a to_chat_id in the profile or specify one as a parameter.")
		if disable_notification == "":
			disable_notification = self.__profile["disable_notification"]
		if protect_content == "":
			protect_content = self.__profile["protect_content"]
		if allow_sending_without_reply == "":
			allow_sending_without_reply = self.__profile["allow_sending_without_reply"]

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"emoji" : emoji,
			"disable_notification" : disable_notification,
			"protect_content" : protect_content,
			"reply_to_message_id" : reply_to_message_id,
			"allow_sending_without_reply" : allow_sending_without_reply,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("sendDice", data=data).json()
	
	def send_chataction(self, action, chat_id="", message_thread_id=""):

		'''Use this method when you need to tell the user that something is happening on the bot's side. The status is set for 5 seconds or less (when a message arrives from your bot, Telegram clients clear its typing status). Returns True on success.
	
		We only recommend using this method when a response from the bot will take a noticeable amount of time to arrive.
		
		- action : str -> Type of action to broadcast. Choose one, depending on what the user is about to receive: typing for text messages, upload_photo for photos, record_video or upload_video for videos, record_voice or upload_voice for voice notes, upload_document for general files, choose_sticker for stickers, find_location for location data, record_video_note or upload_video_note for video notes.
		- chat_id : int/str (optional) -> Chat ID of the chat to send the chat action to. The default one is the one specified by the profile.
		- message_thread_id : int (optional) -> Unique identifier for the target message thread (topic) of the forum; for forum supergroups only.
		
		Refer to https://core.telegram.org/bots/api (sendChatAction) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a chat_id in the profile or specify one as a parameter.")

		data={
			"chat_id" : chat_id,
			"message_thread_id" : message_thread_id,
			"action" : action,
		}

		return self.__request_format("sendChatAction", data=data).json()
	
	def edit_message_text(self, text, chat_id="", message_id="", inline_message_id="", parse_mode="", entities="", disable_web_page_preview="", reply_markup=""):

		'''Use this method to edit text and game messages. On success, if the edited message is not an inline message, the edited Message is returned, otherwise True is returned.
	
		- text : str -> New text of the message, 1-4096 characters after entities parsing
		- chat_id : int/str (limited) -> Required if inline_message_id is not specified. Unique identifier for the target chat or username of the target channel (if not defined looks for the default one)
		- message_id : int (limited) -> Required if inline_message_id is not specified. Identifier of the message to edit
		- inline_message_id : str (limited) -> Required if chat_id and message_id are not specified. Identifier of the inline message
		- parse_mode : str (optional) -> Mode for parsing entities in the message text. See the site for more details.
		- entities : List[MessageEntity] (optional) -> A JSON-serialized list of special entities that appear in message text, which can be specified instead of parse_mode
		- disable_web_page_preview : bool (optional) -> Disables link previews for links in this message
		- reply_markup : InlineKeyboardMarkup (optional) -> A JSON-serialized object for a new message inline keyboard.
		
		Refer to https://core.telegram.org/bots/api (editMessageText) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if inline_message_id == "":
			if chat_id == "":
				chat_id = self.__profile["to_chat_id"]
			if message_id == "" or chat_id == "":
				raise Exception("EXCEPTION: If the inline_message_id is not defined, both chat_id (default counts) and message_id must be defined.")
		else:
			chat_id = ""
			message_id = ""
		if disable_web_page_preview == "":
			disable_web_page_preview = self.__profile["disable_web_page_preview"]
		if parse_mode == "":
			parse_mode = self.__profile["parse_mode"]

		data={
			"chat_id" : chat_id,
			"message_id" : message_id,
			"inline_message_id" : inline_message_id,
			"text" : text,
			"parse_mode" : parse_mode,
			"entities" : json.dumps(entities),
			"disable_web_page_preview" : disable_web_page_preview,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("editMessageText", data=data).json()
	
	def edit_message_caption(self, caption, chat_id="", message_id="", inline_message_id="", parse_mode="", caption_entities="", reply_markup=""):

		'''Use this method to edit captions of messages. On success, if the edited message is not an inline message, the edited Message is returned, otherwise True is returned.
		
		- caption : str -> New caption of the message, 0-1024 characters after entities parsing
		- chat_id : int/str (limited) -> Required if inline_message_id is not specified. Unique identifier for the target chat or username of the target channel (if not defined looks for the default one)
		- message_id : int (limited) -> Required if inline_message_id is not specified. Identifier of the message to edit
		- inline_message_id : str (limited) -> Required if chat_id and message_id are not specified. Identifier of the inline message
		- parse_mode : str (optional) -> Mode for parsing entities in the message caption. See the site for more details.
		- caption_entities : List[MessageEntity] (optional) -> A JSON-serialized list of special entities that appear in the caption, which can be specified instead of parse_mode
		- disable_web_page_preview : bool (optional) -> Disables link previews for links in this message
		- reply_markup : InlineKeyboardMarkup (optional) -> A JSON-serialized object for a new message inline keyboard.
		
		Refer to https://core.telegram.org/bots/api (editMessageCaption) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if inline_message_id == "":
			if chat_id == "":
				chat_id = self.__profile["to_chat_id"]
			if message_id == "" or chat_id == "":
				raise Exception("EXCEPTION: If the inline_message_id is not defined, both chat_id (default counts) and message_id must be defined.")
		else:
			chat_id = ""
			message_id =""
		if parse_mode == "":
			parse_mode = self.__profile["parse_mode"]

		data={
			"chat_id" : chat_id,
			"message_id" : message_id,
			"inline_message_id" : inline_message_id,
			"caption" : caption,
			"parse_mode" : parse_mode,
			"caption_entities" : json.dumps(caption_entities),
			"reply_markup" : reply_markup,
		}

		return self.__request_format("editMessageCaption", data=data).json()
	
	def edit_message_media(self, file_path, chat_id="", message_id="", inline_message_id="", reply_markup=""):

		'''Use this method to edit animation, audio, document, photo, or video messages. If a message is part of a message album, then it can be edited only to an audio for audio albums, only to a document for document albums and to a photo or a video otherwise. When an inline message is edited, a new file can't be uploaded; use a previously uploaded file via its file_id or specify a URL. On success, if the edited message is not an inline message, the edited Message is returned, otherwise True is returned.
	
		- file_path : str -> The path to the media to send
		- chat_id : int/str (limited) -> Required if inline_message_id is not specified. Unique identifier for the target chat or username of the target channel (if not defined looks for the default one)
		- message_id : int (limited) -> Required if inline_message_id is not specified. Identifier of the message to edit
		- inline_message_id : str (limited) -> Required if chat_id and message_id are not specified. Identifier of the inline message
		- reply_markup : InlineKeyboardMarkup (optional) -> A JSON-serialized object for a new message inline keyboard.
		
		Refer to https://core.telegram.org/bots/api (editMessageMedia) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if inline_message_id == "":
			if chat_id == "":
				chat_id = self.__profile["to_chat_id"]
			if message_id == "" or chat_id == "":
				raise Exception("EXCEPTION: If the inline_message_id is not defined, both chat_id (default counts) and message_id must be defined.")
		else:
			chat_id = ""
			message_id =""

		if not os.path.exists(file_path):
			raise Exception(f"EXCEPTION: The file_path {file_path} doesn't lead to any file.")
		files = {"media" : open(file_path, "rb")}

		data={
			"chat_id" : chat_id,
			"message_id" : message_id,
			"inline_message_id" : inline_message_id,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("editMessageMedia", data=data, files=files).json()
	
	def edit_message_live_location(self, latitude, longitude, chat_id="", message_id="", inline_message_id="", horizontal_accuracy="", heading="", proximity_alert_radius="", reply_markup=""):

		'''Use this method to edit live location messages. A location can be edited until its live_period expires or editing is explicitly disabled by a call to stopMessageLiveLocation. On success, if the edited message is not an inline message, the edited Message is returned, otherwise True is returned.
	
		- latitude : float -> Latitude of new location
		- longitude : float -> Longitude of new location
		- chat_id : int/str (limited) -> Required if inline_message_id is not specified. Unique identifier for the target chat or username of the target channel (if not defined looks for the default one)
		- message_id : int (limited) -> Required if inline_message_id is not specified. Identifier of the message to edit
		- inline_message_id : str (limited) -> Required if chat_id and message_id are not specified. Identifier of the inline message
		- horizontal_accuracy : float (optional) -> The radius of uncertainty for the location, measured in meters; 0-1500
		- heading : int (optional) -> Direction in which the user is moving, in degrees. Must be between 1 and 360 if specified.
		- proximity_alert_radius : int (optional) -> The maximum distance for proximity alerts about approaching another chat member, in meters. Must be between 1 and 100000 if specified.
		- reply_markup : InlineKeyboardMarkup (optional) -> A JSON-serialized object for a new message inline keyboard.
		
		Refer to https://core.telegram.org/bots/api (editMessageLiveLocation) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if inline_message_id == "":
			if chat_id == "":
				chat_id = self.__profile["to_chat_id"]
			if message_id == "" or chat_id == "":
				raise Exception("EXCEPTION: If the inline_message_id is not defined, both chat_id (default counts) and message_id must be defined.")
		else:
			chat_id = ""
			message_id =""

		data={
			"chat_id" : chat_id,
			"message_id" : message_id,
			"inline_message_id" : inline_message_id,
			"latitude" : latitude,
			"longitude" : longitude,
			"horizontal_accuracy" : horizontal_accuracy,
			"heading" : heading,
			"proximity_alert_radius" : proximity_alert_radius,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("editMessageLiveLocation", data=data).json()

	def stop_message_live_location(self, chat_id="", message_id="", inline_message_id="", reply_markup=""):

		'''Use this method to stop updating a live location message before live_period expires. On success, if the message is not an inline message, the edited Message is returned, otherwise True is returned.

		- chat_id : int/str (limited) -> Required if inline_message_id is not specified. Unique identifier for the target chat or username of the target channel (if not defined looks for the default one)
		- message_id : int (limited) -> Required if inline_message_id is not specified. Identifier of the message to edit
		- inline_message_id : str (limited) -> Required if chat_id and message_id are not specified. Identifier of the inline message
		- reply_markup : InlineKeyboardMarkup (optional) -> A JSON-serialized object for a new message inline keyboard.

		Refer to https://core.telegram.org/bots/api (stopMessageLiveLocation) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if inline_message_id == "":
			if chat_id == "":
				chat_id = self.__profile["to_chat_id"]
			if message_id == "" or chat_id == "":
				raise Exception("EXCEPTION: If the inline_message_id is not defined, both chat_id (default counts) and message_id must be defined.")
		else:
			chat_id = ""
			message_id =""

		data={
			"chat_id" : chat_id,
			"message_id" : message_id,
			"inline_message_id" : inline_message_id,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("stopMessageLiveLocation", data=data).json()

	def edit_message_reply_markup(self, chat_id="", message_id="", inline_message_id="", reply_markup=""):

		'''Use this method to edit only the reply markup of messages. On success, if the edited message is not an inline message, the edited Message is returned, otherwise True is returned.

		- chat_id : int/str (limited) -> Required if inline_message_id is not specified. Unique identifier for the target chat or username of the target channel (if not defined looks for the default one)
		- message_id : int (limited) -> Required if inline_message_id is not specified. Identifier of the message to edit
		- inline_message_id : str (limited) -> Required if chat_id and message_id are not specified. Identifier of the inline message
		- reply_markup : InlineKeyboardMarkup (optional) -> A JSON-serialized object for a new message inline keyboard.

		Refer to https://core.telegram.org/bots/api (stopMessageLiveLocation) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if inline_message_id == "":
			if chat_id == "":
				chat_id = self.__profile["to_chat_id"]
			if message_id == "" or chat_id == "":
				raise Exception("EXCEPTION: If the inline_message_id is not defined, both chat_id (default counts) and message_id must be defined.")
		else:
			chat_id = ""
			message_id =""

		data={
			"chat_id" : chat_id,
			"message_id" : message_id,
			"inline_message_id" : inline_message_id,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("editMessageReplyMarkup", data=data).json()

	def stop_poll(self, message_id, chat_id="", reply_markup=""):

		'''Use this method to stop a poll which was sent by the bot. On success, the stopped Poll is returned.
		
		- message_id : int -> Identifier of the original message with the poll
		- chat_id : int/str (optional) -> Unique identifier for the target chat or username of the target channel (if not defined looks for the default one)
		- reply_markup : InlineKeyboardMarkup (optional) -> A JSON-serialized object for a new message inline keyboard.

		Refer to https://core.telegram.org/bots/api (stopPoll) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a chat_id in the profile or specify one as a parameter.")

		data={
			"chat_id" : chat_id,
			"message_id" : message_id,
			"reply_markup" : reply_markup,
		}

		return self.__request_format("stopPoll", data=data).json()

	def delete_message(self, message_id, chat_id=""):

		'''Use this method to delete a message, including service messages, with the following limitations:
		- A message can only be deleted if it was sent less than 48 hours ago.
		- Service messages about a supergroup, channel, or forum topic creation can't be deleted.
		- A dice message in a private chat can only be deleted if it was sent more than 24 hours ago.
		- Bots can delete outgoing messages in private chats, groups, and supergroups.
		- Bots can delete incoming messages in private chats.
		- Bots granted can_post_messages permissions can delete outgoing messages in channels.
		- If the bot is an administrator of a group, it can delete any message there.
		- If the bot has can_delete_messages permission in a supergroup or a channel, it can delete any message there.
		Returns True on success.

		- message_id : int -> Identifier of the message to delete
		- chat_id : int/str (optional) -> Unique identifier for the target chat or username of the target channel (if not defined looks for the default one)
		
		Refer to https://core.telegram.org/bots/api (deleteMessage) for more info'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")
		if not self.__send: return {}

		if chat_id == "":
			chat_id = self.__profile["to_chat_id"]
		if chat_id == "":
			raise Exception("EXCEPTION: Either set a chat_id in the profile or specify one as a parameter.")

		data={
			"chat_id" : chat_id,
			"message_id" : message_id,
		}

		return self.__request_format("deleteMessage", data=data).json()

	def __request_format(self, command, data={}, files=None):

		'''Creates a request to the telegram API and returns the response
	
		- command : str -> the command to use
		- data : str -> the data to pass through'''

		if not self.__env: raise Exception("EXCEPTION: constructor hasn't been called yet.")

		url = self.__def_url + "/" + command;

		return requests.post(url, data=data, files=files)
	
	#endregion