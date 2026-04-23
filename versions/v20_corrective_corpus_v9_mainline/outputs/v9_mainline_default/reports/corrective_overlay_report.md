# v20 corrective corpus v9 mainline overlay report

## Strategy

- Keep the token-safe v7 donor backbone exactly as the public-safe base overlay.
- Do not add any new broad BIT exact lane beyond the audited v7 donor pack.
- Do not add any new symbol exact lane in the mainline branch.
- Reintroduce only the A-Open-style matching auxiliary curriculum that is absent from the local 04-08-16-14 base snapshot.
- Extract matching sections only from the 240 binary origin IDs already carried by the v7 token-safe overlay.
- Reuse base synthetic token streams only for v4_public_base rows; retokenize donor rows and all matching auxiliaries from their own text.

## Source mix

- v4_public_base: 808
- v6_binary_donor: 27
- v6_numeral_surface_donor: 10
- v7_numeral_surface_synth: 1
- v9_bit_matching_aux: 543

## Matching auxiliary lane

- binary origin IDs: 240
- all extracted sections: 2160
- informative sections: 739
- kept sections after A-Open downsampling: 543
- missing reasoning files: 0

### Kept by section

- AND: 81
- AND-NOT: 89
- Constant: 17
- Identity: 133
- NOT: 7
- OR: 78
- OR-NOT: 68
- XOR: 40
- XOR-NOT: 30

## Footprint

- overlay token strategy: reuse_base_synthetic
- overlay reuse scope: v4_public_base_only
- reused base synthetic examples: 768
- retokenized overlay examples: 621
- unique rows: 881
- repeated rows: 1389
- total tokens: 33305836
- total steps: 289
- max seq len: 7971
