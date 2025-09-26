from fake_useragent import UserAgent
import random


def generate_headers():
    ua = UserAgent(platforms="desktop")

    return {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": f"en-US,en;q=0.{random.randint(5,9)}",
        "Referer": random.choice(
            [
                "https://www.google.com/",
                "https://www.bing.com/",
                "https://duckduckgo.com/",
            ]
        ),
        "DNT": str(random.randint(0, 1)),
        "Upgrade-Insecure-Requests": "1",
        "Sec-Ch-Ua": '"Google Chrome";v="130", "Chromium";v="130", "Not?A_Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "Windows",
    }


#        'Sec-Ch-Ua-Platform': f'{random.choice(["Windows", "Linux", "Macintosh"])}',
if __name__ == "__main__":
    for i in range(1, 10):
        print(generate_headers())
