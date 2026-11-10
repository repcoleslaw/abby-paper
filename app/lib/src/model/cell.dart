/// A dot on the walk. Row 0 is the far edge of the page, column 0 is A.
class Cell {
  const Cell(this.row, this.col);

  final int row;
  final int col;

  static const columns = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

  String get name => '${columns[col]}${row + 1}';

  bool sharesSide(Cell other) =>
      (row - other.row).abs() + (col - other.col).abs() == 1;

  Cell shift(int dRow, int dCol) => Cell(row + dRow, col + dCol);

  static Cell parse(Object? token, {required int rows, required int cols}) {
    if (token is! String) {
      throw LevelParseException('Bad cell $token.');
    }
    final text = token.trim().toUpperCase();
    final rowNumber = text.length < 2 ? null : int.tryParse(text.substring(1));
    final col = text.isEmpty ? -1 : columns.indexOf(text[0]);
    if (col < 0 || rowNumber == null) {
      throw LevelParseException('$token is off the $cols by $rows board.');
    }
    final row = rowNumber - 1;
    if (row < 0 || col >= cols || row >= rows) {
      throw LevelParseException('$token is off the $cols by $rows board.');
    }
    return Cell(row, col);
  }

  @override
  bool operator ==(Object other) =>
      other is Cell && other.row == row && other.col == col;

  @override
  int get hashCode => Object.hash(row, col);

  @override
  String toString() => name;
}

class LevelParseException implements Exception {
  LevelParseException(this.message);

  final String message;

  @override
  String toString() => message;
}
