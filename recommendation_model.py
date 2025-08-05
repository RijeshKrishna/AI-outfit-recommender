import pandas as pd
import os # Import the os module for path manipulation

# --- Step 1: Load the Data ---
# Using forward slashes for better cross-platform compatibility
csv_directory = r'C:/Vs Code/Fashion Project/outfit recommender'
csv_file_name = 'accurate_fashion_attributes.csv'
csv_file_path = os.path.join(csv_directory, csv_file_name)

print(f"Attempting to load CSV from: {csv_file_path}")

try:
    df = pd.read_csv(csv_file_path)
    print("CSV loaded successfully. First 5 rows:")
    print(df.head())
    print("\nDataFrame Info:")
    df.info()
except FileNotFoundError:
    print(f"Error: The file '{csv_file_path}' was not found.")
    print("Please ensure the file name and path are exactly correct.")
    print("Double-check for typos, extra spaces, or incorrect file extensions.")
    exit()
except Exception as e:
    print(f"An unexpected error occurred while loading the CSV: {e}")
    exit()

# --- Manual Data Correction/Validation (Important Note) ---
# It was observed that ID 21379 (Manchester United Men Solid Black Track Pants) has dress_type 'shirt'.
# This appears to be a data entry error. For accurate recommendations, this should be 'pants' or 'track pants'.
# If this were a real system, you'd implement data validation or a correction pipeline.
# For this demonstration, let's manually correct it in the DataFrame if it exists.
if 21379 in df['id'].values:
    original_dress_type = df.loc[df['id'] == 21379, 'dress_type'].iloc[0]
    if original_dress_type.lower() == 'shirt':
        df.loc[df['id'] == 21379, 'dress_type'] = 'track pants'
        print(f"\nCorrected dress_type for ID 21379 from '{original_dress_type}' to 'track pants' for demonstration purposes.")


# --- Step 2 & 3: Define Compatibility Rules and Recommendation Function ---

def recommend_outfit(item_id, df, num_recommendations_per_type=2):
    """
    Recommends complementary items to form an outfit based on a given item_id.

    Args:
        item_id (int): The 'id' of the item for which to recommend an outfit.
        df (pd.DataFrame): The DataFrame containing all clothing items and their attributes.
        num_recommendations_per_type (int): How many recommendations to provide for each
                                             complementary item type (e.g., pants, shoes).

    Returns:
        dict: A dictionary where keys are item types (e.g., 'shirts', 'pants', 'shoes')
              and values are lists of recommended item dictionaries.
              Returns None if the base item is not found.
    """
    if item_id not in df['id'].values:
        print(f"Error: Item with ID {item_id} not found in the dataset.")
        return None

    base_item = df[df['id'] == item_id].iloc[0]
    print(f"\n--- Base Item for Recommendation ---")
    print(f"Product: {base_item['productDisplayName']} (ID: {base_item['id']})")
    print(f"Type: {base_item['dress_type']}, Occasion: {base_item['occasion']}, Gender: {base_item['gender']}")

    recommendations = {
        'base_item': base_item.to_dict(),
        'recommended_items': {}
    }

    target_gender = base_item['gender']
    target_occasion = base_item['occasion']
    base_item_type = base_item['dress_type'].lower() # Convert to lowercase for easier matching

    # Comprehensive mapping of base item types to what they typically pair with
    item_type_pairings = {
        'shirt': ['pants', 'jeans', 'trousers', 'shorts', 'skirt'],
        't-shirt': ['pants', 'jeans', 'trousers', 'shorts', 'skirt'],
        'top': ['pants', 'jeans', 'trousers', 'shorts', 'skirt'],
        'blouse': ['pants', 'jeans', 'trousers', 'shorts', 'skirt'],
        'sweater': ['pants', 'jeans', 'trousers', 'shorts', 'skirt'],
        'jacket': ['shirt', 't-shirt', 'top', 'blouse', 'sweater', 'pants', 'jeans', 'trousers', 'shorts', 'skirt'],
        'pants': ['shirt', 't-shirt', 'top', 'blouse', 'sweater', 'jacket'],
        'jeans': ['shirt', 't-shirt', 'top', 'blouse', 'sweater', 'jacket'],
        'trousers': ['shirt', 't-shirt', 'top', 'blouse', 'sweater', 'jacket'],
        'shorts': ['shirt', 't-shirt', 'top', 'blouse', 'sweater'],
        'skirt': ['top', 'blouse', 'shirt', 't-shirt', 'sweater', 'jacket'],
        'dress': ['jacket', 'cardigan'],
        'jumpsuit': ['jacket', 'cardigan'],
        'track pants': ['t-shirt', 'shirt', 'hoodie', 'sports bra'],
        'garment': ['shirt', 't-shirt', 'top', 'blouse', 'sweater', 'jacket', 'pants', 'jeans', 'trousers', 'shorts', 'skirt', 'dress', 'jumpsuit', 'shoes', 'accessories'],
        'watch': ['shirt', 't-shirt', 'top', 'blouse', 'sweater', 'jacket', 'pants', 'jeans', 'trousers', 'shorts', 'skirt', 'dress', 'jumpsuit', 'shoes', 'accessory'],
        'shoes': ['pants', 'jeans', 'trousers', 'shorts', 'skirt', 'dress', 'jumpsuit'],
        'accessory': ['shirt', 't-shirt', 'top', 'blouse', 'sweater', 'jacket', 'pants', 'jeans', 'trousers', 'shorts', 'skirt', 'dress', 'jumpsuit', 'shoes', 'watch']
    }

    complementary_types_to_find = []
    found_pairing = False
    for key, value in item_type_pairings.items():
        if key in base_item_type:
            complementary_types_to_find.extend(value)
            found_pairing = True
            break
    if not found_pairing:
        if 'shoes' not in base_item_type and 'accessory' not in base_item_type and 'watch' not in base_item_type:
            complementary_types_to_find.extend(['shirt', 't-shirt', 'top', 'blouse', 'sweater', 'jacket', 'pants', 'jeans', 'trousers', 'shorts', 'skirt', 'dress', 'jumpsuit'])

    if 'shoes' not in base_item_type:
        complementary_types_to_find.append('shoes')
    if 'watch' not in base_item_type and 'accessory' not in base_item_type:
        complementary_types_to_find.append('accessory')

    complementary_types_to_find = list(set(complementary_types_to_find))
    if base_item_type in complementary_types_to_find:
        complementary_types_to_find.remove(base_item_type)

    print(f"Looking for complementary types: {complementary_types_to_find}")

    for item_type_to_find in complementary_types_to_find:
        candidates = df[
            (df['gender'].str.contains(target_gender, case=False, na=False) | df['gender'].str.contains('unisex', case=False, na=False)) &
            (df['occasion'].str.contains(target_occasion, case=False, na=False) | df['occasion'].str.contains('general', case=False, na=False)) &
            (df['dress_type'].str.contains(item_type_to_find, case=False, na=False)) &
            (df['id'] != item_id)
        ].copy()

        base_colors = [c.strip().lower() for c in base_item['colors'].split(',') if c.strip()]
        neutral_colors = ['black', 'white', 'grey', 'gray', 'beige', 'brown', 'navy']

        def check_color_compatibility(candidate_colors_str, base_colors, neutral_colors):
            candidate_colors = [c.strip().lower() for c in candidate_colors_str.split(',') if c.strip()]
            if any(c in neutral_colors for c in base_colors) or any(c in neutral_colors for c in candidate_colors):
                return True
            if any(c in base_colors for c in candidate_colors):
                return True
            return True # Fallback

        if not candidates.empty:
            candidates['color_compatible'] = candidates['colors'].apply(lambda x: check_color_compatibility(x, base_colors, neutral_colors))
            candidates = candidates[candidates['color_compatible']].drop(columns=['color_compatible'])

        if not candidates.empty:
            recommended_items = candidates.sample(min(num_recommendations_per_type, len(candidates))).to_dict(orient='records')
            recommendations['recommended_items'][item_type_to_find + 's'] = recommended_items

    return recommendations

