from decimal import Decimal, ROUND_HALF_UP, ROUND_FLOOR


def round_currency(value):
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def round_reading(value):
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def select_rate_card(month):
    if month < 1 or month > 12:
        raise ValueError("Month must be between 1 and 12.")

    if 4 <= month <= 6:
        return {
            "season": "APRIL_TO_JUNE",
            "base_rate": Decimal("32.00"),
            "fat_step_size": Decimal("0.10"),
            "fat_step_rate": Decimal("0.45"),
            "baseline_fat": Decimal("3.50"),
            "snf_step_size": Decimal("0.10"),
            "snf_step_rate": Decimal("0.20"),
            "baseline_snf": Decimal("8.50"),
        }

    return {
        "season": "STANDARD",
        "base_rate": Decimal("30.00"),
        "fat_step_size": Decimal("0.10"),
        "fat_step_rate": Decimal("0.40"),
        "baseline_fat": Decimal("3.50"),
        "snf_step_size": Decimal("0.10"),
        "snf_step_rate": Decimal("0.20"),
        "baseline_snf": Decimal("8.50"),
    }


def calculate_steps(reading, baseline, step_size):
    if reading <= baseline:
        return 0
    diff = reading - baseline
    steps = (diff / step_size).quantize(Decimal("1"), rounding=ROUND_FLOOR)
    return int(steps)


def calculate_ten_day_bonus(total_litres_ten_days):
    if total_litres_ten_days > Decimal("500.00"):
        return round_currency(total_litres_ten_days * Decimal("0.50"))
    return Decimal("0.00")


def calculate_milk_payout(litres, fat, snf, month, ten_day_total_litres):
    q_litres = round_reading(litres)
    q_fat = round_reading(fat)
    q_snf = round_reading(snf)
    q_ten_day_litres = round_reading(ten_day_total_litres)

    rate_card = select_rate_card(month)
    fat_steps = calculate_steps(
        q_fat, rate_card["baseline_fat"], rate_card["fat_step_size"]
    )
    snf_steps = calculate_steps(
        q_snf, rate_card["baseline_snf"], rate_card["snf_step_size"]
    )

    per_litre_rate = (
        rate_card["base_rate"]
        + (Decimal(fat_steps) * rate_card["fat_step_rate"])
        + (Decimal(snf_steps) * rate_card["snf_step_rate"])
    )
    milk_amount = round_currency(q_litres * per_litre_rate)
    ten_day_bonus = calculate_ten_day_bonus(q_ten_day_litres)

    return {
        "season": rate_card["season"],
        "month": month,
        "litres": q_litres,
        "fat": q_fat,
        "snf": q_snf,
        "fat_steps": fat_steps,
        "snf_steps": snf_steps,
        "per_litre_rate": round_currency(per_litre_rate),
        "milk_amount": milk_amount,
        "ten_day_total_litres": q_ten_day_litres,
        "ten_day_bonus": ten_day_bonus,
        "gross_payout_with_bonus": round_currency(milk_amount + ten_day_bonus),
    }


def main():
    test_cases = [
        ("TC1_April_Bonus", "60.00", "4.25", "8.70", 4, "540.00"),
        ("TC2_June_Exact500L_NoBonus", "50.00", "4.10", "8.50", 6, "500.00"),
        ("TC3_July_Standard_Bonus", "55.00", "4.25", "8.60", 7, "505.50"),
        ("TC4_January_Standard_NoBonus", "40.00", "3.50", "8.50", 1, "380.00"),
    ]

    for name, litres, fat, snf, month, ten_day_litres in test_cases:
        res = calculate_milk_payout(litres, fat, snf, month, ten_day_litres)
        print(
            name,
            "| Season:", res["season"],
            "| Fat:", res["fat"], "(steps:", res["fat_steps"], ")",
            "| SNF:", res["snf"], "(steps:", res["snf_steps"], ")",
            "| Rate: Rs", res["per_litre_rate"],
            "| Milk: Rs", res["milk_amount"],
            "| Bonus: Rs", res["ten_day_bonus"],
            "| Total: Rs", res["gross_payout_with_bonus"],
        )


if __name__ == "__main__":
    main()
