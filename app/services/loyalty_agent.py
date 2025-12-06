from ..domain.models import CustomerProfile


class LoyaltyAgent:
    def calculate_discount(self, customer: CustomerProfile, amount: float) -> float:
        tier_multiplier = {"bronze": 0.01, "silver": 0.02, "gold": 0.03, "platinum": 0.05}
        m = tier_multiplier.get(customer.loyalty_tier.lower(), 0.0)
        discount_from_tier = amount * m
        discount_from_points = min(customer.loyalty_points * 0.1, amount * 0.2)
        return round(discount_from_tier + discount_from_points, 2)
