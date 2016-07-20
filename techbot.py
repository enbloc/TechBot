#!/usr/bin/python
"""
techbot.py
Written by Gabriel Miller
6/27/2016

"""
from newhire import new_hire_sequence
from zsearch import z_search
from zdesk import Zendesk
from pb_py import main as API
import sys
import pymysql
import logging
import stopwords
import re

rds_host = "mysql-techbot.cbfsapoi83vi.us-west-2.rds.amazonaws.com"
rds_port = 3306
rds_name = "gmiller"
rds_pass = "NEWfound0534"
rds_db_name = "techbot_logs"
host = 'aiaas.pandorabots.com'

def zdesk_connect():

    testconfig = {
    'zdesk_email': 'gmiller@mdsol.com',
    'zdesk_password': '8v1eHaF72wyHSGCTLc1e6uSXgHvIypRNdXxmKeFC',
    'zdesk_url': 'https://mdsol.zendesk.com',
    'zdesk_token': True
    }

    zendesk = Zendesk(**testconfig)
    return zendesk

def zdesk_sandbox_connect():

    testconfig = {
    'zdesk_email': 'gmiller@mdsol.com',
    'zdesk_password': 'vmOkiMX0G8KBdiDx3fJoXvvUaUsUopFPjnHcwBHs',
    'zdesk_url': 'https://mdsol1466012404.zendesk.com',
    'zdesk_token': True
    }

    zendesk = Zendesk(**testconfig)
    return zendesk

def zdesk_search(zen_obj, query):

    # Remove unnecessary words from query
    sw = stopwords.filterable
    parsed_query = filter(lambda w: not w in sw, query.split())
    parsed_query_joined = ' '.join(parsed_query)
    search_results = zen_obj.help_center_articles_search(query=parsed_query_joined)
    articles = search_results['results']

    try:
        return "So are you having issues with " + articles[0]['title'].lower() + "?"
    except IndexError:
        return "Hm, I can't seem to find anything..."

def zdesk_sandbox_create_ticket(subject, description):

    zdesk_sandbox = zdesk_sandbox_connect()

    # Create
    new_ticket = {
        'ticket': {
            'requester_name': 'John Doe',
            'requester_email': 'jdoe@mdsol.com',
            'subject': subject,
            'description': description,
            'tags': ['problem', 'issues'],
            'ticket_field_entries': [
                {
                    'ticket_field_id': 1,
                    'value': 'Something1'
                },
                {
                    'ticket_field_id': 2,
                    'value': '$10'
                }
            ]
        }
    }

    result = zdesk_sandbox.ticket_create(data=new_ticket)

    # Alternatively, you can get the complete response and get the location
    # yourself. This can be useful for getting other response items that are
    # not normally returned, such as result['content']['upload']['token']
    # when using zendesk.upload_create()
    #
    # result = zendesk.ticket_create(data=new_ticket, complete_response=True)
    # ticket_url = result['response']['location']
    # ticket_id = get_id_from_url(ticket_url)

    # Need ticket ID?
    from zdesk import get_id_from_url
    ticket_id = get_id_from_url(result)

    return ticket_id


def message_bot(input):
    user_key = '99daf0495907c54b7e8fe16efbcfc7e7'
    app_id = '1409612772625'
    botname = 'testtechbot'
    input_text = input
    bot_session_id = '1'
    reply = API.talk(user_key, app_id, host, botname, input_text, bot_session_id, recent=True)
    return reply['response']

