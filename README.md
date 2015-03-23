## Appstore tools

A small collection of tools used for [Xavee](../xavee).

* `collect_iphone_ranking.py`: this is a tool to collect the current iTunes Appstore rankings for a user-defined list of countries.
Apps can be narrowed down to a ranking type or one or more categories.
Returned are .csv files with the rankings for each country,
along with the ranking of each app in the other specified countries on the same line, to allow for quick comparison. 

* `find_review_word_occurrences.py`: this is a tool to find how often certain words are mentioned in the reviews for an app.
It takes a list of Appstore IDs as input and returns a .csv file with the occurrence numbers of each word in each app,
as well as their context in the review.
