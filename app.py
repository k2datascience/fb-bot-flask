#Python libraries that we need to import for our bot
import os
from flask import Flask, request
from pymessenger.bot import Bot

app = Flask(__name__)
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
bot = Bot(ACCESS_TOKEN)

#We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)

    #if the request was not GET, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                query = message['message'].get('text')
                if query:
                    response_sent_text = get_message(query)
                    send_message(recipient_id, response_sent_text)
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a message to send to the user based on key words
def get_message(query):
    #simple rule-based response
    tuition_set = set('tuition', 'fees', 'cost')
    length_set = set('length', 'timing', 'duration', 'commitment')

    query_set = set(query.split())

    if query_set.intersection(tuition_set):
        response = "The program costs $6,000."
    elif query_set.intersection(length_set):
        response = """The program takes 4-12 months depending on your weekly time commitment.
                      Overall, the course takes 500-700 hours depending on your prior background."""
    else:
        response = "Sorry the bot does not understand your question. Please try a different one."

    # return message to user
    return response

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    app.run()
