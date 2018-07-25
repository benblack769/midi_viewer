from collections import defaultdict
import copy

'''
midi files describe music as several independent channels of sound.

the file format describes notes within a channel as an interval:

(note start, pitch)
(note end, pitch)

This gives rise to a natural chord at every time step.

Unfortunately, the volume of the note decreases after its start,
so many files choose not to end the note until long after it is initiated,
leading to absurdly huge and unweldy chords.

So notes need to be terminated in some way other than a "note end"
event. The code describes 3 ways of doing this:

1.  `stack_ticks_into_chords`:
        only terminate when note ends
2.  `stack_ticks_into_chords_turn_off_when_channel_activates`:
        When a new note within the same channel activates,
        terminate all notes in the channel activated in a previous tick.
3.  'stack_ticks_into_chords_turn_off_on_timeout':
        Notes time out after a certain number of ticks
'''

def merge_dicts(base_dict,replace_dict):
    merge_dict = copy.copy(base_dict)
    for key in replace_dict:
        merge_dict[key] = replace_dict[key]
    return merge_dict

def stack_ticks_into_chords(ticks):
    chords = [defaultdict(set)]
    tick_idx = 0
    while tick_idx < len(ticks):
        tick_num = ticks[tick_idx]['tick']
        chord = copy.deepcopy(chords[-1])
        some_turned_on = False
        while tick_idx < len(ticks) and ticks[tick_idx]['tick'] == tick_num:
            pitch = ticks[tick_idx]['pitch']
            channel = ticks[tick_idx]['channel']
            if ticks[tick_idx]['on'] is False:
                chord[channel].discard(pitch)# remove if exists
            else:
                some_turned_on = True
                chord[channel].add(pitch)
            tick_idx += 1

        if some_turned_on:
            chords.append(chord)
    return chords

def stack_ticks_into_chords_turn_off_when_channel_activates(ticks):
    chords = [defaultdict(set)]
    tick_idx = 50
    while tick_idx < len(ticks):
        tick_num = ticks[tick_idx]['tick']
        chord = defaultdict(set)
        some_turned_on = False
        while tick_idx < len(ticks) and ticks[tick_idx]['tick'] == tick_num:
            pitch = ticks[tick_idx]['pitch']
            channel = ticks[tick_idx]['channel']
            if ticks[tick_idx]['on'] is False:
                chord[channel].discard(pitch)# remove if exists
            else:
                some_turned_on = True
                chord[channel].add(pitch)
            tick_idx += 1

        if some_turned_on:
            chords.append(merge_dicts(chords[-1],chord))
    return chords

def stack_ticks_into_chords_turn_off_on_timeout(ticks, TICK_TIMOUT=0):
    chords = [defaultdict(dict)]
    tick_idx = 0
    while tick_idx < len(ticks):
        tick_num = ticks[tick_idx]['tick']
        chord = copy.deepcopy(chords[-1])
        for channel_pitchs in chord.values():
            for pitch, tick in list(channel_pitchs.items()):
                if tick + TICK_TIMOUT < tick_num:
                    del channel_pitchs[pitch]

        some_turned_on = False
        while tick_idx < len(ticks) and ticks[tick_idx]['tick'] == tick_num:
            pitch = ticks[tick_idx]['pitch']
            channel = ticks[tick_idx]['channel']
            if ticks[tick_idx]['on'] is False:
                if pitch in chord[channel]:
                    del chord[channel][pitch]
            else:
                chord[channel][pitch] = tick_num
                some_turned_on = True
            tick_idx += 1

        if some_turned_on:
            chords.append(chord)
    return chords

_methods_by_name = {
    "stack_ticks_into_chords":stack_ticks_into_chords,
    "stack_ticks_into_chords_turn_off_when_channel_activates":stack_ticks_into_chords_turn_off_when_channel_activates,
    "stack_ticks_into_chords_turn_off_on_timeout":stack_ticks_into_chords_turn_off_on_timeout,
}

def get_method_by_name(method_name):
    if method_name not in _methods_by_name:
        raise RuntimeError("bad chord to text strategy name. Options are:\n{}".format("\n".join(_methods_by_name.keys())))
    else:
        return _methods_by_name[method_name]
