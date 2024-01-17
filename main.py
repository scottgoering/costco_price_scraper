# from costco_price_scraper.price_scraper import price_scraper as ps

# ps.run_price_scraper()


import timeit
from costco_price_scraper.price_scraper import price_scraper as ps

# Wrap the function call in a lambda function
wrapped_function = lambda: ps.run_price_scraper()

# Run the timeit function
execution_time = timeit.timeit(wrapped_function, number=1)

# Print the execution time
print(f"Execution Time: {execution_time:.2f} seconds")
