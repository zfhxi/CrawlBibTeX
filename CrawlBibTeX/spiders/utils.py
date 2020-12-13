import csv


def get_paper_titles(title_filename='./papers.csv'):
    titles = list()
    with open(title_filename, 'r') as csv_f:
        for paper_title in csv.reader(csv_f, delimiter='#'):
            if paper_title[0]:
                titles.append(paper_title[0])
    return titles
