from pytrends.request import TrendReq
import socket

# Hard timeout for ALL sockets (critical on Windows)
socket.setdefaulttimeout(10)


def get_trend_score(keyword: str, country: str):
    try:
        pytrends = TrendReq(hl="en-US", tz=360, timeout=(5, 10))
        pytrends.build_payload(
            [keyword],
            timeframe="today 30-d",
            geo=country,
        )

        df = pytrends.interest_over_time()

        if df.empty:
            return {
                "trend_score": 0,
                "trend_direction": "stable",
                "avg_interest": 0,
                "samples": 0,
            }

        values = df[keyword].tolist()
        avg_interest = sum(values) / len(values)

        direction = (
            "rising" if values[-1] > values[0]
            else "falling" if values[-1] < values[0]
            else "stable"
        )

        return {
            "trend_score": round(avg_interest),
            "trend_direction": direction,
            "avg_interest": round(avg_interest, 2),
            "samples": len(values),
        }

    except Exception as e:
        # FAIL FAST — NEVER BLOCK PIPELINE
        return {
            "trend_score": None,
            "trend_direction": "error",
            "avg_interest": None,
            "samples": 0,
        }
