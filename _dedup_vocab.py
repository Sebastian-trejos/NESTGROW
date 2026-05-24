"""
Elimina palabras duplicadas (misma word_en en varias categorías) del fixture.
Mantiene cada palabra en la categoría más adecuada.
"""
import json

with open('apps/content/fixtures/vocabulario_completo.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# ─────────────────────────────────────────────────────────────────
# PKs a ELIMINAR (duplicados en categoría menos apropiada)
# ─────────────────────────────────────────────────────────────────
ELIMINAR = {
    # Frutas que estaban en Food & Drinks → ahora existen en Cat 14 (Fruits)
    91,   # Apple   → Cat 14 PK 356
    92,   # Banana  → Cat 14 PK 357
    105,  # Orange  → Cat 14 PK 358  (el color Orange PK 47 se mantiene en Colors)
    106,  # Strawberry → Cat 14 PK 359
    107,  # Grape   → Cat 14 PK 360
    108,  # Watermelon → Cat 14 PK 361
    124,  # Lemon   → Cat 14 PK 365
    125,  # Mango   → Cat 14 PK 362
    126,  # Pineapple → Cat 14 PK 363
    127,  # Avocado → Cat 14 PK 375

    # Verduras que estaban en Food & Drinks → ahora existen en Cat 15 (Vegetables)
    109,  # Tomato  → Cat 15 PK 377
    110,  # Carrot  → Cat 15 PK 376
    111,  # Potato  → Cat 15 PK 378
    118,  # Corn    → Cat 15 PK 382

    # Fish: animal principal en Cat 1; el homónimo como comida es confuso para primaria
    99,   # Fish (food) → Cat 1 PK 7 se mantiene

    # School → más adecuados en otras categorías
    199,  # Teacher → Cat 20 (Professions) PK 452
    208,  # Chair   → Cat 9  (House) PK 230
    217,  # Library → Cat 21 (Places) PK 469

    # Adjectives → más adecuados en Emotions
    333,  # Happy → Cat 18 PK 422
    334,  # Sad   → Cat 18 PK 423

    # Nature & Weather → más adecuados en otras categorías
    261,  # Beach → Cat 21 (Places) PK 472
    271,  # Star  → Cat 16 (Shapes) PK 395

    # Shapes → más adecuado en Body Parts
    396,  # Heart → Cat 6 (Body Parts) PK 175
}

# ─────────────────────────────────────────────────────────────────
# PKs cuyo is_unlocked_by_default debe activarse para compensar
# los eliminados que tenían default=True
# ─────────────────────────────────────────────────────────────────
ACTIVAR_DEFAULT = {
    96,   # Rice  (Cat 4 Food) — compensa Apple y Banana eliminados
    97,   # Egg   (Cat 4 Food)
    201,  # Notebook (Cat 8 School) — compensa Teacher eliminado
    336,  # Slow  (Cat 13 Adjectives) — compensa Happy y Sad eliminados
    337,  # Hot   (Cat 13 Adjectives)
}

# ─────────────────────────────────────────────────────────────────
# Aplicar cambios
# ─────────────────────────────────────────────────────────────────
original_count = sum(1 for e in data if e['model'] == 'content.vocabularyitem')

new_data = []
activated = []
removed = []

for entry in data:
    if entry['model'] == 'content.vocabularyitem':
        pk = entry['pk']
        if pk in ELIMINAR:
            removed.append((pk, entry['fields']['word_en'], entry['fields']['category']))
            continue  # No incluir en el nuevo fixture
        if pk in ACTIVAR_DEFAULT:
            entry['fields']['is_unlocked_by_default'] = True
            activated.append((pk, entry['fields']['word_en']))
    new_data.append(entry)

with open('apps/content/fixtures/vocabulario_completo.json', 'w', encoding='utf-8') as f:
    json.dump(new_data, f, ensure_ascii=False, indent=2)

new_count = sum(1 for e in new_data if e['model'] == 'content.vocabularyitem')

print(f'Items originales: {original_count}')
print(f'Items eliminados: {len(removed)}')
print(f'Items finales:    {new_count}')
print()
print('Eliminados:')
for pk, word, cat in sorted(removed):
    print(f'  PK {pk:4d}  {word:<20} (cat {cat})')
print()
print('Activados como default unlock:')
for pk, word in activated:
    print(f'  PK {pk:4d}  {word}')
