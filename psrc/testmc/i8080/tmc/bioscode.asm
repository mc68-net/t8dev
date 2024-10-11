;   "BIOS" for testmc.i8080 simulator
;   Used for unit tests and command-line use.

            relaxed on
            cpu 8080
            z80syntax exclusive
            include "testmc/i8080/tmc/bios.i80"

;   This file will be loaded into memory along with the code under test.
;   It may also be useful to merge their symbols, so we use a separate section
;   for this file's symbols to help avoid conflicts.
;
            section  tmc_i8080_BIOS

; ----------------------------------------------------------------------
;   We use this assertdef after every routine to confirm that our local
;   definition of a symbol matches the global definition from the "include"
;   file (i.e., we ORG'd it correctly) and that we're not accidently
;   overwriting the previous routine when we ORG'd for the new routine.
;
assertdef       macro   sym,{NOEXPAND}
                ;   Ensure that code is where the header says it is.
                if sym <> sym[parent]
                    error "sym=\{sym} <> sym[parent]=\{sym[parent]}"
                endif
               ;warning "last=\{_ad_lastaddr}  sym=\{sym}  $=\{$}"
                ;   Ensure we've not overwritten previous code: the newly
                ;   defined symbol must be at or after the current address
                ;   at the last call to this macro.
                if sym < _ad_lastaddr
                    error "code overlap: last PC=\{_ad_lastaddr} sym=\{sym}"
                endif
                ;   Update our last address to cover the code that was just
                ;   generated and checked.
_ad_lastaddr    set $
                endm

_ad_lastaddr    set 0

; ----------------------------------------------------------------------

            org  prchar
prchar      ld   (charoutport),a
            ret
            assertdef prchar

            org  rdchar
rdchar      ld   a,(charinport)
            ret
            assertdef rdchar

;   Print a platform-appropriate newline.
;   For Unix this is just an LF because output is not raw mode.
            org  prnl
prnl        ld   a,$0A               ; LF
            jp   prchar
            assertdef prnl

            org  errbeep
errbeep     ld   a,$07              ; BEL
            jp   prchar
            assertdef errbeep

            endsection  ; tmc_i8080_BIOS
