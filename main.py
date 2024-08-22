import pygame
import sys
import array

import chip
from preferences import program_name, window_width, window_height, fps

# NOTE: Nearly everything you'd reasonably want to tweak is found in preferences.py

chip_8 = chip.Chip8()

# disclaimer- I have a global 'game' loop because pygame doesn't support two windows run by one process

############################## 'game' loop

clock = pygame.time.Clock()
sixtieth_second = pygame.USEREVENT + 1

pygame.time.set_timer(pygame.USEREVENT, 20)
pygame.mixer.init()
beep = pygame.mixer.Sound(array.array("b"))


# load programs
chip_8.load_program(program_name)

bigger_window = pygame.display.set_mode((window_width, window_height))

debug = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # if event.type == pygame.USEREVENT:
        #     chip_8.delay_timer -= 1
        #     chip_8.sound_timer -= 1
        #     if chip_8.delay_timer == 0:
        #         beep.play()
        #         chip_8.delay_timer = 60
        #         chip_8.sound_timer = 60
    chip_8.delay_timer -= 1
    chip_8.sound_timer -= 1
    if chip_8.delay_timer < 0:
        beep.play()
        chip_8.delay_timer = 60
        chip_8.sound_timer = 60
    if debug:
        a = "{0:04x}".format(chip_8.pc)
        a1 = "{0:04x}".format(chip_8.pc - 0x200)
        b = "{0:04x}".format((chip_8.mem[chip_8.pc] << 8) + chip_8.mem[chip_8.pc + 1])
        print(f"next line to execute is {a} ({a1})")
        print(f"next byte to execute is {b}")
        user_in = input("enter to continue/view\n")
        while user_in != "":
            if user_in == "i":
                print(chip_8.I)
            else:
                user_in = int(user_in, base=16)
                if user_in in chip_8.registers:
                    print(chip_8.registers[user_in])
            user_in = input("enter to continue/view\n")

    chip_8.execute(chip_8.fetch())

    # if re.match('f.0a', chip_8.hex):
    #     debug = True
    #     print('debugging')
    # if not re.match('f.0a', chip_8.hex):
    #     debug = False

    clock.tick(fps)
    scaled_window = pygame.transform.smoothscale(
        chip_8.display.screen, (window_width, window_height)
    )
    bigger_window.blit(scaled_window, (0, 0))
    pygame.display.flip()
    pygame.display.update()


assert not running
pygame.quit()
sys.exit()
