# `E0 00` Control Sequences

Using some information from
[here](https://zeldamods.org/wiki/Msbt#Text_Commands), I've discovered how these
control sequences seem to work. Now all I have to do is to figure out what each
code means.

**Important note:** keep in mind that the files are in Little Endian. When
encoded to UTF-16, and sequences unicode code-point will go from bytes `AB CD`
to `\uCDAB`.


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
| [`0A 00`](#0A-00-command-type) | `\n`      | 4 bytes, 2 shorts        | *Unknown*               |
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

Currently unknown.


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

In one single file, `EUru/SYS_Get_Fish,msbt`, there's a single `0E 00` which is
not part of an escape sequence/command.