# `E0 00` Control Sequences

Using some information from
[here](https://zeldamods.org/wiki/Msbt#Text_Commands), I've discovered how these
control sequences seem to work. Now all I have to do is to figure out what each
code means.

**Important note:** keep in mind that the files are in Little Endian. When
encoded to UTF-16, and sequences unicode code-point will go from bytes `AB CD`
to `\uCDAB`.


---

## Table of Contents

- [`E0 00` Control Sequences](#e0-00-control-sequences)
  - [Table of Contents](#table-of-contents)
  - [Command Types](#command-types)
    - [`00 00` Command Type](#00-00-command-type)
      - [`00 00` Command Variant](#00-00-command-variant)
      - [`02 00` Command Variant](#02-00-command-variant)
      - [`03 00` Command Variant](#03-00-command-variant)
      - [`04 00` Command Variant](#04-00-command-variant)
    - [`28 00` Command Type](#28-00-command-type)
    - [`0A 00` Command Type](#0a-00-command-type)
      - [`00 00` Command Variant](#00-00-command-variant-1)
      - [`01 00` Command Variant](#01-00-command-variant)
      - [`02 00` Command Variant](#02-00-command-variant-1)
      - [`0A 00` Command Variant](#0a-00-command-variant)
    - [`6E 00` Command Type](#6e-00-command-type)
    - [`32 00` Command Type](#32-00-command-type)
    - [`3C 00` Command Type](#3c-00-command-type)
      - [Rough/Scratch notes](#roughscratch-notes)
  - [Anomalies](#anomalies)

---


## Command Types

Each command has two bytes (unsigned short) immediately after its `E0 00` byte.
This is its *command type*. Each different type of command is followed by a set
of *command options*. These options are **unsigned** shorts, and each *type* has
a different number of *options*.

The following is a list of the known command types. The *UTF-16-LE* column is
what the two command type bytes will be decoded as if you decode the entire
string as UTF-16. You can click the entry in the command type column to be taken
to a longer explanation, where applicable.

| Command Type                   | UTF-16-LE | Number of options        | Meaning                 |
| :----------------------------- | :-------- | :----------------------- | :---------------------- |
| [`00 00`](#00-00-command-type) | Null      | Variable                 | Modify Text             |
| [`28 00`](#28-00-command-type) | `(`       | 8 bytes, 4 shorts        | *Unknown*               |
| [`0A 00`](#0A-00-command-type) | `\n`      | Variable                 | Pausing (?)             |
| [`6E 00`](#6E-00-command-type) | `n`       | 4 bytes, 2 shorts        | Pausing/Delay (?)       |
| [`32 00`](#32-00-command-type) | `2`       | 8 bytes, 4 shorts        | *Unknown*               |
| [`3C 00`](#3C-00-command-type) | `<`       | Variable, until `00 00`  | *Unknown*, menu option? |

**Reminder:** the *Command Type* column is Little Endian.

All of these command types have extra bytes attached to them. These are *command
options*. Each command has its known/supposed command options listed below in
their own sections.


### `00 00` Command Type

This command seems to modify text. There are several *variants* of this command.
For example, bytes `0E 00` `00 00` may be followed by several other sets of
bytes. These different variants have different amounts of options:

| Command Variant                   | Number of options | Meaning                 |
| :-------------------------------- | :---------------- | :---------------------- |
| [`00 00`](#00-00-command-variant) | 6 bytes, 3 shorts | *Unknown*               |
| [`02 00`](#02-00-command-variant) | 4 bytes, 2 shorts | *Unknown*               |
| [`03 00`](#03-00-command-variant) | 4 bytes, 2 shorts | Modify colour (?)       |
| [`04 00`](#04-00-command-variant) | 2 bytes, 1 short  | *Unknown*               |

**For example:** The string of bytes, "`0E 00 00 00 03 00 02 00 FF FF`" means:

- `0E 00`: the command escape sequence;
- `00 00`: this command is type `00 00`, modify text;
- `03 00`: this modify text command is variant `03 00`, modify colour(?).
- `02 00 FF FF`: this modify text colour command has `02 00 FF FF` as its
  options.

When following the *number of options* column, be careful that this is the
number of shorts **after** the variant bytes (the **four bytes, two shorts**
after the `03 00` in the given example). So, the full length of the escape
sequences is two higher; one to include `0E 00` and one to include the *command
type*.

Certain extra variants of the `00 00` command type only seem to appear in the
Japanese language MSBT files.


#### `00 00` Command Variant

Currently Unknown.


#### `02 00` Command Variant

Currently Unknown.


#### `03 00` Command Variant

Currently Unknown. Although, I suspect that this variant of the Modify Text
command is used to **change the colour of text**.


#### `04 00` Command Variant

Currently Unknown.


### `28 00` Command Type

Currently unknown.


### `0A 00` Command Type

This command seems to be used for pausing. However, there are variants of it.
Only one seems to have a clear usage.

| Command Variant                     | Number of options | Meaning              |
| :---------------------------------- | :---------------- | :------------------- |
| [`00 00`](#00-00-command-variant-1) | 4 bytes, 2 shorts | Pause for `n` frames |
| [`01 00`](#01-00-command-variant)   | 2 bytes, 1 short  | *Unknown*            |
| [`02 00`](#02-00-command-variant-1) | 2 bytes, 1 short  | *Unknown*            |
| [`0A 00`](#0a-00-command-variant)   | 2 bytes, 1 short  | *Unknown*            |

**Important note**: With regards to variants `01 00`, `02 00` and `0A 00`: it's
possible that the `0A 00` command has behaviour for `00 00` variants and
behaviour for everything else. Writing
[`parse-dialogue.py`](./parse-dialogue.py) in this manner parses all files
without error, so I will work under this assumption for now.


#### `00 00` Command Variant

This variant is always followed by a `02 00` byte sequence. The next byte after
that sequence is a short representing frames to wait for. For example:

```
Offset(h) 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F

0000ECF0  02 00 00 00 20 00 49 00 20 00 73 00 61 00 79 00  .... .I. .s.a.y.
0000ED00  20 00 61 00 67 00 61 00 69 00 6E 00 0E 00 6E 00   .a.g.a.i.n...n.
0000ED10  00 00 00 00 0E 00 0A 00 00 00 02 00 0D 00 0E 00  ................
0000ED20  28 00 0F 00 04 00 00 CD 00 00 42 00 41 00 52 00  (......Í..B.A.R.
0000ED30  42 00 45 00 44 00 2E 00 0A 00 0E 00 0A 00 00 00  B.E.D...........
0000ED40  02 00 0D 00 42 00 45 00 4C 00 4C 00 59 00 2E 00  ....B.E.L.L.Y...
0000ED50  0E 00 0A 00 00 00 02 00 0D 00 20 00 48 00 41 00  .......... .H.A.
0000ED60  49 00 52 00 21 00 0E 00 00 00 03 00 02 00 01 00  I.R.!...........
```

At offset `0xED14`, a `0A 00` `00 00` command is started. Following that, there
are bytes `02 00` `0D 00`. It is unclear what the `02 00` is for (perhaps
selecting "frames" as the timer option?). The `1D 00` bytes are a frame-timer:
`0x1D` = 29. So, the game will pause for 29 frames: 0.9667 seconds. More timers
can be seen at the end of each "BARBED" and "BELLY" (both `0D 00`, 13 frames).


#### `01 00` Command Variant

Currently unknown. This command always seems to be of the form `0E 00` `0A 00`
`01 00` `00 00`.


#### `02 00` Command Variant

Currently unknown. This command always seems to be of the form `0E 00` `0A 00`
`02 00` `00 00`.


#### `0A 00` Command Variant

Currently unknown. This command always seems to be of the form `0E 00` `0A 00`
`0A 00` `00 00`.


### `6E 00` Command Type

Currently unknown.


### `32 00` Command Type

Currently unknown.


### `3C 00` Command Type

Currently unknown. I suspect that, since this didn't turn up until the
`Get_Fish` files, it has something to do with triggering dialogue options
(perhaps, "Would you like to release this fish?").


#### Rough/Scratch notes

From `CNzh/SYS_Get_Fish.msbt` (Chinese catch puns):

- *Variant* `08 00` had 9 shorts after it, 18 bytes: 
  - `0E 00` `3C 00` `08 00` followed by:
  - `0E 00` `05 00` `06 00` `06 00` `06 00` `06 00` `06 00` `05 00` `00 00`.
- *Variant* `01 00` had 5 shorts after it, 10 bytes:
  - `0E 00` `3C 00` `01 00` followed by:
  - `06 00` `08 00` `09 00` `0A 00` `00 00`.

It seems that this command may run until `00 00` bytes.

- *Variant* `0A 00` had 8 shorts after it, 16 bytes:
  - `0E 00` `3C 00` `0A 00` followed by:
  - `0C 00` `06 00` `06 00` `06 00` `06 00` `07 00` `07 00` `00 00`.

Yup. This is definitely a `00 00` terminated command.


## Anomalies

In one single file, `EUru/SYS_Get_Fish.msbt`, there's a single `0E 00` which is
not part of an escape sequence/command. It appears at offset `0x33A0`, and is
between

- `3F 04` `3E 04` `39 04` `3C 04` `30 04` `3B 04`: поймал; and
- `3F 04` `3E 04` `39 04` `3C 04` `30 04` `3B 04` `30 04`: поймала.

These are the masculine and feminine versions of thee same word; "caught." It is
unclear why this is the only case where this disctinction uses the `0E 00` byte
sequence. Perhaps this is because it occurs in the, "Woo-hoo! I've caught all
the fish! You'd think I'd have a pun for this..." message, and this is the first
place that the Russian translation has the player character refer to themselves?