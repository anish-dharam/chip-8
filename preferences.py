# 'bnnn' setting: set to false if using the chip-48/super-chip interpretation of this instruction
offset_jump_original = True

# if offset_jump_original is true: the 'bnnn' instruction will jump to the address nnn + the value in register v0
# otherwise: the instruction 'bxnn' will jump to the address xnn plus the value in the register vx

# '8xy6' and '8x7e' setting: set to false if using the chip-48/super-chip version of this instruction
shift_original = True

# if shift_original is true: the '8xy6/e' instruction will set vx to vy and then shift left/right
# otherwise: the instruction will shift vx in place (ignoring y)

# 'fx55' and 'fx65' setting: set to true if using the original chip-8 version of this instruction
# store_and_load_memory_original = False
store_and_load_memory_original = True

# if store_and_load_memory_original is true: the instructions will not mutate I
# if false, they will mutate I

fps = 1700

window_height = 512  # know that the width will be twice this
window_width = 2 * window_height

# change these values if you want different display colors (pygame specific feature)
on = (255, 255, 255)
off = (0, 0, 0)

# change this value to load different programs
program_name = "PATH_HERE"
