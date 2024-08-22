import pygame
import sys
import array

import chip
from preferences import program_name, SCALE, fps, ON, OFF

# NOTE: Nearly everything you'd reasonably want to tweak is found in preferences.py


# disclaimer- I have a global 'game' loop because pygame doesn't support two windows run by one process

############################## 'game' loop

pygame.init()
pygame.display.set_caption("Anish's chip-8")

window_width = 64 * SCALE
window_height = 32 * SCALE
display = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Anish's Chip-8")

chip_8 = chip.Chip8()

clock = pygame.time.Clock()
sixtieth_second = pygame.USEREVENT + 1

pygame.time.set_timer(pygame.USEREVENT, 20)
pygame.mixer.init()
beep = pygame.mixer.Sound(array.array("b"))


# load programs
chip_8.load_program(program_name)


def draw_array(surface, array):
    for y, row in enumerate(array):
        for x, value in enumerate(row):
            color = ON if value else OFF  # White for True, Black for False
            pygame.draw.rect(surface, color, (x * SCALE, y * SCALE, SCALE, SCALE))


def get_keys_pressed() -> list[int]:
    acc = []
    keys = pygame.key.get_pressed()
    if keys[pygame.K_1]:
        acc.append(1)
    if keys[pygame.K_2]:
        acc.append(2)
    if keys[pygame.K_3]:
        acc.append(3)
    if keys[pygame.K_4]:
        acc.append(0xC)
    if keys[pygame.K_q]:
        acc.append(4)
    if keys[pygame.K_w]:
        acc.append(5)
    if keys[pygame.K_e]:
        acc.append(6)
    if keys[pygame.K_r]:
        acc.append(0xD)
    if keys[pygame.K_a]:
        acc.append(7)
    if keys[pygame.K_s]:
        acc.append(8)
    if keys[pygame.K_d]:
        acc.append(9)
    if keys[pygame.K_f]:
        acc.append(0xE)
    if keys[pygame.K_z]:
        acc.append(0xA)
    if keys[pygame.K_x]:
        acc.append(0)
    if keys[pygame.K_c]:
        acc.append(0xB)
    if keys[pygame.K_v]:
        acc.append(0xF)
    return acc


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

    redraw = chip_8.execute(chip_8.fetch(), get_keys_pressed())

    # if re.match('f.0a', chip_8.hex):
    #     debug = True
    #     print('debugging')
    # if not re.match('f.0a', chip_8.hex):
    #     debug = False

    clock.tick(fps)

    if redraw:
        draw_array(display, chip_8.display)
        pygame.display.update()
    # scaled_window = pygame.transform.smoothscale(
    #     chip_8.display.screen, (window_width, window_height)
    # )
    # bigger_window.blit(scaled_window, (0, 0))
    # pygame.display.flip()
    # pygame.display.update()


assert not running
pygame.quit()
sys.exit()