def session_handler(input, session_id):
    
    # Set up Zendesk object
    zen_obj = zdesk_connect()
    zen_sbx_obj = zdesk_sandbox_connect()

    # Set up logging for testing 
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Connect to Amazon RDS Instance
    try:
        server_address = (rds_host, rds_port)
        conn = pymysql.connect(rds_host, user=rds_name, passwd=rds_pass, db=rds_db_name, connect_timeout=5)
    except:
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
        sys.exit()

    logger.info("SUCCESS: Connection to RDS mysql instance succeeded")



    with conn.cursor() as cur:

        """
        INITIAL DB SETUP

        Check to see if a session already exists with the given session ID,
        and if not, create a session as a table and initialize it.

        """
        # Check to see if session table already exists
        cur.execute("SHOW TABLES LIKE 'Session" + session_id + "'")
        result = cur.fetchone()

        if result:

            # Dump contents of session to log for testing
            cur.execute('SELECT * FROM Session' + session_id)
            rows = cur.fetchall()

            for row in rows:
                logger.info(row)

            # If table does exist, get the most recent message and its properties sent from bot for context
            cur.execute('SELECT Message FROM Session'        + session_id + ' WHERE Sender = 0 ORDER BY ID DESC LIMIT 1')
            last_message = str(cur.fetchone()[0])
            cur.execute('SELECT MessageType FROM Session'    + session_id + ' WHERE Sender = 0 ORDER BY ID DESC LIMIT 1')
            last_message_type = str(cur.fetchone()[0])
            cur.execute('SELECT ResponseNumber FROM Session' + session_id + ' WHERE Sender = 0 ORDER BY ID DESC LIMIT 1')
            last_message_responsenum = str(cur.fetchone()[0])
            logger.info("last_message = "             + last_message)
            logger.info("last_message_type = "        + last_message_type)
            logger.info("last_message_responsenum = " + last_message_responsenum)

        else:
            # If no table exists, create one with session_id and insert default "BOT_INTRO" message
            cur.execute("CREATE TABLE Session" + session_id + " (ID int NOT NULL AUTO_INCREMENT, Message varchar(1024) NOT NULL, MessageType varchar(255) NOT NULL, Sender int NOT NULL, ResponseNumber int, PRIMARY KEY (ID))")  
            cur.execute('INSERT INTO  Session' + session_id + ' (ID, Message, MessageType, Sender, ResponseNumber) VALUES (NULL, "BOT_INTRO", "INTRO", 0, NULL)')
            logger.info("Session created and inserted for Session" + session_id)
            last_message = "BOT_INTRO"
            last_message_type = "INTRO"
            last_message_responsenum = 0
            conn.commit()

        logger.info(last_message)


        """
        MAIN PARSING SEQUENCE

        Use the received user input, plus the most recent message
        sent from the bot (for context) in order to determine what
        the next message should be and what needs to be called.

        """

        ##########################
        # FIRST MESSAGE RESPONSE #
        ##########################
        if last_message_type == "INTRO"      or  \
           last_message_type == "PB_BANTER"  or  \
           last_message_type == "GEN_ERROR"  or  \
           last_message_type == "TS_SUCCESS" or  \
           last_message_type == "TIX_SUBMIT" or  \
           last_message_type == "TIX_REJECT":

            # Do a standard query based on keywords
            if "I need help with" in input:
                #
                # FIX SEARCH HERE
                #
                message = zdesk_search(zen_obj, input.replace("I need help with ", ""))
                message_type = "TS_PROMPT"
                message_response_num = 1
                input_type = "QUERY"

            # Respond to Trouleshooting button 
            elif "TS_BUTTON_PRESS" in input:
                message = "Okay, what seems to be the problem?"
                message_type = "TS_BUTTON_PROMPT"
                message_response_num = 0
                input_type = "TS_BUTTON_PRESS"

            # Respond to New Hire button
            elif "NH_BUTTON_PRESS" in input:
                message_data = new_hire_sequence(message_type="NH_RESPONSE", response_num=1)
                message =              message_data[0]
                message_type =         message_data[1]
                message_response_num = message_data[2]
                input_type =           message_data[3]

            else:
                # General banter response
                message = message_bot(input)
                message_type = "PB_BANTER"
                message_response_num = 0
                input_type = "PB_BANTER"

        ############################
        # NEW HIRE PROMPT RESPONSE #
        ############################
        elif last_message_type == "NH_RESPONSE" or \
             last_message_type == "NH_FORM_REJECT":

            if "NH_BUTTON_PRESS" in input:
                message_data = new_hire_sequence(message_type="NH_RESPONSE", response_num=1)
                message =              message_data[0]
                message_type =         message_data[1]
                message_response_num = message_data[2]
                input_type =           message_data[3]

            else:
                message_data = new_hire_sequence(message_type=last_message_type, response_num=int(last_message_responsenum))
                message =              message_data[0]
                message_type =         message_data[1]
                message_response_num = message_data[2]
                input_type =           message_data[3]

        ###################################
        # TROUBLESHOOTING BUTTON RESPONSE #
        ###################################
        elif last_message_type == "TS_BUTTON_PROMPT":

            # Check for multiple button presses
            if "TS_BUTTON_PRESS" in input:
                message = "What is the issue you would like to troubleshoot?"
                message_type = "TS_BUTTON_PROMPT"
                message_response_num = 0
                input_type = "TS_BUTTON_PRESS"

            else:
                results_list = z_search(input)
                input_type = "QUERY"
                try:
                    # Attempt to grab the next article title for prompt
                    message = "So are you having issues with " + results_list[0]['title'].lower() + "?"
                    message_type = "TS_PROMPT"
                    message_response_num = 1
                except IndexError:
                    # Failed attempt at grabbing article body
                    message = "Hm, I can't seem to find anything. Would you like me to open a Zendesk ticket for you?"
                    message_type = "TS_EMPTY"
                    message_response_num = 0


        ###################################
        # TROUBLESHOOTING PROMPT RESPONSE #
        ###################################
        elif last_message_type == "TS_PROMPT" or \
             last_message_type == "TS_PROMPT_REJECT":

            # Set up and run Zendesk article query
            cur.execute('SELECT Message FROM Session' + session_id + ' WHERE Sender = 1 AND MessageType = "QUERY" ORDER BY ID DESC LIMIT 1')
            last_user_query = str(cur.fetchone()[0]).replace("I need help with ", "")

            results_list = z_search(last_user_query)

            logger.info("Results based on query: " + last_user_query)
            for article in results_list:
                logger.info(article['title'])

            #################
            # YES TO PROMPT #
            #################
            if input in stopwords.affirmative:

                # Log the answer
                logger.info("input contains 'yes'")
                input_type = "CONFIRM"

                # Determine the next result to be called from query
                result_num = int(last_message_responsenum) - 1

                try:
                    # Attempt to grab the article body
                    message = "See if these steps work for you:\n\n" + results_list[result_num]['body'] + "\n\nDid this solve your problem?"
                    message_type = "TS_GUIDE"
                    message_response_num = last_message_responsenum
                    logger.info("Article body response: " + message)
                except IndexError:
                    # Failed attempt at grabbing article body
                    message = "Hm, I can't seem to find anything. Would you like me to open a Zendesk ticket for you?"
                    message_type = "TS_EMPTY"
                    message_response_num = 0
                    logger.info("Couldn't find anything in Zendesk for body search...")

            ################
            # NO TO PROMPT #
            ################
            elif input in stopwords.negative:

                # Log the answer
                logger.info("input contains 'no'")
                input_type = "DENY"

                # Determine the next result to be called from query
                result_num = int(last_message_responsenum)

                try:
                    # Attempt to grab the next article title for prompt
                    message = "So are you having issues with " + results_list[result_num]['title'].lower() + "?"
                    message_type = "TS_PROMPT"
                    message_response_num = int(last_message_responsenum) + 1
                except IndexError:
                    # Failed attempt at grabbing article body
                    message = "Hm, I can't seem to find anything. Would you like me to open a Zendesk ticket for you?"
                    message_type = "TS_EMPTY"
                    message_response_num = 0

            ##################
            # ANSWER UNCLEAR #
            ##################
            else:
                message = "Sorry, I'm going to need a yes or no answer for this one."
                message_type = "TS_PROMPT_REJECT"
                message_response_num = int(last_message_responsenum)
                input_type = "NOISE"

        ##################################
        # TROUBLESHOOTING GUIDE RESPONSE #
        ##################################
        elif last_message_type == "TS_GUIDE" or \
             last_message_type == "TS_GUIDE_REJECT":

            if input in stopwords.affirmative:
                message = "Great! Glad I could help!"
                message_type = "TS_SUCCESS"
                message_response_num = 0
                input_type = "CONFIRM"

            elif input in stopwords.negative:
                message = "That's unfortunate! Would you like me to open a Zendesk ticket for you?"
                message_type = "TS_FAIL"
                message_response_num = 0
                input_type = "DENY"

            else:
                message = "Sorry, was that a yes or a no?"
                message_type = "TS_GUIDE_REJECT"
                message_response_num = int(last_message_responsenum)
                input_type = "NOISE"

        ##################################
        # ZENDESK TICKET PROMPT RESPONSE #
        ##################################
        elif last_message_type == "TS_FAIL" or \
             last_message_type == "TS_EMPTY" or \
             last_message_type == "TIX_REJECT":

            #################
            # OPEN A TICKET #
            #################
            if input in stopwords.affirmative:

                # Pull the last user query
                cur.execute('SELECT Message FROM Session' + session_id + ' WHERE Sender = 1 AND MessageType = "QUERY" ORDER BY ID DESC LIMIT 1')
                last_user_query = str(cur.fetchone()[0]).replace("I need help with ", "")

                # Pull entire conversation log for ticket description
                cur.execute('SELECT Message, Sender FROM Session' + session_id)
                convo_log = cur.fetchall()

                # Set up ticket information and create ticket
                ticket_subject = "TechBot Ticket: " + last_user_query

                # Set up description text
                log_string = "Conversation Log: " + "\n\n"
                for (msg, sndr) in convo_log:
                    if msg != "BOT_INTRO" and msg != "TS_BUTTON_PRESS":
                        if sndr == 0:
                            log_string += "TECHBOT: " + msg + "\n"
                        else:
                            log_string += "USER: " + msg + "\n"

                # Parse the conversation log text to remove tags and format
                log_string_decoded  = log_string.decode('utf-8', 'replace')
                log_string_polished = log_string_decoded.replace("<br />", "\n")
                log_string_final    = re.sub('<[^<]+?>', '', log_string_polished)

                ticket_id = zdesk_sandbox_create_ticket(subject=ticket_subject, description=log_string_final)

                # Construct messages
                message = "Done! Your ticket has been submitted! Your ticket ID number is " + ticket_id + "."
                message_type = "TIX_SUBMIT"
                message_response_num = 0
                input_type = "CONFIRM"

            ######################
            # DO NOT OPEN TICKET #
            ######################
            elif input in stopwords.negative:
                message = "Ah, alright then. Is there anything else that I can help you with?"
                message_type = "TIX_REJECT"
                message_response_num = 0
                input_type = "DENY"

            ##################
            # ANSWER UNLCEAR #
            ##################
            else:
                message = "Sorry, was that a yes or a no?"
                message_type = "TIX_REJECT"
                message_response_num = 0
                input_type = "NOISE"

        ###########################
        # GENERAL CATCH-ALL ERROR #
        ###########################
        else:
            message = "Hm, seems like there has been some kind of error."
            message_type = "GEN_ERROR"
            message_response_num = 0
            input_type = "NOISE"
            logger.info("last_message contains neither BOT_INTRO or So you are having issues...")


        """
        CLEANUP AND LOGGING 

        """


        # Insert new dialog into RDS
        cur.execute("INSERT INTO  Session" + session_id + " (ID, Message, MessageType, Sender, ResponseNumber) VALUES (NULL, '" + input.replace("'", "") + "', '" + input_type.replace("'", "") + "', 1, NULL)")
        logger.info("Inserted " + input.replace("'", "") + "...")
        cur.execute("INSERT INTO  Session" + session_id + " (ID, Message, MessageType, Sender, ResponseNumber) VALUES (NULL, '" + message.replace("'", "") + "', '" + message_type.replace("'", "") + "', 0, '" + str(message_response_num) + "')")
        logger.info("Inserted " + message.replace("'", "") + "...")
        conn.commit()
        return message


def input_handler(event, context):
    input = event['input']
    s_id = event['session_id']
    z_connection = zdesk_connect()

    # Session handler test
    message = session_handler(input, s_id)
    return { 
        'message' : message,
         }