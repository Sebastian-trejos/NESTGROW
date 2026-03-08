import random


def prepare_audio_game(vocabulary_items, count=6):
    """Prepare items for audio matching game."""
    items = list(vocabulary_items.filter(audio__isnull=False))
    if len(items) < 3:
        # If no audio, still prepare visually with word display
        items = list(vocabulary_items)[:count]
    else:
        if len(items) > count:
            items = random.sample(items, count)

    data = []
    for item in items:
        data.append({
            'id': item.id,
            'word_en': item.word_en,
            'word_es': item.word_es,
            'audio': item.audio.url if item.audio else None,
            'image': item.image.url if item.image else None,
        })

    options = data.copy()
    random.shuffle(options)
    return {'items': data, 'options': options}
