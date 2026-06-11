import math

def calculate_circle_area(radius: float) -> float:
    """
    Returns the area of a circle given its radius.
    """
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    return math.pi * (radius ** 2)

def main():
    user_radius = 5.0
    area = calculate_circle_area(user_radius)
    print(f"Area: {area}")

if __name__ == "__main__":
    main()
