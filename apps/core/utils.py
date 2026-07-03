import os
import uuid
from django.utils import timezone
from django.conf import settings


def get_upload_path(instance, filename, folder='uploads'):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    return os.path.join(folder, filename)


def calculate_level(xp):
    thresholds = getattr(settings, 'LEVEL_THRESHOLDS', [0, 100, 250, 500, 1000, 2000, 3500, 5500, 8000, 12000, 20000])
    level = 1
    for i, threshold in enumerate(thresholds):
        if xp >= threshold:
            level = i + 1
    return min(level, len(thresholds))


def get_level_progress(xp):
    thresholds = getattr(settings, 'LEVEL_THRESHOLDS', [0, 100, 250, 500, 1000, 2000, 3500, 5500, 8000, 12000, 20000])
    level = calculate_level(xp)
    if level >= len(thresholds):
        return 100
    current_threshold = thresholds[level - 1]
    next_threshold = thresholds[level]
    if next_threshold == current_threshold:
        return 100
    progress = ((xp - current_threshold) / (next_threshold - current_threshold)) * 100
    return min(int(progress), 100)


def format_xp(xp):
    if xp >= 1000:
        return f'{xp / 1000:.1f}K'
    return str(xp)


def time_greeting():
    hour = timezone.localtime(timezone.now()).hour
    if hour < 12:
        return 'morning'
    elif hour < 17:
        return 'afternoon'
    return 'evening'
