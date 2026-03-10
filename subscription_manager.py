"""
Subscription Manager for ID Card Printer
Handles subscription status checks and expiry notifications
"""

import json
from datetime import date, datetime


def load_config():
    """Load configuration from config.json"""
    with open('config.json', 'r') as f:
        return json.load(f)


def get_subscription_status(config=None):
    """
    Check the current subscription status.

    Returns a dict with keys:
        active (bool): True if subscription is currently valid
        expired (bool): True if the expiry date has passed
        expiry_date (date | None): Parsed expiry date, or None if not set
        days_remaining (int | None): Days until expiry (negative when expired)
        message (str): Human-readable status message
    """
    if config is None:
        config = load_config()

    sub = config.get('subscription', {})
    active_flag = sub.get('active', True)
    expiry_str = sub.get('expiry_date', '')

    expiry_date = None
    days_remaining = None
    expired = False

    if expiry_str:
        try:
            expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d').date()
            today = date.today()
            days_remaining = (expiry_date - today).days
            expired = days_remaining < 0
        except ValueError:
            pass

    active = active_flag and not expired

    if not active_flag:
        message = "Subscription is inactive. Please renew to continue printing."
    elif expired:
        message = (
            f"Subscription expired on {expiry_date.strftime('%B %d, %Y')}. "
            "Please renew to continue printing."
        )
    elif days_remaining is not None and days_remaining <= 30:
        message = (
            f"Subscription expires in {days_remaining} day(s) "
            f"({expiry_date.strftime('%B %d, %Y')}). Please renew soon."
        )
    elif expiry_date:
        message = f"Subscription active. Expires {expiry_date.strftime('%B %d, %Y')}."
    else:
        message = "Subscription active."

    return {
        'active': active,
        'expired': expired,
        'expiry_date': expiry_date,
        'days_remaining': days_remaining,
        'message': message,
    }


def check_subscription_or_raise(config=None):
    """
    Raise a RuntimeError when the subscription is not active.
    Call this before performing any licensed operation (e.g. printing).
    """
    status = get_subscription_status(config)
    if not status['active']:
        raise RuntimeError(status['message'])


if __name__ == "__main__":
    status = get_subscription_status()
    print("=" * 60)
    print("Subscription Status")
    print("=" * 60)
    print(f"Active:         {status['active']}")
    if status['expiry_date']:
        print(f"Expiry Date:    {status['expiry_date'].strftime('%B %d, %Y')}")
    if status['days_remaining'] is not None:
        print(f"Days Remaining: {status['days_remaining']}")
    print(f"Message:        {status['message']}")
    print("=" * 60)
