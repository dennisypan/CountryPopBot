import os
import time
import re
from slackclient import SlackClient
import pandas as pd


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None



# ///////////// get data //////////////////////////////////////////////////////
dataset = pd.read_csv('CtrPopData2016.csv')

#sort countries by population size
result = dataset.sort_values('2016', ascending=False)

ctrarrayALL = []

for x in range(0, len(dataset["Country Code"])):
    ctrarrayALL.append(dataset.iloc[x]["Country Code"] + " = " + dataset.iloc[x]["Country Name"] + "\n")

COMMAND1 = "help"
COMMAND2 = "all countries"
MAXPOP = "country with largest population"
MINPOP = "country with smallest population"
AVGPOP = "average population"

COMMANDS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]	

# ///////////////////////////////////////////////////////////////////////////// 


# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM



MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *help* for a list of commands."

    # Finds and executes the given command, filling in response
    response = None

	
    # This is where you start to implement more commands!
	
	# Find country's population
    if command.startswith(command) and len(command) == 3:
        print(len(dataset['Country Code']))	
        xx = command + ""
        ctrz = dataset.loc[dataset['Country Code'] == xx]
        if (len(ctrz) != 0):
            response = "Country: " + ''.join(ctrz['Country Name'].values) + " / " + ''.join(ctrz['Country Code'].values) + "\n" + "Population: " + ''.join(str(int(ctrz['2016'].values)))
        else:
            response = "Sorry, either this country does not exist, or the command you entered is unrecognized.  Please enter *all countries* for a list of countries acronyms, or enter *help* for a list of commands."
	
    # display a list of commends that can be applied to the chatbot	
    if command.startswith(COMMAND1):
        starting = "*LIST OF COMMANDS:*" + "\n" 
        helpcmd = "(1) *help* = see a list of commands" + "\n" 
        ctrcmd = "(2) Enter a capital letter (e.g. *A*) for a list of countries and corresponding acronyms starting with the letter (e.g. *A*)" + "\n" 
        ctrallcmd = "(3) *all countries* = see a list of all countries and their acronyms" + "\n" 
        acronymcmd = "(4) Enter a country's acronym (e.g. *USA*) to get the country's 2016 population" + "\n"
        maxcmd = "(5) *country with largest population* = see country with biggest 2016 population" + "\n"
        mincmd = "(6) *country with smallest population* = see country with smallest 2016 population" + "\n"
        avgcmd = "(7) *average population* = see average country population for 2016" + "\n"
        response = starting + helpcmd + ctrcmd + ctrallcmd + acronymcmd + maxcmd + mincmd + avgcmd

    # list all the countries and their acronyms		
    if command.startswith(COMMAND2):
        response = ''.join(ctrarrayALL)
    
    # Display country with biggest population
    if command.startswith(MAXPOP):
        response = dataset['Country Name'][dataset['2016'].idxmax()] + " / " + dataset['Country Code'][dataset['2016'].idxmax()] + ": Population = " + str(dataset['2016'][dataset['2016'].idxmax()])

    # Display country with smallest population		
    if command.startswith(MINPOP):
        response = dataset['Country Name'][dataset['2016'].idxmin()] + " / " + dataset['Country Code'][dataset['2016'].idxmin()] + ": Population = " + str(dataset['2016'][dataset['2016'].idxmin()])

    # Display the 2016 average population (on the average, a country has x people in 2016) 		
    if command.startswith(AVGPOP):
        response = dataset['2016'].mean()
	
	# List all countries starting with a given letter (e.g. if user type "A", list all countries with acronyms starting with "A")
    if command.startswith(command) and len(command) == 1:
        arys = []
        for index, row in dataset.iterrows():
            if row['Country Code'].startswith(command): 
                arys.append(row['Country Code'] + ' = ' + row['Country Name'] + '\n')      
        response = ''.join(arys)
	
 
	

	
	# Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Country Population Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")