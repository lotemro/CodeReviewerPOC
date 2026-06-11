def find_maximum_value(numbers: list[int]) -> int:
    """
    Finds and returns the maximum integer in a list.
    """
    if not numbers:
        raise ValueError("List is empty")
    
    current_max = numbers[0]
    for number in numbers:
        if number > current_max:
            current_max = number
    return current_max
