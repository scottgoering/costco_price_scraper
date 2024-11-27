import re
from decimal import Decimal


def parse_product_string(text: str):
    """
    Parse a product string to extract item name, numbers, price, and savings.

    Args:
        text: Product string to parse

    Returns:
        List containing extracted information
    """
    # Remove the "Limit XX" at the end of the string
    limit_pattern = r'(,?\s?Limit.*)'
    text = re.sub(limit_pattern, '', text)

    # Pattern to match different price/savings formats at start of string
    price_pattern = r'^\$ (?:(\d+)(?: (\d+))? After \$(\d+) OFF|(\d+)(?: (\d+))? OFF) '

    # Pattern to match item numbers
    item_numbers_pattern = r'Item ((?:\d+(?:,\s*)?)+)'

    # Extract price/savings information
    price_match = re.match(price_pattern, text)

    price = None
    savings = None

    if price_match:
        groups = price_match.groups()
        if groups[2]:  # "After $X OFF" format
            dollars, cents = groups[0], groups[1]
            price = Decimal(f"{dollars}.{cents or '00'}")
            price = float(price)
            savings = Decimal(groups[2])
            savings = float(savings)
        elif groups[3]:  # "$X OFF" format
            savings = Decimal(groups[3])
            savings = float(savings)
            if groups[4]:  # If there are cents
                savings = Decimal(f"{groups[3]}.{groups[4]}")
                savings = float(savings)

    # Extract item numbers
    item_numbers_match = re.search(item_numbers_pattern, text)
    item_numbers = []
    if item_numbers_match:
        item_numbers = [num.strip() for num in item_numbers_match.group(1).split(',')]

    # Extract item name by removing the price/savings prefix and the Item numbers suffix
    name_text = re.sub(price_pattern, '', text)
    # name_text = re.sub(r'Item (?:\d+(?:,\s*)?)+(?:,\s*Limit \d+)?\.?$', '', name_text)
    name_text = re.sub(r'Item.*', '', name_text)
    item_name = name_text.strip()

    return item_name, item_numbers, price, savings


if __name__ == '__main__':
    # Test the parser with example strings
    test_strings = [
        "$ 5 OFF Frito-Lay Classic Mix Variety pack, 54 ct. Item 1627770, Limit 5.",
        "$ 29 99 After $7 OFF Keurig K-Cup Pods 80 ct. Item 3818035, 3281792, 3365592, 3704330, Limit 5.",
        "$ 4 30 OFF Ghirardelli Assorted Chocolates 23.6 oz. Item 1823485.",
        "$ 139 99 After $40 OFF Delsey Accelerate Luggage Set 2-Piece Hardside Luggage Set. Item 1819421, Limit 10."
    ]

    # Run tests
    for test_string in test_strings:
        item_name, item_numbers, price, savings = parse_product_string(test_string)
        print(f"\nInput: {test_string}")
        print(f"Item Name: {item_name}")
        print(f"Item Numbers: {', '.join(item_numbers)}")
        print(f"Item Price: ${price if price else 'NULL'}")
        print(f"Item Savings: ${savings if savings else 'NULL'}")
