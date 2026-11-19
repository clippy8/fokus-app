from datetime import date, timedelta


def week_date_range(iso_year, iso_week):
    start = date.fromisocalendar(iso_year, iso_week, 1)
    end = start + timedelta(days=6)
    return start, end


def previous_iso_week(iso_year, iso_week):
    start = date.fromisocalendar(iso_year, iso_week, 1)
    prev_day = start - timedelta(days=1)
    prev_year, prev_week, _ = prev_day.isocalendar()
    return prev_year, prev_week
