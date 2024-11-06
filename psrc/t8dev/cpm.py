def compile_submit(commands:str):
    ''' Given a sequence of commands, create the data for a ``$$$.SUB``
        file that the CP/M ``SUBMIT`` command would create for those. For
        convenience the commands are `str`s, but they must contain only
        ASCII characters, and they should not end with CR or newline
        characters.

        The resulting data can be placed in a ``$$$.SUB`` file on the
        A: drive of a CP/M system and the commands will be executed
        when the system starts (including warm starts).
    '''
    sub = bytearray()
    for cmd in reversed(commands):
        sub.append(len(cmd))
        sub += cmd.encode('ASCII')
        sub += b'\x00' * (128 - 1 - len(cmd))
    return bytes(sub)