# --- Example Usage ---

# Example 1: Recommend an outfit based on a Men's Shirt (ID 15970)
recommended_outfit_1 = recommend_outfit(15970, df)
if recommended_outfit_1:
    print("\n--- Outfit Recommendation for ID 15970 (Men's Navy Blue Shirt) ---")
    print(f"Base Item: {recommended_outfit_1['base_item']['productDisplayName']}")
    for item_type, items in recommended_outfit_1['recommended_items'].items():
        if items:
            print(f"  {item_type.capitalize()}:")
            for item in items:
                print(f"    - {item['productDisplayName']} (ID: {item['id']}) - Type: {item['dress_type']}, Colors: {item['colors']}")
        else:
            print(f"  No {item_type.capitalize()} recommendations found.")

print("\n" + "="*50 + "\n")

# Example 2: Recommend an outfit based on Women's Watch (ID 59263) - expecting more general items
recommended_outfit_2 = recommend_outfit(59263, df)
if recommended_outfit_2:
    print("\n--- Outfit Recommendation for ID 59263 (Titan Women Silver Watch) ---")
    print(f"Base Item: {recommended_outfit_2['base_item']['productDisplayName']}")
    for item_type, items in recommended_outfit_2['recommended_items'].items():
        if items:
            print(f"  {item_type.capitalize()}:")
            for item in items:
                print(f"    - {item['productDisplayName']} (ID: {item['id']}) - Type: {item['dress_type']}, Colors: {item['colors']}")
        else:
            print(f"  No {item_type.capitalize()} recommendations found.")

print("\n" + "="*50 + "\n")

# Example 3: Recommend an outfit based on Track Pants (ID 21379) - now with corrected dress_type
recommended_outfit_3 = recommend_outfit(21379, df)
if recommended_outfit_3:
    print("\n--- Outfit Recommendation for ID 21379 (Manchester United Men Solid Black Track Pants) ---")
    print(f"Base Item: {recommended_outfit_3['base_item']['productDisplayName']}")
    for item_type, items in recommended_outfit_3['recommended_items'].items():
        if items:
            print(f"  {item_type.capitalize()}:")
            for item in items:
                print(f"    - {item['productDisplayName']} (ID: {item['id']}) - Type: {item['dress_type']}, Colors: {item['colors']}")
        else:
            print(f"  No {item_type.capitalize()} recommendations found.")