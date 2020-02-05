ALL_METRICS = [
]

METRIC_NAMES_TO_CLASSES = {
}


def register_metric(cls):
    """
    Decorator to register your custom metrics
    """
    ALL_METRICS.append(cls)
    METRIC_NAMES_TO_CLASSES[cls.CLASS_NAME] = cls
    return cls
