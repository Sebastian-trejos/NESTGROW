'use strict';

// ══════════════════════════════════════════════════════════════════════════════
// BASE DE FRASES
// Clave : word_en en minúsculas.
// Valor : plantilla de frase. {word} se reemplaza por el span resaltado en rojo.
//
// Las IMÁGENES de las tarjetas vienen directamente de los ítems de vocabulario
// de la categoría asignada al juego (campo `image` de VocabularyItem).
// Si un ítem no tiene imagen se muestra un placeholder visual con su etiqueta ES.
// ══════════════════════════════════════════════════════════════════════════════
const SENTENCES_DB = {

  // ── EMOCIONES ──────────────────────────────────────────────────────────────
  'sad':          'Milo is {word} today',
  'happy':        'Milo is very {word}',
  'angry':        'Milo is feeling {word}',
  'scared':       'Milo is {word} of the dark',
  'surprised':    'Milo is {word} by the gift',
  'excited':      'Milo is very {word} today',
  'tired':        'Milo is so {word} after class',
  'bored':        'Milo feels {word} at home',
  'sick':         'Milo is {word} today',
  'hungry':       'Milo is {word} for lunch',
  'thirsty':      'Milo is very {word}',
  'worried':      'Milo is {word} about the test',
  'confused':     'Milo is {word} by the puzzle',
  'proud':        'Milo is {word} of his work',
  'shy':          'Milo feels {word} today',

  // ── ACCIONES ───────────────────────────────────────────────────────────────
  'run':          'Milo loves to {word}',
  'running':      'Milo is {word} very fast',
  'jump':         'Milo can {word} very high',
  'jumping':      'Milo is {word} over a puddle',
  'swim':         'Milo can {word} in the lake',
  'swimming':     'Milo is {word} in the pool',
  'eat':          'Milo wants to {word} now',
  'eating':       'Milo is {word} his lunch',
  'sleep':        'Milo needs to {word} early',
  'sleeping':     'Milo is {word} in his bed',
  'read':         'Milo likes to {word} books',
  'reading':      'Milo is {word} a story',
  'dance':        'Milo loves to {word}',
  'dancing':      'Milo is {word} to the music',
  'sing':         'Milo can {word} really well',
  'singing':      'Milo is {word} a song',
  'fly':          'Milo dreams to {word} high',
  'flying':       'Milo is {word} in the sky',
  'write':        'Milo has to {word} a letter',
  'writing':      'Milo is {word} in his notebook',
  'study':        'Milo needs to {word} today',
  'studying':     'Milo is {word} for the test',
  'play':         'Milo wants to {word} outside',
  'playing':      'Milo is {word} with his ball',
  'paint':        'Milo likes to {word} pictures',
  'painting':     'Milo is {word} a portrait',
  'cook':         'Milo can {word} delicious meals',
  'cooking':      'Milo is {word} dinner',
  'think':        'Milo needs to {word} hard',
  'thinking':     'Milo is {word} of a new idea',
  'walk':         'Milo likes to {word} to school',
  'walking':      'Milo is {word} to the park',
  'laugh':        'Milo starts to {word}',
  'laughing':     'Milo is {word} very loud',
  'cry':          'Milo begins to {word}',
  'crying':       'Milo is {word} a little',
  'listen':       'Milo has to {word} carefully',
  'listening':    'Milo is {word} to music',
  'talk':         'Milo likes to {word} with friends',
  'draw':         'Milo loves to {word} animals',
  'drawing':      'Milo is {word} a wolf',
  'help':         'Milo wants to {word} his friend',
  'helping':      'Milo is {word} in class',

  // ── ANIMALES ───────────────────────────────────────────────────────────────
  'dog':          'The {word} is barking loudly',
  'cat':          'The {word} is sleeping on the sofa',
  'lion':         'The {word} is very strong',
  'elephant':     'The {word} has a long nose',
  'butterfly':    'The {word} is flying in the garden',
  'bird':         'The {word} can fly very high',
  'fish':         'The {word} lives in the water',
  'bear':         'The {word} is sleeping in a cave',
  'rabbit':       'The {word} is jumping very fast',
  'snake':        'The {word} is on the ground',
  'tiger':        'The {word} is running in the jungle',
  'monkey':       'The {word} is eating a banana',
  'frog':         'The {word} is jumping in the pond',
  'horse':        'The {word} is running very fast',
  'turtle':       'The {word} is walking very slow',
  'bee':          'The {word} is flying to a flower',
  'cow':          'The {word} is eating grass',
  'pig':          'The {word} is sleeping in the mud',
  'duck':         'The {word} is swimming in the pond',
  'penguin':      'The {word} is swimming in cold water',
  'owl':          'The {word} is watching at night',
  'parrot':       'The {word} is repeating words',
  'wolf':         'The {word} is howling at the moon',
  'fox':          'The {word} is running in the forest',
  'deer':         'The {word} is running in the forest',
  'crocodile':    'The {word} is in the river',
  'giraffe':      'The {word} has a very long neck',
  'zebra':        'The {word} has black and white stripes',
  'shark':        'The {word} is swimming in the ocean',
  'dolphin':      'The {word} is jumping out of the water',

  // ── COLORES ────────────────────────────────────────────────────────────────
  'red':          'The apple is {word}',
  'blue':         'The sky is {word} today',
  'green':        'The grass is {word}',
  'yellow':       'The sun is {word}',
  'orange':       'The pumpkin is {word}',
  'purple':       'The flower is {word}',
  'pink':         'The flamingo is {word}',
  'white':        'The snow is {word} and cold',
  'black':        'The night sky is {word}',
  'brown':        'The bear is {word}',
  'gray':         'The elephant is {word}',
  'grey':         'The elephant is {word}',

  // ── NÚMEROS ────────────────────────────────────────────────────────────────
  'one':          'I can see {word} dog',
  'two':          'There are {word} birds flying',
  'three':        'Milo has {word} friends',
  'four':         'Milo counts {word} stars',
  'five':         'Milo finds {word} coins',
  'six':          'There are {word} flowers',
  'seven':        'Milo counts {word} butterflies',
  'eight':        'Milo reads {word} books',
  'nine':         'There are {word} dogs here',
  'ten':          'Milo scores {word} points',

  // ── FRUTAS ─────────────────────────────────────────────────────────────────
  'apple':        'Milo eats a red {word}',
  'banana':       'Milo eats a yellow {word}',
  'grape':        'Milo eats sweet {word}s',
  'strawberry':   'Milo eats a red {word}',
  'watermelon':   'Milo eats a big {word}',
  'mango':        'Milo loves {word} juice',
  'pear':         'Milo bites into a {word}',
  'peach':        'Milo picks a {word} from a tree',
  'coconut':      'Milo opens a {word}',
  'pineapple':    'Milo eats a yellow {word}',
  'orange':       'Milo drinks {word} juice',
  'lemon':        'The {word} is sour and yellow',
  'cherry':       'The {word} is small and red',
  'kiwi':         'The {word} is green inside',

  // ── COMIDA ─────────────────────────────────────────────────────────────────
  'bread':        'Milo eats {word} for breakfast',
  'milk':         'Milo drinks {word} every morning',
  'egg':          'Milo cooks an {word}',
  'rice':         'Milo eats {word} for lunch',
  'chicken':      'Milo grills some {word}',
  'pizza':        'Milo loves to eat {word}',
  'cake':         'Milo bakes a {word}',
  'sandwich':     'Milo makes a {word} for lunch',
  'soup':         'Milo cooks hot {word}',
  'juice':        'Milo drinks orange {word}',
  'water':        'Milo drinks clean {word}',
  'cookie':       'Milo bakes a sweet {word}',
  'candy':        'Milo eats a sweet {word}',
  'salad':        'Milo eats healthy {word}',
  'chocolate':    'Milo loves {word}',
  'cheese':       'Milo puts {word} on his bread',
  'butter':       'Milo spreads {word} on his toast',
  'corn':         'Milo eats yellow {word}',
  'carrot':       'The rabbit eats the {word}',
  'tomato':       'The {word} is red and juicy',

  // ── PARTES DEL CUERPO ──────────────────────────────────────────────────────
  'head':         'Milo nods his {word}',
  'hand':         'Milo waves his {word}',
  'hands':        'Milo claps his {word}',
  'foot':         'Milo hurts his {word}',
  'feet':         'Milo runs on his {word}',
  'eye':          'Milo closes his {word}',
  'eyes':         'Milo closes his {word}',
  'nose':         'Milo sneezes with his {word}',
  'mouth':        'Milo opens his {word} wide',
  'ear':          'Milo listens with his {word}',
  'ears':         'Milo listens with his {word}',
  'arm':          'Milo stretches his {word}',
  'arms':         'Milo stretches his {word}',
  'leg':          'Milo kicks with his {word}',
  'legs':         'Milo runs with his {word}',
  'hair':         'Milo combs his {word}',
  'teeth':        'Milo brushes his {word}',
  'finger':       'Milo points his {word}',
  'fingers':      'Milo counts on his {word}',
  'stomach':      'Milo rubs his {word}',
  'back':         'Milo stretches his {word}',
  'shoulder':     'Milo shrugs his {word}',
  'knee':         'Milo bumps his {word}',
  'elbow':        'Milo hurts his {word}',
  'tongue':       'Milo sticks out his {word}',
  'chin':         'Milo points to his {word}',
  'cheek':        'Milo shows his {word}',

  // ── FAMILIA ────────────────────────────────────────────────────────────────
  'mother':       'Milo hugs his {word}',
  'father':       'Milo plays with his {word}',
  'sister':       'Milo laughs with his {word}',
  'brother':      'Milo runs with his {word}',
  'grandmother':  'Milo visits his {word}',
  'grandfather':  'Milo listens to his {word}',
  'grandma':      'Milo visits his {word}',
  'grandpa':      'Milo listens to his {word}',
  'baby':         'The {word} is sleeping',
  'family':       'Milo loves his {word}',
  'friend':       'Milo plays with his {word}',
  'friends':      'Milo plays with his {word}',
  'uncle':        'Milo visits his {word}',
  'aunt':         'Milo visits his {word}',
  'cousin':       'Milo plays with his {word}',

  // ── ESCUELA ────────────────────────────────────────────────────────────────
  'book':         'Milo reads his {word}',
  'books':        'Milo reads his {word}',
  'pen':          'Milo writes with a {word}',
  'pencil':       'Milo draws with a {word}',
  'ruler':        'Milo measures with a {word}',
  'eraser':       'Milo uses the {word}',
  'notebook':     'Milo writes in his {word}',
  'bag':          'Milo carries his school {word}',
  'chair':        'Milo sits on the {word}',
  'table':        'Milo studies at the {word}',
  'desk':         'Milo sits at the {word}',
  'classroom':    'Milo is in the {word}',
  'teacher':      'The {word} is explaining',
  'school':       'Milo goes to {word} every day',
  'test':         'Milo studies for the {word}',
  'homework':     'Milo does his {word}',
  'scissors':     'Milo cuts with the {word}',
  'glue':         'Milo uses {word} for his project',
  'crayon':       'Milo draws with a {word}',
  'marker':       'Milo writes with a {word}',
  'globe':        'Milo points to the {word}',
  'map':          'Milo looks at the {word}',

  // ── CLIMA ─────────────────────────────────────────────────────────────────
  'sun':          'The {word} is shining bright',
  'sunny':        'It is {word} outside today',
  'rain':         'The {word} is falling hard',
  'rainy':        'It is a {word} day today',
  'snow':         'The {word} is white and cold',
  'snowy':        'It is {word} outside today',
  'wind':         'The {word} is blowing hard',
  'windy':        'It is very {word} outside',
  'cloud':        'The {word} is in the sky',
  'clouds':       'The {word} are in the sky',
  'cloudy':       'It is a {word} day outside',
  'rainbow':      'Milo sees a beautiful {word}',
  'storm':        'There is a big {word} tonight',
  'thunder':      'The {word} wakes Milo up',
  'foggy':        'It is {word} outside today',
  'hail':         'The {word} is falling from the sky',

  // ── ROPA ──────────────────────────────────────────────────────────────────
  'shirt':        'Milo wears a blue {word}',
  'pants':        'Milo puts on his {word}',
  'shoes':        'Milo ties his {word}',
  'hat':          'Milo puts on his {word}',
  'dress':        'She wears a pink {word}',
  'jacket':       'Milo wears his {word} in winter',
  'socks':        'Milo puts on his warm {word}',
  'gloves':       'Milo wears {word} in the snow',
  'scarf':        'Milo wears a {word} in winter',
  'coat':         'Milo wears his {word} outside',
  'sweater':      'Milo wears his {word} in winter',
  'boots':        'Milo wears {word} in the rain',
  'shorts':       'Milo wears {word} in summer',
  'skirt':        'She wears a red {word}',
  'cap':          'Milo puts on his {word}',
  'tie':          'Milo wears a {word} to school',
  'uniform':      'Milo wears his school {word}',

  // ── ADJETIVOS ─────────────────────────────────────────────────────────────
  'big':          'The elephant is very {word}',
  'small':        'The mouse is very {word}',
  'little':       'The baby is very {word}',
  'tall':         'Milo wants to be {word}',
  'short':        'The dog has {word} legs',
  'fast':         'The cheetah is very {word}',
  'slow':         'The turtle is very {word}',
  'hot':          'The soup is very {word}',
  'cold':         'The ice cream is very {word}',
  'new':          'Milo has a {word} book',
  'old':          'The grandfather is {word}',
  'dirty':        "Milo's shirt is {word}",
  'clean':        'Milo keeps his room {word}',
  'loud':         'The music is very {word}',
  'quiet':        'The library is very {word}',
  'beautiful':    'The flower is {word}',
  'funny':        'The joke is very {word}',
  'brave':        'Milo is very {word}',
  'strong':       'The lion is very {word}',
  'weak':         'Milo feels {word} today',
  'heavy':        'The elephant is very {word}',
  'light':        'The butterfly is very {word}',
  'soft':         'The pillow is very {word}',
  'wet':          'Milo is {word} after swimming',
  'dry':          'Milo is {word} after the sun',
  'young':        'The baby is very {word}',
  'full':         'Milo is {word} after lunch',
  'empty':        "Milo's bag is {word}",
  'kind':         'Milo is very {word}',
  'smart':        'Milo is very {word}',
  'silly':        'Milo looks {word} today',

  // ── NATURALEZA ────────────────────────────────────────────────────────────
  'tree':         'Milo climbs the {word}',
  'trees':        'Milo climbs the {word}',
  'flower':       'Milo smells a {word}',
  'flowers':      'Milo smells the {word}',
  'grass':        'Milo sits on the {word}',
  'leaf':         'The {word} falls from the tree',
  'leaves':       'The {word} fall from the tree',
  'mountain':     'Milo climbs the {word}',
  'river':        'Milo swims in the {word}',
  'sea':          'Milo swims in the {word}',
  'ocean':        'Milo swims in the {word}',
  'lake':         'Milo swims in the {word}',
  'sky':          'The {word} is very blue today',
  'moon':         'Milo looks at the {word}',
  'star':         'Milo counts the {word}s',
  'stars':        'Milo counts the {word}',
  'forest':       'Milo runs in the {word}',
  'beach':        'Milo swims at the {word}',
  'sand':         'Milo plays in the {word}',
  'rock':         'Milo climbs a big {word}',
  'volcano':      'The {word} is erupting',
  'desert':       'It is hot in the {word}',
  'jungle':       'The tiger runs in the {word}',

  // ── TRANSPORTE ────────────────────────────────────────────────────────────
  'car':          'Milo rides in a {word}',
  'bus':          'Milo takes the {word} to school',
  'bike':         'Milo rides his {word}',
  'bicycle':      'Milo rides his {word}',
  'train':        'Milo rides the {word}',
  'airplane':     'Milo sees the {word} flying',
  'plane':        'Milo sees the {word} in the sky',
  'boat':         'Milo sails on the {word}',
  'ship':         'Milo sails on the big {word}',
  'truck':        'Milo sees a big {word}',
  'helicopter':   'Milo sees the {word} flying',
  'motorcycle':   'Milo sees a {word} on the road',
  'taxi':         'Milo takes a {word}',
  'ambulance':    'The {word} goes very fast',
  'fire truck':   'The {word} has a loud siren',

  // ── HOGAR ─────────────────────────────────────────────────────────────────
  'house':        'Milo goes back to his {word}',
  'home':         'Milo is at {word} today',
  'door':         'Milo opens the {word}',
  'window':       'Milo looks through the {word}',
  'bed':          'Milo jumps on his {word}',
  'sofa':         'Milo sits on the {word}',
  'kitchen':      'Milo cooks in the {word}',
  'bathroom':     'Milo washes in the {word}',
  'room':         'Milo cleans his {word}',
  'garden':       'Milo plays in the {word}',
  'stairs':       'Milo runs up the {word}',
  'lamp':         'Milo turns on the {word}',
  'clock':        'Milo looks at the {word}',
  'mirror':       'Milo looks in the {word}',
  'fridge':       'Milo opens the {word}',
  'stove':        'Milo cooks on the {word}',
  'sink':         'Milo washes his hands in the {word}',

  // ── SALUDOS / EXPRESIONES ─────────────────────────────────────────────────
  'hello':        'Milo says {word} to his friends',
  'hi':           'Milo says {word} to everyone',
  'goodbye':      'Milo says {word} to his teacher',
  'bye':          'Milo says {word} to his friend',
  'please':       'Milo says {word} politely',
  'sorry':        'Milo says {word} to his friend',
  'good':         'Milo had a {word} day at school',
  'bad':          'Milo had a {word} day today',
  'yes':          'Milo nods and says {word}',
  'no':           'Milo shakes his head: {word}',

  // ── DEPORTES / ACTIVIDADES ────────────────────────────────────────────────
  'football':     'Milo plays {word} with his friends',
  'soccer':       'Milo plays {word} in the park',
  'basketball':   'Milo shoots the {word}',
  'tennis':       'Milo plays {word}',
  'ball':         'Milo kicks the {word}',
  'game':         'Milo wins the {word}',
  'music':        'Milo listens to {word}',
  'song':         'Milo sings a {word}',
  'art':          'Milo loves {word} class',
  'sport':        'Milo loves every {word}',

  // ── LUGARES ──────────────────────────────────────────────────────────────
  'park':         'Milo plays at the {word}',
  'playground':   'Milo runs to the {word}',
  'library':      'Milo reads at the {word}',
  'hospital':     'Milo visits the {word}',
  'store':        'Milo shops at the {word}',
  'market':       'Milo shops at the {word}',
  'restaurant':   'Milo eats at the {word}',
  'zoo':          'Milo visits the {word}',
  'pool':         'Milo swims in the {word}',
  'farm':         'Milo visits the {word}',
  'stadium':      'Milo watches a game at the {word}',
  'museum':       'Milo learns at the {word}',
  'airport':      'Milo arrives at the {word}',
  'bakery':       'Milo buys bread at the {word}',

  // ── TIEMPO (DÍAS / MOMENTOS) ──────────────────────────────────────────────
  'morning':      'Milo wakes up in the {word}',
  'night':        'Milo sleeps at {word}',
  'afternoon':    'Milo plays in the {word}',
  'today':        'Milo is happy {word}',
  'monday':       '{word} is the first school day',
  'friday':       "{word} is Milo's favorite day",
  'weekend':      'Milo rests on the {word}',
  'birthday':     'Milo celebrates his {word}',
  'holiday':      'Milo enjoys the {word}',
  'summer':       'Milo swims in {word}',
  'winter':       'Milo plays in the snow in {word}',
  'spring':       'Flowers bloom in {word}',
  'autumn':       'Leaves fall in {word}',
  'fall':         'Leaves fall in {word}',

};

