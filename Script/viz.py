import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 1. Load the datasets
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data_source'))

df_books = pd.read_csv(os.path.join(base_dir, 'books.csv'), delimiter=';', encoding='latin-1', on_bad_lines='skip')
df_ratings = pd.read_csv(os.path.join(base_dir, 'ratings.csv'), delimiter=';', encoding='latin-1', on_bad_lines='skip')
df_users = pd.read_csv(os.path.join(base_dir, 'users.csv'), delimiter=';', encoding='latin-1', on_bad_lines='skip')

# 2. Merge the datasets
print("Merging DataFrames...")
df_merged = pd.merge(df_ratings, df_users, on='User-ID', how='inner')
df_merged = pd.merge(df_merged, df_books, on='ISBN', how='inner')
print("DataFrames merged successfully. Head of merged data:")
print(df_merged.head())

# 3. Clean and prepare the 'Age' column
print("\nCleaning and preparing 'Age' column...")
df_cleaned = df_merged.dropna(subset=['Age'])
df_cleaned['Age'] = df_cleaned['Age'].astype(int)
df_cleaned = df_cleaned[(df_cleaned['Age'] >= 5) & (df_cleaned['Age'] <= 100)]

# Create age groups
bins = [5, 10, 18, 25, 35, 50, 65, 100]
labels = ['5-9', '10-17', '18-24', '25-34', '35-49', '50-64', '65-100']
df_cleaned['Age_Group'] = pd.cut(df_cleaned['Age'], bins=bins, labels=labels, right=False)
print("Age column cleaned and grouped.")
print("Value counts for Age_Group:")
print(df_cleaned['Age_Group'].value_counts().sort_index())

# 4. Calculate average rating and rating count for each book within each age group
print("\nAggregating book ratings by age group...")
book_age_group_ratings = df_cleaned.groupby(['Age_Group', 'Book-Title']).agg(
    avg_rating=('Book-Rating', 'mean'),
    rating_count=('Book-Rating', 'count')
).reset_index()

# 5. Filter for books with a minimum number of ratings
min_ratings_threshold = 10
book_age_group_ratings_filtered = book_age_group_ratings[
    book_age_group_ratings['rating_count'] >= min_ratings_threshold
]

# Sort by average rating in descending order within each age group
book_age_group_ratings_filtered = book_age_group_ratings_filtered.sort_values(
    by=['Age_Group', 'avg_rating'], ascending=[True, False]
)
print(f"Filtered for books with at least {min_ratings_threshold} ratings.")

# 6. Get top N books per age group
top_n_books = 5
top_books_per_age_group = book_age_group_ratings_filtered.groupby('Age_Group').head(top_n_books)
print(f"\nTop {top_n_books} books per age group identified.")
print(top_books_per_age_group)

# 7. Generate and save visualization (Top 5 Recommended Books per Age Group)
print("\nGenerating visualization (Top 5 Recommended Books per Age Group)...")
sns.set_style("whitegrid")

age_groups = top_books_per_age_group['Age_Group'].unique()

# Filter out None/NaN age groups if any exist from pd.cut
age_groups = [group for group in age_groups if pd.notna(group)]

if not age_groups:
    print("No valid age groups found to visualize. Please check the data and age binning.")
else:
    fig1, axes1 = plt.subplots(nrows=len(age_groups), ncols=1, figsize=(10, 6 * len(age_groups)))
    fig1.suptitle('Top 5 Recommended Books per Age Group', fontsize=16, y=1.02)

    if len(age_groups) == 1:
        axes1 = [axes1] # Ensure axes is iterable even for a single subplot

    for i, age_group in enumerate(age_groups):
        ax = axes1[i]
        data = top_books_per_age_group[top_books_per_age_group['Age_Group'] == age_group].sort_values(by='avg_rating', ascending=True)

        # Changed palette to 'Blues' for a blue color scheme
        sns.barplot(x='avg_rating', y='Book-Title', data=data, palette='Blues', ax=ax)
        ax.set_title(f'Age Group: {age_group}', fontsize=14)
        ax.set_xlabel('Average Book Rating', fontsize=12)
        ax.set_ylabel('Book Title', fontsize=12)
        ax.tick_params(axis='x', labelsize=10)
        ax.tick_params(axis='y', labelsize=10)

        for p in ax.patches:
            width = p.get_width()
            ax.text(width + 0.1, p.get_y() + p.get_height() / 2, f'{width:.2f}', va='center')

    plt.tight_layout()
    
    # Save the figure as a PNG file
    output_filename1 = 'book_recommendations_by_age.png'
    plt.savefig(output_filename1)
    print(f"Visualization saved successfully as {output_filename1}")
    plt.close(fig1) # Close the plot to free up memory

