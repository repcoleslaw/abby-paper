---
tags: [gift, anniversary, paper-games, path]
created: 2026-11-03
---

# 00 Paper Abby

Back to [[00 Paper Apps]].

A solo walk, portrait, about the size of a phone turned long. Abby is the paw. The flag is the last dot. She draws one line between dots that share a side. Each new dot spends a circle of energy. A treat gives three circles back. Trees and cliffs she goes around. Water waits for a life vest. A cave waits for a head lamp. Sticks and tennis balls count only when they do not make the walk longer.

There is no phone game this is copying. The loop is the walk itself: a budget, a flag, and a find that may or may not be worth leaving the line for. The other two games in this collection use loose pieces, because something on those boards has to fall or leave. Nothing here falls. The pencil is the piece. Erasing is the undo.

Print the pages in [print](print). Her copy is the file without "answer" in the name. The routes are in [[Answer Key]].

## Why this shape

| Beat | On the page |
|---|---|
| She can see the whole walk | Six columns, ten rows, the flag already drawn |
| A step budget | Twelve circles. The same twelve on every level |
| She spends a step | She draws to the next dot and fills one circle |
| A find on the way | She circles it on the map and checks the journal |
| A gate | Waves need the vest first. An arch needs the lamp first |
| The budget runs out | She erases the line and draws another. The page is not lost |
| She arrives | She scores the line. Higher is better |

Six columns is a glance, same as the well. Ten rows is a short walk, not a maze poster. Diagonals do not count. A dot is used once. The line does not cross itself, because crossing would reuse the corner she already left.

## What you are printing

One half-letter page per level, 5.5 by 8.5 inches. Print at actual size, portrait, scale 100. If the dialog offers "fit to page," turn that off. On letter paper the sheet sits with room around it. The board is about phone width. The journal is the right margin.

The pages are SVG, so the type is still type. Nudge a label if you want. To move a tree, edit the level file and run the tool again, or delete that tree's group in the SVG. The groups are named: `grid`, `terrain`, `dots`, `items`, `journal`, `legend`, and on the answer sheet `answer`. Colors live in the `<style>` block at the top. A tree is `tree-C4`. A cliff is `cliff-D8-D7`.

| File | What it is |
|---|---|
| [levels](levels) | The maps. Cell names, not coordinates |
| [print](print) | The sheets, one pair per level |
| [assets](assets) | PNG marks. A file here replaces the drawn one on the next run |
| [tools/paper_abby.py](tools/paper_abby.py) | Checks the route and redraws the sheets |
| [[Answer Key]] | The only best line on each page, and why the other ideas lose |

Every page carries the rules in four lines under the board. She should not need this note at the table.

## Pictures

The paw, the flag, the trees, the waves, the arch, the cliff, and the things she picks up are paths drawn in [tools/paper_abby.py](tools/paper_abby.py). The sheets in [print](print) are the stored pages. Open one and the drawing is already in it.

To use a picture you made, save a PNG in [assets](assets). The file name is the mark.

| File | Slot on the sheet |
|---|---|
| `paw.png`, `flag.png`, `vest.png`, `lamp.png`, `stick.png`, `ball.png`, `treat.png` | 4 mm square, centered above the dot |
| `tree.png`, `water.png`, `cave.png` | 9 mm square, centered in the 12 mm cell. The cell color remains in the margin |
| `cliff.png` | 2.3 mm by 10.6 mm, drawn upright. A horizontal cliff turns the picture |

Transparent background. Crop the canvas to the drawing. The whole canvas is scaled into that slot, so empty margin in the file makes the mark smaller. The largest slot is 9 mm, about a third of an inch, so 512 pixels on the long side is enough to print cleanly.

Water and caves keep their dot, drawn on top of the picture. Leave the middle of those two quiet if the dot should show. A tree has no dot. The legend at the bottom of the page uses the same files, fit into a 4 mm square.

Run `all` again after a picture changes. Each sheet stores its own copy, so the page still prints after it leaves this folder. A mark with no PNG stays the drawn one.

## Rules

### The line

Columns are A to F, left to right. Rows are 1 to 10, top to bottom. Row 1 is the far edge of the page.

She starts on the paw. She ends on the flag. A move is a straight step to a dot that shares a side. She may not step to a tree, across a cliff, or onto a dot already in the line.

She stops when she draws into the flag. The flag is the last dot, not a dot she passes through.

### Energy

