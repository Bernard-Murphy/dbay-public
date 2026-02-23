"""Seed constants: must match scripts/seed_constants.py and listing-service usage."""
import uuid

SEED_USER_IDS = [str(uuid.uuid5(uuid.NAMESPACE_DNS, f"dbay.seed.user.{i}")) for i in range(100)]
SEED_USERNAME_WORDS = [
    "surfer", "skate", "bookworm", "gamer", "travel", "music", "art", "tech",
    "vintage", "craft", "fitness", "chef", "photo", "garden", "motor", "wave",
    "star", "river", "mountain", "ocean", "sunny", "cosmic", "lucky", "bold",
]
SEED_USERNAMES = [f"{SEED_USERNAME_WORDS[i % len(SEED_USERNAME_WORDS)]}{10 + i}" for i in range(100)]
