ROOT_ROLE_NAME = "Root"
SYSTEM_ROLE_NAME = "System"
ADMIN_ROLE_NAME = "Admin"
APP_USER_ROLE_NAME = "AppUser"

# Root and Admin can see/manage other users (GET /user/all, POST /user/info).
USER_MANAGEMENT_ROLE_NAMES = {ROOT_ROLE_NAME, ADMIN_ROLE_NAME}

# Word pools for auto-generated usernames (adjective + fruit/vegetable, no
# space) and passwords (one word + three digits). First block of each list
# is localsend's alias generator (github.com/localsend/localsend), the rest
# is added here to widen the pool so collisions stay rare.
USERNAME_ADJECTIVES = [
    "Adorable", "Beautiful", "Big", "Bold", "Brave", "Breezy", "Bright",
    "Calm", "Cheerful", "Chill", "Clean", "Clever", "Cool", "Cunning",
    "Curious", "Cute", "Dazzling", "Determined", "Dreamy", "Eager", "Efficient",
    "Energetic", "Fantastic", "Fast", "Fine", "Fluffy", "Fresh", "Friendly",
    "Gentle", "Giggly", "Good", "Gorgeous", "Great", "Handsome", "Happy",
    "Hot", "Jolly", "Jumpy", "Kind", "Lovely", "Merry", "Mystic",
    "Neat", "Nice", "Patient", "Playful", "Powerful", "Pretty", "Rich",
    "Secret", "Silly", "Smart", "Solid", "Sparkly", "Special", "Speedy",
    "Strategic", "Strong", "Sturdy", "Sunny", "Swift", "Tidy", "Tiny",
    "Vivid", "Wise", "Witty", "Zesty", "Zippy",
]

USERNAME_FRUITS_AND_VEGETABLES = [
    "Apple", "Avocado", "Banana", "Beet", "Blackberry", "Blueberry", "Broccoli",
    "Cabbage", "Carrot", "Celery", "Cherry", "Coconut", "Corn", "Cucumber",
    "Eggplant", "Fig", "Grape", "Guava", "Kale", "Kiwi", "Leek",
    "Lemon", "Lettuce", "Mango", "Melon", "Mushroom", "Onion", "Orange",
    "Papaya", "Parsnip", "Pea", "Peach", "Pear", "Pepper", "Pineapple",
    "Plum", "Potato", "Pumpkin", "Radish", "Raspberry", "Spinach", "Squash",
    "Strawberry", "Tomato", "Turnip", "Zucchini",
]