// ══════════════════════════════════════════════════════════════════════════════
// FUNCIÓN PRINCIPAL
// ══════════════════════════════════════════════════════════════════════════════
function initComparacion(opts) {
  const {
    VOCABULARY,
    DIFFICULTY,
    GAME_ID,
    POINTS_REWARD,
    PENALTY_AMOUNT,
    SAVE_URL,
    CSRF,
    TIME_LIMIT,
    autoStartPlay,
  } = opts;

  // Tarjetas y preguntas según dificultad
  const CARDS_COUNT   = { 1: 2, 2: 3, 3: 4 }[DIFFICULTY] || 2;
  const MAX_QUESTIONS = DIFFICULTY === 1 ? 8 : 10;

  // Si la categoría tiene menos ítems que CARDS_COUNT, bajamos las tarjetas
  const effectiveCards = Math.min(CARDS_COUNT, VOCABULARY.length);

  let questions    = [];
  let currentQ     = 0;
  let score        = 0;
  let correctCount = 0;
  let ptsPerQ      = 1;
  let timeElapsed  = 0;
  let timerInterval = null;
  let busy         = false;

  // ── Mensajes del banner ──────────────────────────────────────────────────
  const BANNER_MSGS = [
    '¡Lee la frase y elige la imagen correcta! 🐺',
    '¡Fíjate bien en la palabra en rojo! 👀',
    '¿Qué imagen muestra lo que dice la frase? 🤔',
    '¡Tú puedes! Analiza la frase con cuidado. 💪',
    '¡Excelente trabajo, sigue así! ⭐',
    '¡Ya casi! No te rindas. 🎉',
  ];

  // ── Helpers ──────────────────────────────────────────────────────────────
  function showError(msg) {
    const sec = document.getElementById('gameSection');
    sec.innerHTML = `<div class="alert alert-warning text-center m-4 rounded-4">${msg}</div>`;
    sec.style.display = 'block';
  }

  function shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  // ── Construir preguntas ──────────────────────────────────────────────────
  // Cada tarjeta muestra la IMAGEN del ítem de vocabulario correspondiente.
  // La tarjeta correcta = el ítem cuya palabra aparece en la frase.
  // Las tarjetas distractor = otros ítems de la misma categoría.
  function buildQuestions() {
    if (effectiveCards < 2) return [];

    const result  = [];
    const shuffled = shuffle(VOCABULARY);

    for (const item of shuffled) {
      if (result.length >= MAX_QUESTIONS) break;

      const key      = item.word_en.toLowerCase().trim();
      const template = SENTENCES_DB[key];
      if (!template) continue;

      // Frase con la palabra resaltada en rojo
      const highlighted = `<span class="comp-word-highlight">${item.word_en}</span>`;
      const sentence    = template.replace('{word}', highlighted);

      // Distractores: otros ítems del mismo vocabulario
      const pool       = VOCABULARY.filter(v => v.id !== item.id);
      if (pool.length < effectiveCards - 1) continue; // no hay suficientes distractores

      const distractors = shuffle(pool).slice(0, effectiveCards - 1);

      // Mezclar tarjeta correcta con distractores
      const cards = shuffle([
        { vocabItem: item,       isCorrect: true  },
        ...distractors.map(v => ({ vocabItem: v,  isCorrect: false })),
      ]);

      result.push({ item, sentence, cards });
    }
    return result;
  }

  // ── Construir elemento de tarjeta ────────────────────────────────────────
  function buildCardEl(card) {
    const el = document.createElement('div');
    el.className = 'comp-card';
    el.dataset.correct = card.isCorrect ? '1' : '0';

    const v      = card.vocabItem;
    const imgSrc = v.image || null;

    // Placeholder visual cuando no hay imagen
    const placeholderHtml = `
      <div class="comp-card-placeholder" style="display:${imgSrc ? 'none' : 'flex'}">
        <span class="comp-placeholder-emoji">📷</span>
        <span class="comp-placeholder-label">${v.word_es}</span>
      </div>`;

    const imgHtml = imgSrc
      ? `<img
           src="${imgSrc}"
           alt="${v.word_es}"
           class="comp-card-img"
           draggable="false"
           onerror="this.style.display='none';this.nextElementSibling.style.display='flex';"
         >`
      : '';

    el.innerHTML = `
      <div class="comp-card-img-wrap">
        ${imgHtml}
        ${placeholderHtml}
      </div>
      <div class="comp-card-label">${v.word_es}</div>
    `;

    el.addEventListener('click', () => handleClick(el));
    return el;
  }

  // ── Mostrar pregunta ─────────────────────────────────────────────────────
  function showQuestion() {
    if (currentQ >= questions.length) { endGame(); return; }
    busy = false;

    const q         = questions[currentQ];
    const container = document.getElementById('cardsContainer');

    document.getElementById('qNum').textContent         = currentQ + 1;
    document.getElementById('sentenceDisplay').innerHTML = q.sentence;
    document.getElementById('progressFill').style.width  =
      `${Math.round((currentQ / questions.length) * 100)}%`;
    document.getElementById('compBannerText').textContent =
      BANNER_MSGS[currentQ % BANNER_MSGS.length];

    container.innerHTML = '';
    container.className = `comp-cards-wrap comp-cards-${effectiveCards}`;

    q.cards.forEach((card, i) => {
      const el = buildCardEl(card);
      el.style.cssText = 'opacity:0;transform:scale(.8) translateY(20px);transition:none';
      container.appendChild(el);
      requestAnimationFrame(() => {
        setTimeout(() => {
          el.style.cssText = 'transition:opacity .3s ease, transform .3s ease';
          el.style.opacity = '1';
          el.style.transform = 'scale(1) translateY(0)';
        }, i * 90);
      });
    });
  }

  // ── Manejar clic ────────────────────────────────────────────────────────
  function handleClick(cardEl) {
    if (busy || cardEl.classList.contains('comp-card--disabled')) return;

    const isCorrect = cardEl.dataset.correct === '1';

    if (isCorrect) {
      busy = true;
      cardEl.classList.add('comp-card--correct');
      score += ptsPerQ;
      correctCount++;
      document.getElementById('scoreDisplay').textContent = score;
      showScoreToast(ptsPerQ, true);
      setTimeout(() => { currentQ++; showQuestion(); }, 950);

    } else {
      cardEl.classList.add('comp-card--wrong', 'comp-card--disabled');
      score = Math.max(0, score - PENALTY_AMOUNT);
      document.getElementById('scoreDisplay').textContent = score;
      showScoreToast(PENALTY_AMOUNT, false);

      // Si solo queda la correcta, resaltarla y avanzar
      const remaining = document.querySelectorAll(
        '.comp-card:not(.comp-card--disabled):not(.comp-card--correct)'
      );
      if (remaining.length === 1 && remaining[0].dataset.correct === '1') {
        busy = true;
        setTimeout(() => {
          remaining[0].classList.add('comp-card--auto');
          setTimeout(() => { currentQ++; showQuestion(); }, 1100);
        }, 500);
      }
    }
  }

  // ── Timer ────────────────────────────────────────────────────────────────
  function startTimer() {
    if (TIME_LIMIT <= 0) return;
    timerInterval = setInterval(() => {
      timeElapsed++;
      const remaining = Math.max(0, TIME_LIMIT - timeElapsed);
      const mm = String(Math.floor(remaining / 60)).padStart(2, '0');
      const ss = String(remaining % 60).padStart(2, '0');
      const el = document.getElementById('timerDisplay');
      if (el) el.textContent = `${mm}:${ss}`;
      if (remaining <= 0) { clearInterval(timerInterval); endGame(); }
    }, 1000);
  }

  // ── Fin de juego ─────────────────────────────────────────────────────────
  async function endGame() {
    clearInterval(timerInterval);
    busy = true;

    const fillEl = document.getElementById('progressFill');
    if (fillEl) fillEl.style.width = '100%';

    const maxScore = questions.length * ptsPerQ;
    const pct      = Math.round((score / Math.max(maxScore, 1)) * 100);
    const stars    = pct >= 80 ? '⭐⭐⭐' : pct >= 50 ? '⭐⭐' : '⭐';

    document.getElementById('winScore').textContent   = score;
    document.getElementById('winCorrect').textContent = correctCount;
    document.getElementById('winTotal').textContent   = questions.length;
    document.getElementById('winStars').textContent   = stars;
    document.getElementById('winOverlay').style.display = 'flex';

    try {
      const res = await fetch(SAVE_URL, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF },
        body:    JSON.stringify({
          game_id:    GAME_ID,
          score,
          max_score:  maxScore,
          time_spent: timeElapsed,
          completed:  true,
        }),
      });
      const data = await res.json();
      if (data.registro_pk) {
        document.getElementById('btnVolverPanel').href =
          '/talleres/mis-talleres/?revisado=' + data.registro_pk;
      }
    } catch (_) {}
  }

  // ══════════════════════════════════════════════════════════════════════════
  // ARRANQUE
  // ══════════════════════════════════════════════════════════════════════════
  if (VOCABULARY.length < 2) {
    showError('⚠️ Necesitas al menos 2 palabras en la categoría para jugar.');
    return;
  }

  questions = buildQuestions();

  if (questions.length === 0) {
    showError(
      '⚠️ Las palabras de esta categoría aún no tienen frases asignadas en ' +
      'Comparación. El profesor puede añadir más vocabulario con palabras en inglés ' +
      'comunes para desbloquear el juego.'
    );
    return;
  }

  ptsPerQ = Math.max(1, Math.round(POINTS_REWARD / questions.length));
  document.getElementById('qTotal').textContent = questions.length;

  showQuestion();

  if (autoStartPlay) {
    document.getElementById('gameSection').style.display = 'block';
    startTimer();
  } else {
    const btn = document.getElementById('startGameBtn');
    if (btn) {
      btn.addEventListener('click', startTimer, { once: true });
    } else {
      document.getElementById('gameSection').style.display = 'block';
      startTimer();
    }
  }
}
