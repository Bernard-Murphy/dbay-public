"""
Shared seed constants for dbay. Use deterministic UUIDs and fixed usernames
so user-service and listing-service seeds stay in sync.
"""
import uuid

# Deterministic UUIDs for 100 seed users (same every run)
SEED_USER_IDS = [str(uuid.uuid5(uuid.NAMESPACE_DNS, f"dbay.seed.user.{i}")) for i in range(100)]

# Fixed list of 100 realistic usernames (deterministic from word + number)
SEED_USERNAME_WORDS = [
    "surfer", "skate", "bookworm", "gamer", "travel", "music", "art", "tech",
    "vintage", "craft", "fitness", "chef", "photo", "garden", "motor", "wave",
    "star", "river", "mountain", "ocean", "sunny", "cosmic", "lucky", "bold",
]
SEED_USERNAMES = [f"{SEED_USERNAME_WORDS[i % len(SEED_USERNAME_WORDS)]}{10 + i}" for i in range(100)]