# 8. Add visualization for User Rating Distribution
print("\nGenerating visualization (User Rating Distribution)...")
fig2, ax2 = plt.subplots(figsize=(10, 6))
# Changed palette to 'Blues' for a blue color scheme
sns.countplot(x='Book-Rating', data=df_ratings, palette='Blues', ax=ax2)
ax2.set_title('Distribution of User Book Ratings', fontsize=16)
ax2.set_xlabel('Book Rating', fontsize=12)
ax2.set_ylabel('Frequency', fontsize=12)
plt.tight_layout()
output_filename2 = 'user_rating_distribution.png'
plt.savefig(output_filename2)
print(f"Visualization saved successfully as {output_filename2}")
plt.close(fig2)

# 9. Add visualization for Heatmap of User-Book Interaction
print("\nGenerating visualization (Heatmap of User-Book Interaction)...")

# To make the heatmap manageable, let's sample a subset of users and books.
# We'll select users who have rated at least a certain number of books,
# and books that have received at least a certain number of ratings.
# Then, we'll take a random sample from these filtered users/books.

# Get users who have rated at least 20 books
user_rating_counts = df_merged['User-ID'].value_counts()
active_users = user_rating_counts[user_rating_counts >= 20].index

# Get books that have been rated at least 20 times
book_rating_counts = df_merged['ISBN'].value_counts()
popular_books = book_rating_counts[book_rating_counts >= 20].index

# Filter the merged DataFrame to include only active users and popular books
df_filtered_interaction = df_merged[
    df_merged['User-ID'].isin(active_users) &
    df_merged['ISBN'].isin(popular_books)
]

# Take a random sample of users and books from the filtered data for the heatmap
# This prevents the heatmap from being too dense and unreadable.
sample_users = df_filtered_interaction['User-ID'].sample(min(50, len(df_filtered_interaction['User-ID'].unique())), random_state=42).unique()
sample_books = df_filtered_interaction['Book-Title'].sample(min(30, len(df_filtered_interaction['Book-Title'].unique())), random_state=42).unique()

df_heatmap_sample = df_filtered_interaction[
    df_filtered_interaction['User-ID'].isin(sample_users) &
    df_filtered_interaction['Book-Title'].isin(sample_books)
]

if not df_heatmap_sample.empty:
    # Create a pivot table for the heatmap
    user_book_pivot = df_heatmap_sample.pivot_table(
        index='User-ID',
        columns='Book-Title',
        values='Book-Rating'
    )

    fig3, ax3 = plt.subplots(figsize=(15, 10))
    # Changed cmap to 'Blues' for a blue color scheme
    sns.heatmap(user_book_pivot, cmap='Blues', annot=False, fmt=".0f", linewidths=.5, ax=ax3)
    ax3.set_title('Heatmap of User-Book Interactions (Sampled)', fontsize=16)
    ax3.set_xlabel('Book Title', fontsize=12)
    ax3.set_ylabel('User ID', fontsize=12)
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    output_filename3 = 'user_book_interaction_heatmap.png'
    plt.savefig(output_filename3)
    print(f"Visualization saved successfully as {output_filename3}")
    plt.close(fig3)
else:
    print("Not enough data to generate a meaningful heatmap after sampling. Consider adjusting thresholds or sample size.")