Every level starts at 12. The page prints twelve solid circles and twelve dashed ones. The dashed ones are not hers yet.

The paw is free. She is already standing there. Each new dot costs one circle. She fills it in. Landing on a treat lets her ink three dashed circles, after paying for that dot. She cannot hold more than 24, and the page has nowhere to put a 25th, so the cap and the paper are the same rule.

If the next dot would need a circle she does not have, the line stops. She erases it and tries another. Arriving on the flag may take her last circle. That still counts.

A treat is worth three energy and one point. It is not a life. Running out is the same kindness as the clips on the well: set the line aside and draw again.

### The tiles

| Mark | Rule |
|---|---|
| Dot | She may enter. The line goes dot to dot |
| Tree | No dot. She cannot enter. Go around |
| Cliff | A heavy edge between two dots. She cannot cross that edge. Both dots can still be part of the walk if she comes at them another way |
| Waves | Water. She may enter only if the vest is already checked |
| Arch | A cave. She may enter only if the lamp is already checked |
| Vest, lamp, stick, ball, treat | Sitting on a dot. She picks it up by drawing into that dot, circles it, and checks the journal. The vest and the lamp do not score |

The vest has to be picked up before the step into the water, not on the water. Same for the lamp and the cave. A tool on the far side of its own gate is a broken map.

### The journal

One line per thing on that page, with its cell, so "Stick D3" is that stick and not a stick from another walk. She checks it when the line enters the cell. She does not check the ball she only looked at.

Steps are the number of filled circles, which is the number of new dots, which is one less than the dots in the line if you are counting the paw. The paw was free.

### The score

Sticks, plus three for each tennis ball, plus treats, minus steps.

The vest is not in that sum. The lamp is not in that sum. A stick is one point. A tennis ball is three. A treat is one. A step is one point the other way. A one-step detour for a stick ties the line she already had. A two-step detour for a stick loses. A ball pays for a detour of one or two steps.

The number will usually sit below zero. That is the length of the walk, not a failed page. Higher is better. Minus seven beats minus twelve.

She can win with a minus. She wins by touching the flag with a legal line. The score is how she compares two lines, if she wants to. The gift does not require her to find the best one. The answer key is for you, so you know the page has a best line and what it is.

## The twelve levels

Level 1 is the proof sheet: every mark, on one walk, so you can judge the page. Levels 2 through 5 add one idea at a time. Level 6 puts a ball and a second stick on short bulges that still reach the flag. Levels 7 through 12 leave most of the dots open, so a wrong line can still reach the flag. Every stick and every tennis ball sits on at least one line that touches the flag. If you want her first evening to be quiet, give her 2, then 3, then 4. Level 1 can wait until the drawings feel right, or it can be the page you scribble on while you decide.

| Lv | Name | What is new |
|----|------|-------------|
| 1 | The whole walk | Every mark at once. Two sticks and a ball, each on a walk that reaches the flag. A cliff that is holding the best line in place |
| 2 | Around the trees | A second lane, a second stick, and a ball. All three walks reach the flag |
| 3 | The cliff | One heavy edge. A second stick and a ball sit two steps off the walk around it |
| 4 | The vest | A dry walk with its own stick, and a shorter walk that crosses the water. A ball two steps off the water |
| 5 | The lamp | The long way has its own stick. A ball sits two steps off the cave |
| 6 | The ball | Vest, lamp, and two treats. The ball and a second stick are bulges that still reach the flag |
| 7 | The open field | Six trees. One stick on the best line, another on the right side, and a ball along the top |
| 8 | Two sticks | A far corner and two sticks on one walk. The ball is two steps off that walk and still finishes |
| 9 | The pond | A small pond on the short line. The ball goes around the water. A second stick never crosses it |
| 10 | The den | The cave is the short way. The ball walk and a second stick both reach the flag |
| 11 | Both gates | Open ground. Water and a cave on the best line. Another stick, and a ball, on walks that still finish |
| 12 | The wide park | Four trees and both gates. The ball walk and the stick over the top both reach the flag |

The sentences under the titles are blanks for you to replace, same as the other games. One Tuesday each. Not a motto. The blurbs on the sheets now are the rules of that page, and those can stay.

## The next thirteen

Levels 13 through 25 are a second evening. The rules do not change. The pocket does. Every one of these pages has four sticks and three tennis balls, and every one of them sits on a walk that reaches the flag. A stick is one point. A tennis ball is three, so a two-step detour for a ball wins by one.

