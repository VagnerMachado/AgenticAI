# Fix for printing search results from WebSearchItem objects
# The correct way to access the attributes is directly on the search object

# Example of the problematic code (what you want to fix):
# for search in result.final_output.searches:
#     print(search.query.reason)  # WRONG - this tries to access .reason on the query string
#     print(search.query.query)   # WRONG - this tries to access .query on the query string
#     print("-" * 50)

# Corrected code:
for search in result.final_output.searches:
    print(f"reason: {search.reason}")
    print(f"query: {search.query}")
    print("-" * 50)

# Explanation:
# - search is a WebSearchItem object
# - search.reason gives you the reason string
# - search.query gives you the query string
# - The original code was trying to access .reason and .query on the query string itself, which doesn't exist 