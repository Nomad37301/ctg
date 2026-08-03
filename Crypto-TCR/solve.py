#!/usr/bin/env python3
# Solver untuk Challenge ROT13 - Caesar's Cousin

import codecs

ciphertext = "grpneg{e0g_guvegrra_vf_rnfl_crnfna}"

# ROT13 decode
flag = codecs.decode(ciphertext, 'rot_13')

print("=" * 40)
print("SOLVER - Caesar's Cousin")
print("=" * 40)
print(f"Ciphertext : {ciphertext}")
print(f"Plaintext  : {flag}")
print("=" * 40)