Two roads leave Abby, and they meet again only at the flag. On the plain pages the roads carry the same number of sticks, and the longer road picks up one more ball. Two steps for that ball wins, so the longer road is best. On the water pages and the cave pages the long road is still the one that pays: the vest or the lamp is already on it, and the heavier pocket is worth the extra steps. Level 20 is the cliff. The short step from F8 to F7 would score better, and it is closed.

| Lv | Name | What the page is asking |
|----|------|-------------------------|
| 13 | The full pocket | Two sticks on each road. The extra ball is the long way |
| 14 | The low road | The bottom road is shorter. The extra ball on the long road wins by one |
| 15 | The creek | The vest, then one water dot. The dry road is lighter |
| 16 | The far bank | The same choice, from the top of the page |
| 17 | The burrow | The lamp, then the arch. The open column misses both |
| 18 | The high cave | The arch is one step after the lamp |
| 19 | The long crossing | Vest and lamp, both on the road that scores better |
| 20 | The cut | The cliff is holding a better step shut. The stick is on the long side |
| 21 | The hedge | Two sticks each. The long road's second ball pays for the two steps |
| 22 | The column | The left-hand road is the one with the extra ball |
| 23 | The high water | The vest is on the long road, up at the top |
| 24 | The lamp road | The lamp and the arch are on the right edge |
| 25 | The last pocket | Both gates again. The right-hand column skips them and loses by three |

Same quiet order if you want it: 13, then 14, then 15. Level 20 can wait until the cliff on level 3 already makes sense.

## How a route was checked

A line is legal if it starts on the paw, ends on the flag, steps only to side-by-side dots, never reuses a dot, never enters a tree, never crosses a cliff, never enters water before the vest, and never enters a cave before the lamp. Energy starts at 12, drops by one per new dot, and rises by three on a treat, and it is never asked to go below zero. The flag may be entered on the last point.

The best line is the legal one with the highest score. The tool in [tools/paper_abby.py](tools/paper_abby.py) searches all of them. Each of these pages has exactly one line at that score. A tie would have been a reason to move a tree, not a thing to print. The full trace for every level, including energy after each dot, is in [[Answer Key]]. Level 1 is repeated below so this note can be read on its own.

Run it from the vault:

```
py -3 "Paper Apps/Paper Abby/tools/paper_abby.py" all
```

`solve` checks one file. `preview` prints the map. If you change a level, run `all` again before you trust the old answer sheet.

## Level 1 answer

Kept in this note so the proof sheet can be checked without flipping files. The same trace is the first entry in [[Answer Key]].

The only best score is 1 stick + 1×3 ball + 2 treats − 17 steps = **−11**. Nothing else ties it.

The line, and the energy after each new dot:

A10 (12) → B10 (11) → C10 treat (13) → D10 ball (12) → D9 (11) → C9 (10) → C8 vest (9) → D8 water (8) → E8 water (7) → E7 treat (9) → D7 (8) → D6 lamp (7) → D5 cave (6) → D4 (5) → D3 stick (4) → E3 (3) → F3 (2) → F2 flag (1).

She finishes with 1 energy. The ball at D10 is the bulge C10, D10, D9, C9. That line is two steps longer than the walk that skips it, and the ball is worth three, so it wins by one. The walk that skips the ball scores −12. The stick at C4 is the bulge D4, C4, C3, D3. Two steps for one stick loses, and that line scores −13. It still reaches the flag.

The cliff between D8 and D7 is the reason the line goes through E8 and the second treat. That step is not allowed. With the cliff in place, −11 is the best legal score, and only one line has it.

## Order of work

1. Print level 1 at actual size. Draw the line with a pencil. Fill the circles. If a rule makes you hesitate, the legend is wrong, or the rule is. Fix the legend before you print the set.
2. If the trees are too loud or the journal is tight, change the style block or the layout constants in the tool, or replace a mark with a PNG as described under Pictures, and run `all` again.
3. Play 2, 3, and 4 yourself, relaxed. If the vest does not feel worth picking up, the dry walk is not long enough. Lengthen that walk. Do not add a rule.
4. Write the twelve sentences. They can live on the back of the sheet, one each.
5. Print her set without the answer files.

If a rule only makes sense with you explaining it, it is too fiddly. The four lines under the board are the game. The vest, the lamp, and the ball are the color. It is better to hand her three kind walks than a page that needs a referee.
