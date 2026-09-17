import numpy as np


def effective_staggering_ratio(config: dict) -> float:
    """Return the user-requested overlap ratio clamped to a valid range."""
    ratio = float(config.get("staggering_ratio", 0.75))
    return min(max(ratio, 0.0), 1.0)


def build_schedule_start_months(config: dict, durations, startup_durations=None) -> np.ndarray:
    """Return plant start months with monotonic project finish dates.

    Plants are nominally staggered by ``1 - staggering_ratio`` of the previous
    construction duration. If a later plant would finish construction or finish
    startup before the previous plant, its start is delayed until the earlier
    finish date is tied.
    """
    durations = np.array(durations, dtype=float)
    if startup_durations is None:
        startup_durations = np.zeros(len(durations), dtype=float)
    else:
        startup_durations = np.array(startup_durations, dtype=float)

    ratio = effective_staggering_ratio(config)
    starts = np.zeros(len(durations), dtype=float)
    for idx in range(1, len(durations)):
        nominal_start = starts[idx - 1] + (1.0 - ratio) * durations[idx - 1]
        previous_construction_finish = starts[idx - 1] + durations[idx - 1]
        previous_startup_finish = previous_construction_finish + startup_durations[idx - 1]
        construction_tie_start = previous_construction_finish - durations[idx]
        startup_tie_start = previous_startup_finish - durations[idx] - startup_durations[idx]
        nominal_start = max(nominal_start, construction_tie_start, startup_tie_start)
        starts[idx] = max(nominal_start, 0.0)
    return starts


def build_schedule_timeline(config: dict, plant_numbers, durations, startup_durations) -> dict[str, np.ndarray]:
    """Return timeline arrays with corrected start and finish dates."""
    plant_numbers = np.array(plant_numbers, dtype=int)
    durations = np.array(durations, dtype=float)
    startup_durations = np.array(startup_durations, dtype=float)
    starts = build_schedule_start_months(config, durations, startup_durations)
    construction_finish = starts + durations
    startup_finish = construction_finish + startup_durations
    return {
        "plant_number": plant_numbers,
        "construction_start_month": starts,
        "construction_duration_months": durations,
        "construction_finish_month": construction_finish,
        "startup_duration_months": startup_durations,
        "startup_finish_month": startup_finish,
    }
