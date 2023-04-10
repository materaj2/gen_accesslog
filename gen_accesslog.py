import sys
import argparse
import random
from datetime import datetime, timedelta
import os
import requests
from faker import Faker

# Initialize the Faker library
fake = Faker()

# Add sample referrers and user-agents
referrers = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://www.yahoo.com/",
    "https://www.facebook.com/",
    "https://twitter.com/",
    "-"
]

def generate_normal_log(domain):
    pages = ["/index.php", "/about.php", "/contact.php", "/products.php", "/login.php", "/register.php"]
    ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    timestamp = datetime.now().strftime("%d/%b/%Y:%H:%M:%S %z")
    method = random.choice(["GET", "POST"])
    page = random.choice(pages)
    status_code = random.choice([200, 404, 500])
    referrer = random.choice(referrers)
    user_agent = fake.user_agent()
    return f'{ip} - - [{timestamp}] "{method} {page} HTTP/1.1" {status_code} 0 "{referrer}" "{user_agent}"\n'


def generate_sql_injection_log(domain):
    injection_payloads = ["' OR '1'='1", "' OR 1=1 --", "' OR 1=1 /*", "' OR 1=1#", "' UNION SELECT * FROM users WHERE '1'='1"]
    ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    timestamp = datetime.now().strftime("%d/%b/%Y:%H:%M:%S %z")
    method = "GET"
    page = f"/index.php?id=1{random.choice(injection_payloads)}"
    status_code = 200
    referrer = random.choice(referrers)
    user_agent = fake.user_agent()
    return f'{ip} - - [{timestamp}] "{method} {page} HTTP/1.1" {status_code} 0 "{referrer}" "{user_agent}"\n'

def generate_local_file_inclusion_log(domain):
    lfi_payloads = ["../../../../etc/passwd", "../../../../var/log/access.log", "../../../../proc/self/environ"]
    ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    timestamp = datetime.now().strftime("%d/%b/%Y:%H:%M:%S %z")
    method = "GET"
    page = f"/index.php?file={random.choice(lfi_payloads)}"
    status_code = 200
    referrer = random.choice(referrers)
    user_agent = fake.user_agent()
    return f'{ip} - - [{timestamp}] "{method} {page} HTTP/1.1" {status_code} 0 "{referrer}" "{user_agent}"\n'

def generate_brute_force_log(domain):
    password_attempts = ["password", "123456", "admin", "letmein", "welcome"]
    ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    timestamp = datetime.now().strftime("%d/%b/%Y:%H:%M:%S %z")
    method = "POST"
    page = "/login.php"
    status_code = random.choice([200, 401])
    referrer = random.choice(referrers)
    user_agent = fake.user_agent()
    return f'{ip} - - [{timestamp}] "{method} {page} HTTP/1.1" {status_code} 0 "{referrer}" "{user_agent}"\n'

def generate_log(attacks, normal_count, attack_count, domain):
    logs = []
    for _ in range(normal_count):
        logs.append(generate_normal_log(domain))

    for _ in range(attack_count):
        attack = random.choice(attacks)
        if attack == "sql_injection":
            logs.append(generate_sql_injection_log(domain))
        elif attack == "local_file_inclusion":
            logs.append(generate_local_file_inclusion_log(domain))
        elif attack == "brute_force":
            logs.append(generate_brute_force_log(domain))

    random.shuffle(logs)
    return logs

def main(args):
    attacks = args.attack_type.split(",")
    start_date = datetime.strptime(args.begin_date, "%Y-%m-%d")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    current_date = start_date

    # Create the output directory if it doesn't exist
    os.makedirs(args.output_path, exist_ok=True)

    while current_date <= end_date:
        with open(os.path.join(args.output_path, f"{current_date.strftime('%Y-%m-%d')}.log"), "w") as f:
            logs = generate_log(attacks, args.normal_events, args.attack_events, args.domain)
            for log in logs:
                f.write(log)
        current_date += timedelta(days=1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--attack_type", help="Type of attack: sql_injection, local_file_inclusion, brute_force (comma-separated)", default="sql_injection,local_file_inclusion,brute_force")
    parser.add_argument("-b", "--begin_date", help="Begin date in YYYY-MM-DD format", required=True)
    parser.add_argument("-e", "--end_date", help="End date in YYYY-MM-DD format", required=True)
    parser.add_argument("-d", "--domain", help="Domain of victim", required=True)
    parser.add_argument("-n", "--normal_events", help="Number of normal events", type=int, default=100)
    parser.add_argument("-a", "--attack_events", help="Number of attack events", type=int, default=100)
    parser.add_argument("-o", "--output_path", help="Output path for generated log files", default=".")
    args = parser.parse_args()
    main(args)
