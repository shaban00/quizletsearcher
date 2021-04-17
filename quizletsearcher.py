import requests
import certifi
from bs4 import BeautifulSoup
from random import choice
from difflib import SequenceMatcher
import banners
import os
import sys
import heapq


cert = certifi.where()

base_url = "https://www.google.com"


with open("user_agents.txt", "r") as file:
    user_agents = file.read().splitlines()


def google_search(url: str):

    google_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Host": "www.google.com",
        "TE": "Trailers",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": choice(user_agents)
    }

    quizlet_links = list()
    quizlet_navigations = list()

    with requests.Session() as sess:
        try:
            max_retries = requests.adapters.HTTPAdapter(max_retries=10)
            sess.mount("https://", max_retries)
            sess.mount("http://", max_retries)
            response = sess.get(url, headers=google_headers, verify=cert)
        except requests.exceptions.RequestException as error:
            print(error)

        soup = BeautifulSoup(response.text, "html.parser")

        results = soup.findAll("div", {"class": "g"})

        navigations = soup.findAll("td")


        for result in results:
            if result.find("div", {"class": "yuRUbf"}):
                link = result.find("div", {"class": "yuRUbf"}).find("a").get("href")

                if "quizlet.com" in link:
                    quizlet_links.append(link)

        for navigation in navigations:
            if navigation.find("a", {"class": "fl"}):
                nav_link = base_url + navigation.find("a", {"class": "fl"}).get("href")
                quizlet_navigations.append(nav_link)

    return quizlet_links, quizlet_navigations


def quizlet_search(url: str, user_question: str):

    quizlet_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Host": "quizlet.com",
        "DNT": "1",
        "TE": "Trailers",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": choice(user_agents)
    }

    items_list = list()

    with requests.Session() as sess:
        try:
            max_retries = requests.adapters.HTTPAdapter(max_retries=10)
            sess.mount("https://", max_retries)
            sess.mount("http://", max_retries)
            response = sess.get(url, headers=quizlet_headers, verify=cert)
        except requests.exceptions.RequestException as error:
            print(error)

        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.findAll("div", {"class": "SetPageTerms-term"})

        for row in rows:

            items_dict = dict()

            word_text = row.find("a", {"class": "SetPageTerm-wordText"}).getText()
            definition_text = row.find("a", {"class": "SetPageTerm-definitionText"}).getText()


            word_text_ratio = SequenceMatcher(None, word_text.lower(), user_question).ratio()
            definition_text_ratio = SequenceMatcher(None, definition_text.lower(), user_question).ratio()

            if word_text_ratio > definition_text_ratio:
                items_dict["question"] = word_text.lower()
                items_dict["answer"] = definition_text.lower()
                items_dict["ratio"] = word_text_ratio

                items_list.append(items_dict)

            elif word_text_ratio < definition_text_ratio:
                items_dict["question"] = definition_text.lower()
                items_dict["answer"] = word_text.lower()
                items_dict["ratio"] = definition_text_ratio

                items_list.append(items_dict)


    max_ratio = max([item.get("ratio") for item in items_list]) if len([item.get("ratio") for item in items_list]) else False

    if max_ratio:    
        for item in items_list:
            if item.get("ratio") == max_ratio:
                return item


def operating_system():
    if sys.platform == "linux" or sys.platform == "linux2":
        os.system("clear")
    elif sys.platform == "darwin":
        os.system("clear")
    elif sys.platform == "win32":
        os.system("cls")


def main(url: str, user_question: str):
    links, navigations = google_search(url)

    table_headers = ["question", "answer", "ratio", "link"]
    table_list = list()

    if len(links) > 0:
        print("\033[1m\nQuestions & Answers\033[0m\n")
        for link in links:
            item = quizlet_search(link, user_question)

            if item:
                print("\033[94mQuestion: \033[0m" + "\033[1m" + str(item.get("question").capitalize()) + "\033[0m")
                print("\033[92mAnswer: \033[0m" + "\033[1m" + str(item.get("answer").capitalize()) + "\033[0m")
                print("\033[96mQuestion similarity: \033[0m" + "\033[1m" + str(item.get("ratio")) + "\033[0m")
                print("\033[95mLink: \033[0m" + "\033[1m" + str(link) + "\033[0m")

                print("-----------------------------------------------------------------")

    else:
        print("\n")
        print("\033[93mSorry!!!. There are no search results on quizlet\033[0m")
        print(print("\033[93\033[1mBut you can still try again\033[0m"))


if __name__ == "__main__":
    while True:
        operating_system()
        print(banners.banner())
        
        try:
            user_question = input("\033[94m\033[1mQuestion: >>> \033[0m")
        except KeyboardInterrupt:
            print("\nProgram exited!!!")
            sys.exit()


        search_url = base_url + "/search?q=" + user_question.lower() + " quizlet"

        main(search_url, user_question)

        try:
            continuation = input("\nDo you want to continue: (y/n) : ").lower()
        except KeyboardInterrupt:
            print("\nProgram exited!!!")
            sys.exit()
            

        if continuation != "y":
            print("\nProgram exited!!!")
            sys.exit()