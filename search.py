import sys
import pprint
import string
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
from googleapiclient.discovery import build

alpha = 1.0
beta = 1.0
gamma = 0.5

def get_query(api_key, engine_key, query):
    s = build("customsearch","v1",developerKey=api_key)
    res = s.cse().list(
        q=query,
        cx=engine_key
    ).execute()
    return res['items']

# Ignore this please :)
# def augment_query(query, relevant_articles):
#     if not relevant_articles:
#         return ""
#     inverted_index = {}
#     doc_id = 1
#     for article in relevant_articles:
#         current_index = {}
#         snippet = article['snippet'] + " " + article['title']
#         snippet = snippet.lower()
#         normalized = snippet.translate(str.maketrans('', '', string.punctuation))
#         tokens = normalized.split()
#         my_word_dict = {word:(tokens.count(word),doc_id) for word in set(tokens)}
#         for key in my_word_dict.keys():
#             if key in inverted_index:
#                 inverted_index[key].append(my_word_dict[key])
#             else:
#                 inverted_index[key] = [my_word_dict[key]]
    
#     pprint.pprint(inverted_index)
#     quit()


#     return query

def td_idf(relevant, irrelevant):
    cleaned = []
    documents = relevant + irrelevant
    for article in documents:
        snippet = article.get('snippet','') + " " + article['title']
        snippet = snippet.lower()
        normalized = snippet.translate(str.maketrans('', '', string.punctuation))
        cleaned.append(normalized)
    tfidf_vectorizer = TfidfVectorizer(stop_words="english", sublinear_tf=True, min_df=2)
    vectors = tfidf_vectorizer.fit_transform(cleaned)
    feature_names = tfidf_vectorizer.get_feature_names()
    dense = vectors.todense()
    denselist = dense.tolist()
    df = pd.DataFrame(denselist, columns=feature_names)
    return (df.iloc[:len(relevant)],df.tail(len(irrelevant)))

def augment_query(query, relevant_articles, irrelevant_articles):
    if not relevant_articles:
        return ""
    # relevant_vector = td_idf(relevant_articles)
    # irrelevant_vector = td_idf(irrelevant_articles)
    (relevant_vector, irrelevant_vector) = td_idf(relevant_articles,irrelevant_articles)
    ## Rocchio
    term2 = dict(((relevant_vector * beta) / len(relevant_articles)).sum())
    term3 = dict(((irrelevant_vector * gamma) / len(irrelevant_articles)).sum())
    result = {key: max(0, term2[key] - term3.get(key, 0)) for key in term2}
    return " ".join(sorted(result, key=result.get, reverse=True)[:2])







