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

# 7. Generate and save visualization
print("\nGenerating visualization...")
sns.set_style("whitegrid")

age_groups = top_books_per_age_group['Age_Group'].unique()

# Filter out None/NaN age groups if any exist from pd.cut
age_groups = [group for group in age_groups if pd.notna(group)]

if not age_groups:
    print("No valid age groups found to visualize. Please check the data and age binning.")
else:
    fig, axes = plt.subplots(nrows=len(age_groups), ncols=1, figsize=(10, 6 * len(age_groups)))
    fig.suptitle('Top 5 Recommended Books per Age Group', fontsize=16, y=1.02)

    if len(age_groups) == 1:
        axes = [axes] # Ensure axes is iterable even for a single subplot

    for i, age_group in enumerate(age_groups):
        ax = axes[i]
        data = top_books_per_age_group[top_books_per_age_group['Age_Group'] == age_group].sort_values(by='avg_rating', ascending=True)

        sns.barplot(x='avg_rating', y='Book-Title', data=data, palette='viridis', ax=ax)
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
    output_filename = 'book_recommendations_by_age.png'
    plt.savefig(output_filename)
    print(f"Visualization saved successfully as {output_filename}")
    plt.close(fig) # Close the plot to free up memory
