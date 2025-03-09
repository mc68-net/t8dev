from    io  import BytesIO
import  builtins


class MBytesIO(BytesIO):
    ''' Extend the `BytesIO` API with some methods that make it more
        convenient to mutate its buffer. This covers typical actions we
        want to do during during unit tests such as clearing previous ouput
        in preparation to check new output, check what's been read, etc.

        XXX `MBytesIO`, indicating "mutable `BytesIO`" is not really
        a great name for this, but we've not been able to think up
        something better yet.
    '''

    def written(self, print=False):
        ''' Return all bytes written to this stream, with optional
            debugging printout.

            If `print` is `True`, this prints the the value to ``stdout``
            before returning. (ASCII visible chars  are printed as is;
            control characters and values ≥ 0x80 are printed in ``\\xNN``
            format.) This is useful to help debug what's going wrong in
            unit tests.

            With ``print=False`` this is an alias for `getvalue()`.
        '''
        b = self.getvalue()
        if print:
            s = b.decode('ISO-8859-1') \
                 .encode('unicode_escape') \
                 .decode('ISO-8859-1')
            builtins.print(s)
        return b

    def unread(self):
        ' Return all bytes not yet read from this stream. '
        return self.getvalue()[self.tell():]

    def clear(self):
        ''' Clear all collected output from the this `BytesIO`. This is
            typically used in multi-step unit tests that generate some
            output, check it, and then generate further output.
        '''
        self.seek(0)
        self.truncate(0)

    def setinput(self, bs:bytes):
        self.clear()
        self.write(bs)
        self.seek(0)