if __name__ == "__main__":
    # First parse and validate arguments
    if(len(sys.argv) != 5):
        print(f"Usage: {sys.argv[0]} <API Key> <Engine Key> <Precision> <Query>")
    
    client_key = sys.argv[1]
    engine_key = sys.argv[2]
    target_precision = float(sys.argv[3])
    query = sys.argv[4].strip('"')

    is_complete = False
   

    top_ten = get_query(client_key, engine_key, query)

    # Example so we don't waste queries must delete later!
    # top_ten = [{'kind': 'customsearch#result', 'title': 'Per Se | Thomas Keller Restaurant Group', 'htmlTitle': '<b>Per Se</b> | Thomas Keller Restaurant Group', 'link': 'https://www.thomaskeller.com/perseny', 'displayLink': 'www.thomaskeller.com', 'snippet': 'Per Se Front Door. center. Per Se Front Door. center. Per Se Front Door. center. \nPer Se Front Door. center. Per Se Front Door. center. Per Se Front Door. center.', 'htmlSnippet': '<b>Per Se</b> Front Door. center. <b>Per Se</b> Front Door. center. <b>Per Se</b> Front Door. center. <br>\n<b>Per Se</b> Front Door. center. <b>Per Se</b> Front Door. center. <b>Per Se</b> Front Door. center.', 'cacheId': 'RTF1K2ydkZkJ', 'formattedUrl': 'https://www.thomaskeller.com/perseny', 'htmlFormattedUrl': 'https://www.thomaskeller.com/<b>perse</b>ny', 'pagemap': {'cse_thumbnail': [{'src': 'https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcRIw0ztWYwEU_l3uhc4XjKjycMHv9rsxgHlHvRP2l0FvVZRnYBcT6fWRAc', 'width': '338', 'height': '149'}], 'metatags': [{'msapplication-tilecolor': '#2b5797', 'msapplication-config': '/sites/all/themes/thomaskeller/favicons/browserconfig.xml', 'theme-color': '#ffffff', 'handheldfriendly': 'true', 'viewport': 'width=device-width', 'mobileoptimized': 'width'}], 'cse_image': [{'src': 'https://www.thomaskeller.com/sites/default/files/styles/homepage_height_620px/public/media/tk.com_per.se_homepage_1a_0.jpg?itok=r8IQ_tmt'}]}}, {'kind': 'customsearch#result', 'title': 'Per se - Wikipedia', 'htmlTitle': '<b>Per se</b> - Wikipedia', 'link': 'https://en.wikipedia.org/wiki/Per_se', 'displayLink': 'en.wikipedia.org', 'snippet': 'Per se may refer to: per se, a Latin phrase meaning "by itself" or "in itself". Illegal \nper se, the legal usage in criminal and antitrust law; Negligence per se, legal\xa0...', 'htmlSnippet': '<b>Per se</b> may refer to: <b>per se</b>, a Latin phrase meaning &quot;by itself&quot; or &quot;in itself&quot;. Illegal <br>\n<b>per se</b>, the legal usage in criminal and antitrust law; Negligence <b>per se</b>, legal&nbsp;...', 'cacheId': '0ATHlffvgAMJ', 'formattedUrl': 'https://en.wikipedia.org/wiki/Per_se', 'htmlFormattedUrl': 'https://en.wikipedia.org/wiki/<b>Per</b>_<b>se</b>', 'pagemap': {'metatags': [{'referrer': 'origin'}]}}, {'kind': 'customsearch#result', 'title': 'Perse | Definition of Perse by Merriam-Webster', 'htmlTitle': '<b>Perse</b> | Definition of <b>Perse</b> by Merriam-Webster', 'link': 'https://www.merriam-webster.com/dictionary/perse', 'displayLink': 'www.merriam-webster.com', 'snippet': 'We generally use per se to distinguish between something in its narrow sense \nand some larger thing that it represents. Thus, you may have no objection to\xa0...', 'htmlSnippet': 'We generally use <b>per se</b> to distinguish between something in its narrow sense <br>\nand some larger thing that it represents. Thus, you may have no objection to&nbsp;...', 'cacheId': 'Rp6Iz9Xmc7QJ', 'formattedUrl': 'https://www.merriam-webster.com/dictionary/perse', 'htmlFormattedUrl': 'https://www.merriam-webster.com/dictionary/<b>perse</b>', 'pagemap': {'cse_thumbnail': [{'src': 'https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcSKksTSKYwpW8It403nrjw5t1_a8pLO2PI6ImEG7uvFrNfacgiziPZgG-_O', 'width': '225', 'height': '225'}], 'metatags': [{'msapplication-tilecolor': '#2b5797', 'og:image': 'https://merriam-webster.com/assets/mw/static/social-media-share/mw-logo-245x245@1x.png', 'twitter:title': 'Definition of PERSE', 'twitter:card': 'summary', 'theme-color': '#ffffff', 'twitter:url': 'https://www.merriam-webster.com/dictionary/perse', 'og:title': 'Definition of PERSE', 'twitter:aria-text': 'Share the Definition of perse on Twitter', 'og:aria-text': 'Post the Definition of perse to Facebook', 'og:description': 'of a dark grayish blue resembling indigo… See the full definition', 'twitter:image': 'https://merriam-webster.com/assets/mw/static/social-media-share/mw-logo-245x245@1x.png', 'referrer': 'unsafe-url', 'fb:app_id': '178450008855735', 'twitter:site': '@MerriamWebster', 'viewport': 'width=device-width, initial-scale=1.0', 'twitter:description': 'of a dark grayish blue resembling indigo… See the full definition', 'og:url': 'https://www.merriam-webster.com/dictionary/perse'}], 'cse_image': [{'src': 'https://merriam-webster.com/assets/mw/static/social-media-share/mw-logo-245x245@1x.png'}]}}, {'kind': 'customsearch#result', 'title': 'Per se meaning, how to use per se in a sentence | Readable ...', 'htmlTitle': '<b>Per se</b> meaning, how to use <b>per se</b> in a sentence | Readable ...', 'link': 'https://readable.com/blog/how-to-correctly-use-per-se/', 'displayLink': 'readable.com', 'snippet': "Aug 11, 2017 ... 'Per se' is a Latin term which literally means, “by itself”, “in itself” or “of itself”. This \nmeans you're taking something out of its context to describe it\xa0...", 'htmlSnippet': 'Aug 11, 2017 <b>...</b> &#39;<b>Per se</b>&#39; is a Latin term which literally means, “by itself”, “in itself” or “of itself”. This <br>\nmeans you&#39;re taking something out of its context to describe it&nbsp;...', 'cacheId': '-TVqSvTpAk4J', 'formattedUrl': 'https://readable.com/blog/how-to-correctly-use-per-se/', 'htmlFormattedUrl': 'https://readable.com/blog/how-to-correctly-use-<b>per</b>-<b>se</b>/', 'pagemap': {'cse_thumbnail': [{'src': 'https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcSlBYiffhbzXBFP31tB9A-NHz9y8Boyra5kgr8nCH-AjsCS_urf5OzmCys', 'width': '320', 'height': '157'}], 'metatags': [{'og:image': 'https://readable.com/wp-content/uploads/2017/08/header-cafe-talking.jpg', 'og:type': 'article', 'article:published_time': '2017-08-11T12:20:48+00:00', 'og:image:width': '850', 'twitter:card': 'summary_large_image', 'twitter:title': "Grammar 101: How to correctly use 'per se'", 'og:site_name': 'Readable', 'og:title': "Grammar 101: How to correctly use 'per se'", 'og:image:height': '418', 'readability-verification': 'M2yJBSY87fQXWGH3v2KnUHUZbpFst73kV5Y6xD4g', 'bingbot': 'index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1', 'og:description': '‘Per se’ is originally a Latin term which is commonly misused in English. Find out the true meaning of per se and how you can avoid this easy mistake.', 'twitter:creator': '@ReadableHQ', 'article:publisher': 'https://www.facebook.com/ReadableHQ', 'twitter:site': '@ReadableHQ', 'article:modified_time': '2020-10-15T13:17:37+00:00', 'viewport': 'width=device-width, initial-scale=1', 'twitter:description': '‘Per se’ is originally a Latin term which is commonly misused in English. Find out the true meaning of per se and how you can avoid this easy mistake.', 'og:locale': 'en_US', 'fb:admins': '860405712', 'og:url': 'https://readable.com/blog/how-to-correctly-use-per-se/'}], 'cse_image': [{'src': 'https://readable.com/wp-content/uploads/2017/08/header-cafe-talking.jpg'}]}}, {'kind': 'customsearch#result', 'title': 'Home | Per Sé Group', 'htmlTitle': 'Home | <b>Per Sé</b> Group', 'link': 'https://www.persegroup.com/', 'displayLink': 'www.persegroup.com', 'snippet': "Why Per Sé? There's a better solution to staffing. We're here to make a positive \nimpact by connecting great people with great careers. More About Us Our\xa0...", 'htmlSnippet': 'Why <b>Per Sé</b>? There&#39;s a better solution to staffing. We&#39;re here to make a positive <br>\nimpact by connecting great people with great careers. More About Us Our&nbsp;...', 'cacheId': 'o05coAcLKXgJ', 'formattedUrl': 'https://www.persegroup.com/', 'htmlFormattedUrl': 'https://www.<b>perse</b>group.com/', 'pagemap': {'cse_thumbnail': [{'src': 'https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcRZU48MDTE1ITMIcR_ceJEoQmJW45SY6oswxkKW4z8MaOuvA33qqf1BaXk', 'width': '299', 'height': '168'}], 'metatags': [{'og:image': 'https://www.persegroup.com/wp-content/uploads/2017/02/per_se_group_staffing.png', 'og:image:width': '1900', 'og:type': 'website', 'twitter:card': 'summary_large_image', 'twitter:title': 'Per Sé Group | People are Our Purpose | People are Our Purpose', 'og:site_name': 'Per Sé Group', 'og:title': 'Per Sé Group | People are Our Purpose | People are Our Purpose', 'og:image:height': '1069', 'twitter:image:height': '1069', 'og:description': 'There’s a better solution to staffing. We’re here to make a positive impact by connecting great people with great careers.', 'twitter:image': 'https://www.persegroup.com/wp-content/uploads/2017/02/per_se_group_staffing.png', 'twitter:image:width': '1900', 'viewport': 'width=device-width initial-scale=1 maximum-scale=1', 'twitter:description': 'There’s a better solution to staffing. We’re here to make a positive impact by connecting great people with great careers.', 'og:locale': 'en_US', 'og:url': 'https://www.persegroup.com/'}], 'cse_image': [{'src': 'https://www.persegroup.com/wp-content/uploads/2017/02/per_se_group_staffing.png'}]}}, {'kind': 'customsearch#result', 'title': 'per se - Wiktionary', 'htmlTitle': '<b>per se</b> - Wiktionary', 'link': 'https://en.wiktionary.org/wiki/per_se', 'displayLink': 'en.wiktionary.org', 'snippet': 'Borrowed from Latin per sē (“by itself”), from per (“by, through”) and sē (“itself, \nhimself, herself, themselves”). PronunciationEdit. (UK) IPA: /pəːˈseɪ/\xa0...', 'htmlSnippet': 'Borrowed from Latin <b>per sē</b> (“by itself”), from per (“by, through”) and sē (“itself, <br>\nhimself, herself, themselves”). PronunciationEdit. (UK) IPA: /pəːˈseɪ/&nbsp;...', 'cacheId': 'GhXbAKm2VRQJ', 'formattedUrl': 'https://en.wiktionary.org/wiki/per_se', 'htmlFormattedUrl': 'https://en.wiktionary.org/wiki/<b>per</b>_<b>se</b>', 'pagemap': {'metatags': [{'referrer': 'origin', 'theme-color': '#eaecf0', 'viewport': 'width=device-width, initial-scale=1.0, user-scalable=yes, minimum-scale=0.25, maximum-scale=5.0'}]}}, {'kind': 'customsearch#result', 'title': 'Per Se - Home - New York, New York - Menu, Prices, Restaurant ...', 'htmlTitle': '<b>Per Se</b> - Home - New York, New York - Menu, Prices, Restaurant ...', 'link': 'https://www.facebook.com/perse/', 'displayLink': 'www.facebook.com', 'snippet': "Per Se, New York, NY. 56361 likes · 251 talking about this · 50043 were here. \nThe official page of Thomas Keller's Per Se.", 'htmlSnippet': '<b>Per Se</b>, New York, NY. 56361 likes · 251 talking about this · 50043 were here. <br>\nThe official page of Thomas Keller&#39;s <b>Per Se</b>.', 'cacheId': 'nr4RifcguF8J', 'formattedUrl': 'https://www.facebook.com/perse/', 'htmlFormattedUrl': 'https://www.facebook.com/<b>perse</b>/', 'pagemap': {'cse_thumbnail': [{'src': 'https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcS2TKaK6RC8W61N8L7OM57AGc99Ifbgj4E3F8KhrrxuBHiqUx-AbPjoxFwL', 'width': '259', 'height': '194'}], 'metatags': [{'al:android:url': 'fb://page/13166590145?referrer=app_link', 'referrer': 'default', 'og:image': 'https://lookaside.fbsbx.com/lookaside/crawler/media/?media_id=13166590145', 'al:ios:app_name': 'Facebook', 'og:title': 'Per Se', 'al:android:package': 'com.facebook.katana', 'al:ios:url': 'fb://page/?id=13166590145', 'og:url': 'https://www.facebook.com/perse/', 'og:description': "Per Se, New York, NY. 56,361 likes · 251 talking about this · 50,043 were here. The official page of Thomas Keller's Per Se", 'al:android:app_name': 'Facebook', 'al:ios:app_store_id': '284882215'}], 'cse_image': [{'src': 'https://lookaside.fbsbx.com/lookaside/crawler/media/?media_id=10152679710585146'}], 'listitem': [{'item': 'Places', 'name': 'Places', 'position': '1'}, {'item': 'New York, New York', 'name': 'New York, New York', 'position': '2'}, {'item': 'New American Restaurant', 'name': 'New American Restaurant', 'position': '3'}]}}, {'kind': 'customsearch#result', 'title': 'Per Se DUI Laws - FindLaw', 'htmlTitle': '<b>Per Se</b> DUI Laws - FindLaw', 'link': 'https://www.findlaw.com/dui/laws-resources/per-se-dui-laws.html', 'displayLink': 'www.findlaw.com', 'snippet': 'Oct 25, 2018 ... Per se laws in DUI or DWI cases generally establish that once an individual is \nshown to have a blood-alcohol concentration (BAC) at or above\xa0...', 'htmlSnippet': 'Oct 25, 2018 <b>...</b> <b>Per se</b> laws in DUI or DWI cases generally establish that once an individual is <br>\nshown to have a blood-alcohol concentration (BAC) at or above&nbsp;...', 'cacheId': 'eD9ExcbxuqkJ', 'formattedUrl': 'https://www.findlaw.com/dui/laws-resources/per-se-dui-laws.html', 'htmlFormattedUrl': 'https://www.findlaw.com/dui/laws-resources/<b>per</b>-<b>se</b>-dui-laws.html', 'pagemap': {'cse_thumbnail': [{'src': 'https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcT0t9xnFvbwMHrPXQJUUuXAxzrxO752NCj3-meTSCZIxFpNIU-yI7TRFSc', 'width': '225', 'height': '225'}], 'metatags': [{'og:image': 'https://www.findlawimages.com/public/thumbnails_62x62/findlaw_62x62.png', 'og:type': 'article', 'og:site_name': 'Findlaw', 'viewport': 'width=device-width, initial-scale=1.0', 'og:title': 'Per Se DUI Laws - FindLaw', 'og:url': 'https://www.findlaw.com/dui/laws-resources/per-se-dui-laws.html', 'og:description': "Per se laws in DUI or DWI cases generally establish that once an individual is shown to have a blood-alcohol concentration (BAC) at or above .08 percent, that person is considered intoxicated by law. Learn more in FindLaw's DUI Law section."}], 'cse_image': [{'src': 'https://www.findlawimages.com/public/thumbnails_62x62/findlaw_62x62.png'}]}}, {'kind': 'customsearch#result', 'title': 'Per Se Restaurant - New York, NY | OpenTable', 'htmlTitle': '<b>Per Se</b> Restaurant - New York, NY | OpenTable', 'link': 'https://www.opentable.com/per-se', 'displayLink': 'www.opentable.com', 'snippet': "Per Se offers two prix fixe tasting menus a Tasting of Vegetables or the Chef's \nTasting Menu, which changes daily. Dining Style. Fine Dining. Cuisines. \nAmerican\xa0...", 'htmlSnippet': '<b>Per Se</b> offers two prix fixe tasting menus a Tasting of Vegetables or the Chef&#39;s <br>\nTasting Menu, which changes daily. Dining Style. Fine Dining. Cuisines. <br>\nAmerican&nbsp;...', 'formattedUrl': 'https://www.opentable.com/per-se', 'htmlFormattedUrl': 'https://www.opentable.com/<b>per</b>-<b>se</b>', 'pagemap': {'cse_thumbnail': [{'src': 'https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcQJIh872gjfGpOR2KBEL4_AC_l9vVIlUWWeYx3XBUjk0_PfJT4_lD39yZQ', 'width': '208', 'height': '208'}], 'metatags': [{'business:contact_data:postal_code': '10019', 'place:location:longitude': '-73.9825000', 'og:image': 'https://resizer.otstatic.com/v2/profiles/legacy/2783.jpg', 'fb:profile_id': 'http://facebook.com/perse', 'og:type': 'website', 'og:image:width': '200', 'og:site_name': 'www.opentable.com', 'business:contact_data:website': 'http://www.perseny.com/', 'al:ios:app_name': 'OpenTable', 'business:contact_data:locality': 'en-US', 'business:contact_data:region': 'Columbus Circle', 'place:location:latitude': '40.7680000', 'business:contact_data:phone_number': '(212) 823-9335', 'og:title': 'Per Se - New York, NY on OpenTable', 'og:image:height': '200', 'al:ios:url': 'reservetable-com.contextoptional.OpenTable-1://?rid=2783&dt=2021-02-01T01%3A22%3A10-05%3A00&ps=2', 'og:description': 'Per Se, Fine Dining American cuisine. Read reviews and book now.', 'al:ios:app_store_id': '296581815', 'ot:page_type': 'restaurants,restaurant-profile,listing', 'fb:app_id': '123876194314735', 'viewport': 'width=device-width, initial-scale=1', 'business:contact_data:country': 'United States', 'business:contact_data:street_address': '10 Columbus Circle', 'og:url': 'https://www.opentable.com/per-se'}], 'cse_image': [{'src': 'https://resizer.otstatic.com/v2/profiles/legacy/2783.jpg'}]}}, {'kind': 'customsearch#result', 'title': 'Per se - definition of per se by The Free Dictionary', 'htmlTitle': '<b>Per se</b> - definition of <b>per se</b> by The Free Dictionary', 'link': 'https://www.thefreedictionary.com/per+se', 'displayLink': 'www.thefreedictionary.com', 'snippet': 'per se. A Latin phrase meaning by itself, used to mean intrinsically. Dictionary of \nUnfamiliar Words by Diagram Group Copyright © 2008 by Diagram\xa0...', 'htmlSnippet': '<b>per se</b>. A Latin phrase meaning by itself, used to mean intrinsically. Dictionary of <br>\nUnfamiliar Words by Diagram Group Copyright © 2008 by Diagram&nbsp;...', 'cacheId': 'K7HaWMvUCEkJ', 'formattedUrl': 'https://www.thefreedictionary.com/per+se', 'htmlFormattedUrl': 'https://www.thefreedictionary.com/<b>per</b>+<b>se</b>', 'pagemap': {'cse_thumbnail': [{'src': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRYdkuI0uE9gcqSkj_ayX2U9j3w9PMpjL9KOS4mDt6h2s29lFotin4do3Q', 'width': '225', 'height': '225'}], 'metatags': [{'og:image': 'http://img.tfd.com/TFDlogo1200x1200.png', 'msapplication-packagefamilyname': 'Farlex.581429F59E1D8_wyegy4e46y996', 'apple-itunes-app': 'app-id=379450383, app-argument=thefreedictionary://search/per+se?', 'og:type': 'article', 'og:image:width': '1200', 'og:site_name': 'TheFreeDictionary.com', 'viewport': 'width=device-width, initial-scale=1.0', 'og:title': 'per se', 'og:image:height': '1200', 'og:url': 'https://www.thefreedictionary.com/per+se', 'og:description': 'Definition, Synonyms, Translations of per se by The Free Dictionary', 'msapplication-id': 'Farlex.581429F59E1D8'}], 'cse_image': [{'src': 'http://img.tfd.com/TFDlogo1200x1200.png'}]}}]
    
    while not (is_complete):
        print("Parameters:")
        print(f"Client Key = {client_key}")
        print(f"Engine Key = {engine_key}")
        print(f"Query      = {query}")
        print(f"Precision  = {target_precision}")
        print("Google Search Results:")
        print("======================")

        if(len(top_ten) != 10):
            print("Could not obtain 10 relevant articles")
            quit()
            
        res_count = 1
        relevant = []
        irrelevant = []

        # Display and guage results
        for result in top_ten:
            print(f"Result {res_count}")
            print("[")
            print(f" URL: {result.get('formattedUrl','null')}")
            print(f" Title: {result.get('title','null')}")
            print(f" Summary: {result.get('snippet','null')}")
            print("]\n")
            is_relevant = input("Relevant (Y/N)?")
            if (is_relevant.lower() == "y"):
                relevant.append(result)
            else:
                irrelevant.append(result)
            res_count+=1
        print("======================")
        print("FEEDBACK SUMMARY")
        print(f"Query {query}")
    
        # Calculate Precision
        precision = len(relevant) / (len(relevant) + len(irrelevant))
        print(f"Precision {precision}")
        if(precision >= target_precision): # If target precision reached, exit program
            print("Desired precision reached, done")
            is_complete=True
        else: # Else continue and augment query
            print(f"Still below the desired precision of {target_precision}")
            print("Indexing Results ....")
            augment = augment_query(query, relevant,irrelevant)
            print("Indexing Results ....")
            print(f"Augmenting by {augment}")
            if((precision == 0) or (augment == "")): # Keeping this for now to match the example format, but may change
                print("Below desired precision, but can no longer augment the query")
                quit()
            query += " " + augment
            top_ten = get_query(client_key, engine_key, query)


