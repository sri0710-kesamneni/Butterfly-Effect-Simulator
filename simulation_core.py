import numpy as np

def simulate_mm_s(n_customers, arrival_rate, proxy_service_mean, counters, seed=42):
    """Simple FCFS multi-counter what-if. Service time is a proxy assumption."""
    if n_customers < 1 or arrival_rate <= 0 or proxy_service_mean <= 0 or counters < 1:
        raise ValueError("n_customers, rates, durations, and counters must be positive.")
    rng = np.random.default_rng(seed)
    interarrivals = rng.exponential(1 / arrival_rate, size=n_customers)
    arrivals = np.cumsum(interarrivals)
    # Exponential service is a deliberately simple M/M/s assumption.
    services = rng.exponential(proxy_service_mean, size=n_customers)
    available = np.zeros(counters)
    waits = np.zeros(n_customers)
    for i, (arrival, service) in enumerate(zip(arrivals, services)):
        j = int(np.argmin(available))
        start = max(arrival, available[j])
        waits[i] = start - arrival
        available[j] = start + service
    return waits
