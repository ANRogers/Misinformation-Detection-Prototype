from inference import predict_article
from source_checker import check_source_reliability
from article_warnings import generate_warnings
from generate_report import export_report_to_pdf
from bs4 import BeautifulSoup
import os
import requests
import time
from urllib.parse import urlparse

def download_webpage(url):
    try:
        webpage = requests.get(url)  # get webpage from url
        webpage.raise_for_status()  # check for errors
        article_soup = BeautifulSoup(webpage.text, 'html.parser')  # parse article
        return article_soup.get_text(separator=' ', strip=True)
    except requests.RequestException as e:
        print(f"Error downloading page: {e}")
        return None

def get_source_from_url(url):
    parsed_url = urlparse(url)  # breakup url into each section
    source = parsed_url.netloc  # get only source part of url
    return source.replace('www.', '')  # format into same form as sources

def extract_article_text(file_path):  # extracts the html text from a html file
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            article_content = file.read()
        article_soup = BeautifulSoup(article_content, 'html.parser')  # parse article
        return article_soup.get_text(separator=' ', strip=True)
    except FileNotFoundError:
        print(f"\nError: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"\nError reading file {file_path}: {e}")
        return None

def process_file(html_content, source, name):  # predict article and display results
    try:
        result = predict_article(html_content)
        source_status = check_source_reliability(source)

        print("\nPREDICTION RESULT")
        print(f"Name            : {name}")
        print(f"Source          : {source}")
        print(f"Source Status   : {source_status}")
        print(f"Content Analysis: {result['content_prediction']}")
        print(f"Confidence      : {result['confidence']}")
        print(f"Final Decision  : {result['final_decision']}")

        print("\nARTICLE REPORT")
        warnings = generate_warnings(result, source_status)
        for warning in warnings:
            print(warning)

        return name, source, source_status, result, warnings

    except Exception as e:
        print(f"Error processing article: {e}")

def main():
    print("MEDICAL MISINFORMATION DETECTOR")

    choice = input("\nDo you want to process a (1) an article url or (2) multiple files from a text list? (Enter 1 or 2): ")

    if choice == '1':
        # download from url
        url = input("Enter the webpage URL: ").strip()
        html_content = download_webpage(url)
        source = get_source_from_url(url)
        if html_content:
            start_time = time.time()
            name, source, source_status, result, warnings = process_file(html_content, source, url)
            end_time = time.time()
            print(f"\nProcessing time: {end_time - start_time:.2f} seconds")
            
            report = [[name, source, source_status, result, warnings]]
            choice = input("\nWould you like to export the report to file? 1 = yes, 0 = no :")
            if choice == '1':
                export_report_to_pdf(report)

    elif choice == '2':
        # read multiple files at once
        list_file_path = input("\nEnter the path to the text file listing HTML paths and sources: ")

        if not os.path.exists(list_file_path):  # check if file exists
            print(f"List file '{list_file_path}' not found.")
            return

        with open(list_file_path, 'r', encoding='utf-8') as list_file:
            articles = list_file.readlines()

        # get article file locations and then extracts their text
        # To input an article put in article file location then | followed by source of article 
        report = []
        for article in articles:
            article = article.strip()
            if not article or '|' not in article:
                continue  # Skip lines with no article path
            html_file_path, source = map(str.strip, article.split('|', 1))
            content = extract_article_text(html_file_path)
            if content:
                name, source, source_status, result, warnings = process_file(content, source, html_file_path)
                report.append([name, source, source_status, result, warnings])

        choice = input("\nWould you like to export the report to file? 1 = yes, 0 = no :")
        if choice == '1':
            export_report_to_pdf(report)

    else:
        print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
