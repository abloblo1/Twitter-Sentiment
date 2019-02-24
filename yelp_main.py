from pathlib import Path
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
import pyarrow as pa
import pyarrow.parquet as pq
from fastparquet import ParquetFile
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob, Word
from sklearn.externals import joblib
import json

class YelpSentiment:
    def __init__(self):
        self.review = []
        self.user = []
        self.user_review =[]


    def parse(self):
        yelp_dir = Path('data', 'yelp_dir')
        parquet_dir = yelp_dir / 'parquet'
        if not parquet_dir.exists():
            parquet_dir.mkdir(exist_ok=True)

        for file in ['review', 'user']:
            print(file)
            json_file = yelp_dir / f'yelp_academic_dataset_{file}.json'
            parquet_file = parquet_dir / f'{file}.parquet'

            try:
                pd.read_parquet(parquet_file, engine='pyarrow')
            except Exception as e:
                print(e)
                pd.read_parquet(parquet_file, engine='fastparquet')

    def main(self):
        yelp_dir = Path('data', 'yelp_dir')
        parquet_dir = yelp_dir / 'parquet'
        if not parquet_dir.exists():
            parquet_dir.mkdir(exist_ok=True)

        for file in ['review', 'user']:
            json_file = yelp_dir / f'yelp_academic_dataset_{file}.json'
            parquet_file = parquet_dir / f'{file}.parquet'

            data = json_file.read_text(encoding='utf-8')
            json_data = '[' + ','.join([l.strip()
                                        for l in data.split('\n') if l.strip()]) + ']\n'
            data = json.loads(json_data)
            df = json_normalize(data)
            if file == 'review':
                df.date = pd.to_datetime(df.date)
                latest = df.date.max()
                df['year'] = df.date.dt.year
                df['month'] = df.date.dt.month
                df = df.drop(['date', 'business_id', 'review_id'], axis=1)
            if file == 'user':
                df.yelping_since = pd.to_datetime(df.yelping_since)
                df = (df.assign(member_yrs=lambda x: (latest - x.yelping_since)
                                .dt.days.div(365).astype(int))
                      .drop(['elite', 'friends', 'name', 'yelping_since'], axis=1))
            df.dropna(how='all', axis=1).to_parquet(parquet_file, compression='gzip')


        self.user = pd.read_parquet(parquet_dir / 'user.parquet')
        self.review = pd.read_parquet(parquet_dir / 'review.parquet', engine='fastparquet')

        self.user.head()
        self.review.head()
        self.user_review = (
            self.review.merge(self.user, on='user_id', how='left', suffixes=['', '_user']).drop('user_id', axis=1))
        # remove 0 stars
        self.user_review = self.user_review[self.user_review.stars > 0]
        self.boxPlot()
        self.histogram()
        self.lineGraph()

    def barChart(self):
        # star rating distribution
        x = self.user_review['stars'].value_counts()
        x = x.sort_index()
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x.index, x.values, alpha=0.8)
        plt.title("Star Rating Distribution")
        plt.ylabel('count')
        plt.xlabel('Star Ratings')
        rects = ax.patches
        labels = x.values
        for rect, label in zip(rects, labels):
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2, height + 5, label, ha='center', va='bottom')
        plt.show()
        plt.close()

    def subPlots(self):
        fig, axes = plt.subplots(ncols=2, figsize=(14, 4))
        self.user_review.year.value_counts().sort_index().plot.bar(title='Reviews per Year', ax=axes[0]);
        sns.lineplot(x='year', y='stars', data=self.user_review, ax=axes[1])
        axes[1].set_title('Stars per year')
        plt.show()
        plt.close()



    def boxPlot(self):
        sample_reviews = self.user_review[['stars', 'text']].sample(1000)

        def detect_polarity(text):
            return TextBlob(text).sentiment.polarity

        sample_reviews['polarity'] = sample_reviews.text.apply(detect_polarity)
        sample_reviews.head()

        plt.figure(figsize=(10, 6))
        sns.boxenplot(x='stars', y='polarity', data=sample_reviews, palette=sns.color_palette("Set2", n_colors=5))
        plt.show()
        plt.close()

    def histogram(self):
        # user_review = (
        #     self.review.merge(self.user, on='user_id', how='left', suffixes=['', '_user']).drop('user_id', axis=1))
        # # remove 0 stars
        # user_review = user_review[user_review.stars > 0]

        sample_reviews = self.user_review[['stars', 'text']].sample(1000)

        def detect_polarity(text):
            return TextBlob(text).sentiment.polarity

        sample_reviews['polarity'] = sample_reviews.text.apply(detect_polarity)
        sample_reviews.head()

        num_bins = 50
        plt.figure(figsize=(10, 6))
        n, bins, patches = plt.hist(sample_reviews.polarity, num_bins, facecolor='pink', alpha=0.5)
        plt.xlabel('Polarity')
        plt.ylabel('Count')
        plt.title('Histogram of polarity')
        plt.show()

    def lineGraph(self):
        # user_review = (
        #     self.review.merge(self.user, on='user_id', how='left', suffixes=['', '_user']).drop('user_id', axis=1))
        # user_review = user_review[user_review.stars > 0]

        sample_reviews = self.user_review[['stars', 'text', 'year']].sample(1500)

        def detect_polarity(text):
            return TextBlob(text).sentiment.polarity

        sample_reviews['polarity'] = sample_reviews.text.apply(detect_polarity)
        sample_reviews.head()
        print(sample_reviews.head(5))
        plt.figure(figsize=(10, 6))
        plt.title("Year vs Polarity by Stars")
        sns.lineplot(x="year", y="polarity", hue="stars", data=sample_reviews, legend="full")
        plt.show()
        plt.close()


if __name__ == "__main__":
    sa = YelpSentiment()
    sa.main()
