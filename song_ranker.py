#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Jonas Berg

import pandas as pd
import yt_dlp
import subprocess
import json

# Load data frame - contestants for the basic data or enriched-contestants for
# the ones with the youtube metadata already loaded.
#df = pd.read_csv('contestants2004-2024.csv')
df = pd.read_csv('enriched-contestants2004-2024.csv')
# Make each contestant identifiable for other analysis pipelines and joining data to this one
df['performance_id'] = df['year'].astype(str) + '-' + df['to_country_id']
if 'spotify_popularity' not in df.columns:
    spot = pd.read_csv('prelim-top80-Spotify-updated.csv', usecols=['year', 'to_country_id','spotify_popularity', 'notes'])
    spot['performance_id'] = spot['year'].astype(str) + '-' + spot['to_country_id']
    spot = spot.set_index('performance_id')
    df = df.join(spot[['spotify_popularity', 'notes']], on='performance_id')

# ** Get fractions of points for the year to normalize between years **
# TODO: useless variable?
outperformers = 0
for year in range(2004,2025):
    current_years_contestants = df[df['year'] == year]
    finals_point_sum_total = current_years_contestants['points_final'].sum()
    finals_jury_point_sum_total = current_years_contestants['points_jury_final'].sum()
    finals_tele_point_sum_total = current_years_contestants['points_tele_final'].sum()

    current_years_contestants['fraction_of_total_points'] = current_years_contestants['points_final'] / finals_point_sum_total
    current_years_contestants['fraction_of_jury_points'] = current_years_contestants['points_jury_final'] / finals_jury_point_sum_total
    current_years_contestants['fraction_of_tele_points'] = current_years_contestants['points_tele_final'] / finals_tele_point_sum_total

    # Get those who got more than 10% of all available votes that year
    outperformers += current_years_contestants[current_years_contestants['fraction_of_total_points']>=0.1].shape[0]
    for index in current_years_contestants.index.array:
        df.at[index, 'fraction_of_total_points'] = current_years_contestants.at[index, 'fraction_of_total_points']
        df.at[index, 'fraction_of_jury_points'] = current_years_contestants.at[index, 'fraction_of_jury_points']
        df.at[index, 'fraction_of_tele_points'] = current_years_contestants.at[index, 'fraction_of_tele_points']

# ** Get metadata for linked performance videos **
def scrape_video_metadata():
    # Only check for finalists
    video_list = df[df['place_final'].notnull()]['youtube_url']
    for video in video_list:
        #print(video)
        # Call with --simulate and --dump_json to get only metadata, use jquery to get only the interesting columns
        # Faster to write than actully using Python, but slower to run
        command = "python3 -m yt_dlp -s -j \"%s\" | jq '{\"url\":.original_url,\"title\":.title,\"upload_date\":.upload_date,\"views\":.view_count,\"likes\":(.like_count // 0), \"comments\":(.comment_count)}'" % video
        output = subprocess.run(command, shell=True, capture_output=True, encoding='utf-8')
        try:
            output.check_returncode()
            # If for some reason we don't get data but don't have an error code, get out by throwing the wrong error
            if output.stdout == None:
                raise subprocess.CalledProcessError
            # Throws JSONDecodeError if stdout is empty
            json_output = json.loads(output.stdout)
            # Find matching row index in a non-optimal way
            index = df[df['youtube_url'] == video].index[0]
            df.at[index, 'views'] = json_output['views']
            df.at[index, 'upload_date'] = json_output['upload_date']
            df.at[index, 'likes'] = json_output['likes']
            df.at[index, 'comments'] = json_output['comments']
            # Sanity check for catching music videos, lyrics videos, winner's performances
            if 'final' not in json_output['title'].lower() and 'live' not in json_output['title'].lower():
                print("Possibly non-live performance for %s: %s " % (json_output['url'], json_output['title']))
            df.at[index, 'video_title'] = json_output['title']
        except (subprocess.CalledProcessError, json.decoder.JSONDecodeError):
            print(output.stdout)
            print(output.stderr)

#scrape_video_metadata()

# ** Going through fractions and rank all per year 'block' according to views and votes
# First block: only televotes (mostly)
first_block = df[(df['year'] >= 2004) & (df['year'] < 2009)]
views_sum_total = first_block['views'].sum()
first_block['fraction_of_views'] = first_block['views'] / views_sum_total
first_block['view_rank'] = first_block['fraction_of_views'].rank(ascending=False)
first_block['point_rank'] = first_block['fraction_of_total_points'].rank(ascending=False)
first_block['spotify_rank'] = first_block['spotify_popularity'].rank(ascending=False)
# We want all votes to have the same weight
first_block['weighted_average_total_rank'] = (4 * first_block['point_rank'] + first_block['view_rank'] + first_block['spotify_rank']) / 6.0

