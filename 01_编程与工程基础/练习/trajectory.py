import math

def validate_sample(t_s, q):
    def judge_number(x):
        return (
            not isinstance(x, bool)
            and isinstance(x, (int, float))
            and math.isfinite(x)
        )

    if not judge_number(t_s) or t_s <0:
        raise ValueError("t_s must be finite int/float and not bool")
    if not isinstance(q, (list, tuple)) or len(q) != 2:
        raise ValueError("q must cotain two joint postions")
    if not all(judge_number(x) for x in q):
        raise ValueError("q must contain finite numbers")

    return float(t_s), [float(x) for x in q]

