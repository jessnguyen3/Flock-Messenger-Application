Authentication: 
-    first/last name must be alphabetical no numbers or symbols
-    register leaves the user logged in
-    userid and channel id are 0 indexed

Channels:

- other than channel_id and name, each channel in the channels list also 
contains is_public, lists containing members, and a list of sent messages

- members will be split into lists owner_members and all_members, and
all_members does not include owner_members, only non-owners

channel.py:
- in function channel_join, raises InputError if user is already a member of
  the channel

- flockr owner is a normal owner upon joining channel, but has owner perms.
whether or not flockr owner is also a channel owner does not matter

Message:

- channel_id of channel that a message was sent in is stored with each message

other.py:
- in the search function, lower cases and upper cases (in the given query
string) are treated as the same. That is, if you were to search for "iNfO",
this will be treated as searching for any message that contains the word info,
regardless of the upper/lower cases