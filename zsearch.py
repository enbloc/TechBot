#!/usr/bin/python
"""
zsearch.py
Written by Gabriel Miller
6/27/2016

"""
from zdesk import Zendesk
import stopwords

def z_search(query):

	# Connect to Zendesk API
	testconfig = {
	    'zdesk_email': 'gmiller@mdsol.com',
	    'zdesk_password': '8v1eHaF72wyHSGCTLc1e6uSXgHvIypRNdXxmKeFC',
	    'zdesk_url': 'https://mdsol.zendesk.com',
	    'zdesk_token': True
	    }

	zendesk = Zendesk(**testconfig)

	# Initialize list
	results_list = []

	# Direct query phrase search
	search_results = zendesk.help_center_articles_search(query=query)
	articles = search_results['results']

	idx1 = 0
	for article in articles:
		results_list.append(articles[idx1])
		idx1 += 1
		if len(results_list) >= 3:
			break

	print "Number of results after direct phrase search: " + str(len(results_list))

	# Remove unnecessary words from query and re-search direct phrase
	if len(results_list) < 3:

		sw = stopwords.filterable
		parsed_query = filter(lambda w: not w in sw, query.split())
		parsed_query_joined = ' '.join(parsed_query)

		search_results = zendesk.help_center_articles_search(query=parsed_query_joined)
		articles = search_results['results']

		idx1 = 0
		for article in articles:
			if articles[idx1] not in results_list:
				results_list.append(articles[idx1])
				idx1 += 1
				if len(results_list) >= 3:
					break

	print "Number of results after SW cleared direct phrase search: " + str(len(results_list))

	# Search word-by-word for results from stopword-cleared phrase
	if len(results_list) < 3:

		for keyword in parsed_query:
			search_results = zendesk.help_center_articles_search(query=keyword)
			articles = search_results['results']

			idx1 = 0
			for article in articles:
				if articles[idx1] not in results_list:
					results_list.append(articles[idx1])
					idx1 += 1
					if len(results_list) >= 3:
						break

	print "Number of results after word-by-word search: " + str(len(results_list))

	######################################################################
	# This section conducts a lemmatized version of the word-by-word     #
	# search. Implementation TBD.                                        #
	######################################################################

	# Lemmatize and search word-by-word from stopword-cleared phrase
	#if len(results_list) < 3:
	#
	#	import nltk
    #	from nltk.stem.wordnet import WordNetLemmatizer
	#
	#	nltk.data.path.append('C:/Users/gabri/Desktop/techbot-dir')
	#	lm = WordNetLemmatizer()
	#
	#	for keyword in parsed_query:
	#		lemmed_keyword = lm.lemmatize(keyword)
	#		search_results = zendesk.help_center_articles_search(query=lemmed_keyword)
	#		articles = search_results['results']
	#
	#		idx1 = 0
	#		for article in articles:
	#			if articles[idx1] not in results_list:
	#				results_list.append(articles[idx1])
	#				idx1 += 1
	#				if len(results_list) >= 3:
	#					break
	#
	#print "Number of results after lemmatized word-by-word search: " + str(len(results_list))	

	return results_list
