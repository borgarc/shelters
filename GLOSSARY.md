# Shelters

Management of feral cat colonies and the people who look after them.

## Colonies and cats

**Colony**:
A group of free-roaming cats living at a known location.
_Avoid_: Shelter, group, site

**Cat**:
An individual animal registered in the system, optionally belonging to a Colony.

## People

**User**:
Anyone who can sign in. Being a User grants no role by itself.
_Avoid_: Account, member

**Caretaker** (Cuidador):
A person who physically looks after one or more Colonies (feeding, monitoring, TNR). A User may or may not be a Caretaker.
_Avoid_: Volunteer, feeder, keeper

**Administrator**:
A User who manages the organisation's data and invites Caretakers, whether or not they are a Caretaker themselves.
_Avoid_: Coordinator, staff

**Assignment**:
The period during which a Caretaker looks after a given Colony, from when they join until they leave it.
_Avoid_: Membership, link

**Lead Caretaker** (Cuidador responsable):
The Caretaker whose current Assignment marks them as the identified contact person for a Colony. A Colony has at most one at a time, and may temporarily have none.
_Avoid_: Owner, main caretaker

**Anonymised Caretaker**:
A former Caretaker whose personal data has been removed, kept only so that a Colony's past Assignments remain countable.
_Avoid_: Deleted caretaker

**Invitation**:
An Administrator's offer for a person to become a Caretaker, which they accept by setting their password.
