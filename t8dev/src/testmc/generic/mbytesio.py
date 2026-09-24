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

            If `print` is `True`, this prints the value to ``stdout``
            before returning. (ASCII visible chars are printed as is;
            control characters and values ≥ 0x80 are printed as escape
            sequences (``\r`` etc.) This is useful to help debug what's
            going wrong in unit tests.

            With ``print=False`` this is an alias for `getvalue()`.
        '''
        b = self.getvalue()
        if print:
            #   For the printout we do not use errors='backslashreplace'
            #   because we want non-printing ASCII chars replaced as well:
            #   e.g., $00 printed as '\x00' rather than an actual NUL
            #   and $07 printed as '\a' rather than an actual BEL.
            s = b.decode('ISO-8859-1') \
                 .encode('unicode_escape') \
                 .decode('ISO-8859-1')
            builtins.print(s)
        return b

    def written_str(self, print=False):
        ''' As `written()` but return an ASCII string. Bytes ≥ $80 will be
            expanded to escape sequences of the form ``\\xHH`` where *HH*
            is always two lower-case hex digits.

            Note that this output is ambiguous: there's no way to tell
            whether `\\xff` in the return value was expanded from a printed
            $FF or was actually printed as those ASCII characters. If you
            need to check correctness of high-bit characters, use
            `written()` instead.

            `print` works as for `written()`. Note that the printed string
            will, unlike the returned string, also have non-printing ASCII
            chars replaced by escape sequences of ASCII backslash followed
            by a letter or hex output.
        '''
        return self.written(print).decode('ASCII', errors='backslashreplace')

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
