from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=3,          # Number of iterations
    memory_cost=65536,    # Memory usage in KiB (64MB)
    parallelism=4,        # Number of parallel threads
    hash_len=32,          # Hash output length in bytes
    salt_len=16           # Salt length in bytes
)
