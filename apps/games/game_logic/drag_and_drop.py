import random


def prepare_drag_drop_data(vocabulary_items, count=6):
    """
    Prepare vocabulary items for drag-and-drop game.
    Returns shuffled items for both images (draggables) and labels (targets).
    """
    items = list(vocabulary_items)
    if len(items) > count:
        items = random.sample(items, count)

    data = [
        {
            'id': item.id,
            'word_en': item.word_en,
            'word_es': item.word_es,
            'image': item.image.url if item.image else None,
        }
        for item in items
    ]

    shuffled_labels = data.copy()
    random.shuffle(shuffled_labels)

    return {
        'items': data,
        'shuffled_labels': shuffled_labels,
        'count': len(data),
    }


def calculate_score(correct, total, time_taken, time_limit):
    """Calculate score based on correctness and time."""
    if total == 0:
        return 0
    base = (correct / total) * 100
    # Time bonus: up to 20 extra points for speed
    if time_limit > 0 and time_taken < time_limit:
        time_bonus = ((time_limit - time_taken) / time_limit) * 20
    else:
        time_bonus = 0
    return int(base + time_bonus)
