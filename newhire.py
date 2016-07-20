#!/usr/bin/python
"""
newhire.py
Written by Gabriel Miller
6/27/2016

"""

def new_hire_sequence(message_type, response_num):

	if message_type == "NH_RESPONSE":

		message_type = "NH_RESPONSE"
		input_type =   "NH_INPUT"

		# Name
		if response_num == 1:
			message = "What is the name of your new hire?"
			message_response_num = 2

        # Title
		elif response_num == 2:
			message = "What is the title of your new hire?"
			message_response_num = 3

        # Department
		elif response_num == 3:
			message = "Which department will your new hire be working in?"
			message_response_num = 4

        # Start date
		elif response_num == 4:
			message = "When will your new hire be starting? (mm/dd/yyyy format)"
			message_response_num = 5

        # Location
		elif response_num == 5:
			message = "At which office will your new hire be working?"
			message_response_num = 6

        # Contractor
		elif response_num == 6:
			message = "Are they a contractor?"
			message_response_num = 7

        # Re-hire?
		elif response_num == 7:
			message = "Are they a re-hire?"
			message_response_num = 8

        # Computer requested
		elif response_num == 8:
			message = "What kind of computer will they need?"
			message_response_num = 9

        # Other information
		elif response_num == 9:
			message = "Any other information that you want to provide?"
			message_response_num = 10

		elif response_num == 10:
			# Submit New Hire Ticket
			#create_new_hire_ticket()
			message = "Great, thanks for the info! Your ticket has been created."
			message_response_num = 0

		else:
			# Error handling
			message = "Error"
			message_response_num = 0


	return (message, message_type, message_response_num, input_type)

