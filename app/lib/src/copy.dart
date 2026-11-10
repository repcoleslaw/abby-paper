const rules = <String>[
  'Paw is Abby. Flag is the last dot. Trees have no dot. A heavy edge is a cliff: go around.',
  'Waves need the vest. An arch needs the lamp. Pick it up, then step in.',
  'One circle each new dot. A treat inks three more. None left: erase and redraw.',
  'The flag may take the last circle. Score is sticks + 3×balls + treats − steps. Higher is better.',
];

String formatScore(int score) => score < 0 ? '−${-score}' : '$score';
