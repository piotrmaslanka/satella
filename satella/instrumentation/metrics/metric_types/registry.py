METRIC_NAMES_TO_CLASSES = {
}

__all__ = ['METRIC_NAMES_TO_CLASSES', 'register_metric']


def register_metric(cls):
    """
    Decorator to register your custom metrics
    """
    METRIC_NAMES_TO_CLASSES[cls.CLASS_NAME] = cls
    return cls
