# `00 0e` Control Sequences

Using some information from
[here](https://zeldamods.org/wiki/Msbt#Text_Commands), I've discovered how these
control sequences seem to work. Now all I have to do is to figure out what each
code means.


## Command Types

Each command has two bytes (unsigned short) immediately after its `00 0e` byte.
This is its *command type*. The following is a list of the known command types.
The *UTF-16-LE* column is what the two command type bytes will be decoded as if
you decode the entire string as UTF-16 using Little Endian (what AC:NH uses).
You can click the entry in the command type column to be taken to a longer
explanation, where applicable.

| Command Type              | UTF-16-LE | Additional Bytes    | Meaning     |
| :------------------------ | :-------- | :------------------ | :---------- |
| [`00 00`](#00-00-command) | N/A       | 6 bytes, 3 shorts   | Modify Text |
| [`00 0a`](#00-0a-command) | `\n`      | 4 bytes, 2 shorts   | *Unkown*    |
| [`00 28`](#00-28-command) | `(`       | 6 bytes, 3 shorts   | *Unkown*    |

Many of these command types have extra bytes attached to them. These are
*command options*. Each command has its known/supposed command options listed
below.


### `00 00` Command

This command seems to modify text. After most critter names, the sequence is `00
0ee`, `00 00`, `00 03`, `00 02`, `ff ff`. This seems to suggest that, per
ZeldaMods' table, the `FF FF` bytes are used to turn text back to white.


### `00 0a` Command

Currently unknown.


### `00 28` Command

Currently unknown.