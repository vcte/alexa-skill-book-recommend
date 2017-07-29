from bs4 import BeautifulSoup
import requests
import random
import json

site = "http://www.whatshouldireadnext.com"

def lambda_handler(event, context):
    # check app id
    if event["session"]["application"]["applicationId"] != "":
        raise ValueError("Invalid Application ID")

    intent = event["request"]["intent"]
    if event["request"]["type"] == "LaunchRequest":
        return on_launch(intent)
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(intent)
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(intent)

def on_launch(intent):
    return get_welcome_response()

def on_intent(intent):
    intent_name = intent["name"]

    if intent_name == "RecommendSimilarBookIntent":
        return get_similar_book(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or \
         intent_name == "AMAZON.StopIntent":
        return get_goodbye_response()

def on_session_ended(intent):
    pass

def get_welcome_response():
    text = "Welcome to the book recommendation skill. "
    reprompt = "You can ask me to recommend a book similar " + \
               "to one you've already read. Try asking, recommend me a book" + \
               "similar to Harry Potter"
    return build_response("RecommendSimilarBooks", text, reprompt, False)

def get_goodbye_response():
    text = "Thank you for using the book recommendation skill"
    return build_response("RecommendSimilarBooks - Goodbye", text, None, True)

def get_similar_book(intent):
    intent_book = intent["slots"]["Book"]["value"]
    r = requests.get(site + "/finder.php?q=" + intent_book)
    if r.ok:
        soup = BeautifulSoup(r.content, "html.parser")
        choices = soup.ul.find_all("li")
        if len(choices) > 0:
            href = choices[0].a.get("href")
            r = requests.get(site + href)
            if r.ok:
                soup = BeautifulSoup(r.content, "html.parser")
                lis = soup.find_all("li", class_ = "recommendation-logged-out")
                li = random.choice(lis[:5])
                print('"' + li.text + '"')
                author, _, book = li.text.partition(" - ")
                author = author.partition(" (")[0]
                book = book.partition(" (")[0]
                return build_recommended_book_msg(author, book)
            else:
                return build_site_down_msg()
        else:
            return book_not_found_msg(intent_book)
    else:
        return build_site_down_msg()

def build_recommended_book_msg(author, book):
    txt1 = "Why don't you try " + book + ", by " + author
    txt2 = "I recommend reading " + book + ", by " + author
    txt3 = book + " by " + author + " is similar to that book"
    text = random.choice([txt1, txt2, txt3])
    return build_response("Book recommendation", text, "", False)

def build_site_down_msg():
    text = """I'm running into technical problems at the moment,
              and I cannot answer your question."""
    return build_response("Site down", text, "", False)

def book_not_found_msg(book):
    text = "I'm sorry, I could not find any books with the name " + book
    return build_response("Book not found", text, "", False)

def build_response(title, output, reprompt_text, should_end_session):
    return {
        "version" : "1.0",
        "sessionAttributes" : {},
        "response" : {
            "outputSpeech" : {
                "type" : "PlainText",
                "text" : output
            },
            "card" : {
                "type" : "Simple",
                "title" : title,
                "content" : output
            },
            "reprompt" : {
                "outputSpeech" : {
                    "type" : "PlainText",
                    "text" : reprompt_text
                }
            },
            "shouldEndSession" : should_end_session
        }
    }

sample_intent = json.loads("""{
      "name": "RecommendSimilarBookIntent",
      "slots": {
        "Book": {
          "name": "Book",
          "value": "adsf"
        }
      }
    }""")
print(handle_intent(sample_intent))