for index in first_block.index.array:
    df.at[index, 'fraction_of_views'] = first_block.at[index, 'fraction_of_views']
    df.at[index, 'view_rank'] = first_block.at[index, 'view_rank']
    df.at[index, 'point_rank'] = first_block.at[index, 'point_rank']
    df.at[index, 'spotify_rank'] = first_block.at[index, 'spotify_rank']
    df.at[index, 'weighted_average_total_rank'] = first_block.at[index, 'weighted_average_total_rank']

# Second block: combined votes for televotes and jury, count like before
second_block = df[(df['year'] >= 2009) & (df['year'] < 2016)]
views_sum_total = second_block['views'].sum()
second_block['fraction_of_views'] = second_block['views'] / views_sum_total
second_block['view_rank'] = second_block['fraction_of_views'].rank(ascending=False)

second_block['point_rank'] = second_block['fraction_of_total_points'].rank(ascending=False)
second_block['point_jury_rank'] = second_block['fraction_of_jury_points'].rank(ascending=False)
second_block['point_tele_rank'] = second_block['fraction_of_tele_points'].rank(ascending=False)
second_block['spotify_rank'] = second_block['spotify_popularity'].rank(ascending=False)

#NB 2013 special - using the combined points twice
second_block['weighted_average_total_rank'] = (2 * (second_block['point_jury_rank'] + second_block['point_tele_rank']) + second_block['view_rank'] + second_block['spotify_rank']) / 6.0

for index in second_block.index.array:
    df.at[index, 'fraction_of_views'] = second_block.at[index, 'fraction_of_views']
    df.at[index, 'view_rank'] = second_block.at[index, 'view_rank']
    df.at[index, 'point_rank'] = second_block.at[index, 'point_rank']
    df.at[index, 'point_jury_rank'] = second_block.at[index, 'point_jury_rank']
    df.at[index, 'point_tele_rank'] = second_block.at[index, 'point_tele_rank']
    df.at[index, 'spotify_rank'] = second_block.at[index, 'spotify_rank']
    df.at[index, 'weighted_average_total_rank'] = second_block.at[index, 'weighted_average_total_rank']

# Third block: separate votes for televotes and jury
third_block = df[df['year'] >= 2016]
views_sum_total = third_block['views'].sum()
third_block['fraction_of_views'] = third_block['views'] / views_sum_total
third_block['view_rank'] = third_block['fraction_of_views'].rank(ascending=False)

third_block['point_rank'] = third_block['fraction_of_total_points'].rank(ascending=False)
third_block['point_jury_rank'] = third_block['fraction_of_jury_points'].rank(ascending=False)
third_block['point_tele_rank'] = third_block['fraction_of_tele_points'].rank(ascending=False)
third_block['spotify_rank'] = third_block['spotify_popularity'].rank(ascending=False)

third_block['weighted_average_total_rank'] = (2 * (third_block['point_jury_rank'] + third_block['point_tele_rank']) + third_block['view_rank'] + third_block['spotify_rank']) / 6.0

for index in third_block.index.array:
    df.at[index, 'fraction_of_views'] = third_block.at[index, 'fraction_of_views']
    df.at[index, 'view_rank'] = third_block.at[index, 'view_rank']
    df.at[index, 'point_rank'] = third_block.at[index, 'point_rank']
    df.at[index, 'point_jury_rank'] = third_block.at[index, 'point_jury_rank']
    df.at[index, 'point_tele_rank'] = third_block.at[index, 'point_tele_rank']
    df.at[index, 'spotify_rank'] = third_block.at[index, 'spotify_rank']
    df.at[index, 'weighted_average_total_rank'] = third_block.at[index, 'weighted_average_total_rank']

correlations = df[['point_rank', 'point_jury_rank', 'point_tele_rank', 'view_rank', 'spotify_rank']].corr()
rank_correlations = df[['point_rank', 'point_jury_rank', 'point_tele_rank', 'view_rank', 'spotify_rank']].corr(method='spearman')
#tau_correlations = df[['point_rank', 'point_jury_rank', 'point_tele_rank', 'view_rank', 'spotify_rank']].corr(method='kendall')
print("Pearson correlation")
print(correlations)
print("Spearman rank correlation")
print(rank_correlations)

print("2004-2008")
print(first_block[['point_rank', 'point_jury_rank', 'point_tele_rank', 'view_rank', 'spotify_rank']].corr())
print("2009-2015")
print(second_block[['point_rank', 'point_jury_rank', 'point_tele_rank', 'view_rank', 'spotify_rank']].corr())
print("2016-2024")
print(third_block[['point_rank', 'point_jury_rank', 'point_tele_rank', 'view_rank', 'spotify_rank']].corr())

#print("Kendall's tau")
#print(tau_correlations)
df.to_csv('enriched-contestants2004-2024.csv', index=False)
df.sort_values(by=['weighted_average_total_rank']).to_csv('sorted-enriched-contestants2004-2024.csv', index=False)
