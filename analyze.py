# packages to store and manipulate data
import pandas as pd
import numpy as np

# plotting packages
import matplotlib.pyplot as plt
import seaborn as sns

# model building package
import sklearn

# package to clean text
import re

from wordcloud import WordCloud


pathname = ''

def billreader(pathname):
    bill = pd.read_csv(pathname)

    return bill

bill = billreader(pathname)

# Remove punctuation
bill['paper_text_processed'] = \
bill['paper_text'].map(lambda x: re.sub('[,\.!?]', '', x))
# Convert the titles to lowercase
bill['paper_text_processed'] = \
bill['paper_text_processed'].map(lambda x: x.lower())
# Print out the first rows of papers
bill['paper_text_processed'].head()

# Import the wordcloud library
# Join the different processed titles together.
long_string = ','.join(list(papers['paper_text_processed'].values))
# Create a WordCloud object
wordcloud = WordCloud(background_color="white", max_words=5000, contour_width=3, contour_color='steelblue')
# Generate a word cloud
wordcloud.generate(long_string)
# Visualize the word cloud
wordcloud.to_image()

