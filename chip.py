from collections import deque
import pygame
import sys
import re
from random import randrange

import components
from preferences import (
    offset_jump_original,
    shift_original,
    store_and_load_memory_original,
    on,
    off,
)


class Chip8:
    def __init__(self):
        comps = components.Components()
        self.mem = comps.mem
        self.stack = comps.stack

        self.I = comps.I
        self.pc = comps.pc
        self.display = comps.display
        self.registers = comps.registers

        self.delay_timer = comps.delay_timer
        self.sound_timer = comps.sound_timer

    def fetch(self):
        res = (self.mem[self.pc] << 8) + self.mem[self.pc + 1]
        self.pc += 2
        return res

    def decode(self, num: int):
        binary = "{0:016b}".format(num)
        binary = [int(digit) for digit in binary]

        self.hex = "{0:04x}".format(num)

        self.x = binary[4] * 8 + binary[5] * 4 + binary[6] * 2 + binary[7]
        self.y = binary[8] * 8 + binary[9] * 4 + binary[10] * 2 + binary[11]
        self.n = binary[12] * 8 + binary[13] * 4 + binary[14] * 2 + binary[15]
        self.nn = (self.y << 4) + self.n
        self.nnn = (self.x << 8) + (self.y << 4) + self.n

        self.vx = self.registers[self.x]
        self.vy = self.registers[self.y]

    def execute(self, num: int):
        opcode = "{0:04b}".format(num // 4096)

        match opcode[0]:
            case "0":
                self.opcode_zero(num)
            case "1":
                self.opcode_one(num)
            case _:
                print(f"opcode neither 0 nor 1: {'{0:04x}'.format(num)}")
                pygame.quit()
                exit()

    def opcode_zero(self, num: int):
        self.decode(num)

        hex_match = lambda pattern: re.match(pattern, self.hex)

        if hex_match("00e0"):  # clear screen
            self.display.clear_screen()
        elif hex_match("1..."):  # jump
            self.pc = self.nnn
        elif hex_match("2..."):  # call subroutine
            self.stack.append(self.pc)
            self.pc = self.nnn
        elif hex_match("00ee"):  # return address, pop stack frame, etc...
            self.pc = self.stack.pop()
        # the following four instructions are conditional skips
        elif hex_match("3..."):
            if self.vx == self.nn:
                self.pc += 2  # addresses one byte, and each instruction is two so we increment by two
        elif hex_match("4..."):
            if self.vx != self.nn:
                self.pc += 2
        elif hex_match("5..0"):
            if self.vx == self.vy:
                self.pc += 2
        elif hex_match("6..."):  # set vx
            self.registers[self.x] = self.nn
        elif hex_match("7..."):  # increment vx
            self.registers[self.x] += self.nn
            if self.registers[self.x] >= 256:  # only an 8-bit register
                self.registers[self.x] -= 256
        else:
            print(f"Unknown instruction with opcode 0: {self.hex}")
            pygame.quit()
            exit()

    def opcode_one(self, num: int):
        self.decode(num)
        hex_match = lambda pattern: re.match(pattern, self.hex)

        if hex_match("8..."):  # arithmetic or logic
            eight_match = lambda pattern: re.match(pattern, self.hex[1:])
            if eight_match("..0"):  # set
                self.registers[self.x] = self.vy
            elif eight_match("..1"):  # binary OR
                self.registers[self.x] = self.vx | self.vy
            elif eight_match("..2"):  # binary AND
                self.registers[self.x] = self.vx & self.vy
            elif eight_match("..3"):  # bitwise XOR
                self.registers[self.x] = self.vx ^ self.vy
            elif eight_match("..4"):  # add
                res = self.vx + self.vy
                if res > 255:
                    res -= 256
                    self.registers[0xF] = 1
                self.registers[self.x] = res

            elif eight_match("..5"):  # vx - vy
                if self.vx >= self.vy:
                    self.registers[0xF] = 1
                else:
                    self.registers[0xF] = 0
                self.registers[self.x] = self.vx - self.vy
            elif eight_match("..7"):  # vy - vx
                if self.vy >= self.vx:
                    self.registers[0xF] = 1
                else:
                    self.registers[0xF] = 0
                self.registers[self.x] = self.vy - self.vx
            elif eight_match("..6"):  # shift
                if not shift_original:
                    self.registers[self.x] = self.vy
                if self.registers[self.x] % 2 == 1:  # rightmost bit is 1
                    self.registers[0xF] = 1
                    self.registers[self.x] -= 1
                else:  # rightmost bit is 0
                    self.registers[0xF] = 0
                self.registers[self.x] >>= 1
            elif eight_match("..e"):  # shift
                if not shift_original:
                    self.registers[self.x] = self.vy
                if self.registers[self.x] >= 128:  # leftmost bit is 1
                    self.registers[0xF] = 1
                    self.registers[self.x] -= 128
                else:  # leftmost bit is 0
                    self.registers[0xF] = 0
                self.registers[self.x] <<= 1
            else:
                print(f"Unknown instruction starting with 8: {self.hex}")
                pygame.quit()
                exit()

        elif hex_match("9..0"):
            if self.vx != self.vy:
                self.pc += 2
        elif hex_match("a..."):  # set index
            self.I = self.nnn
        elif hex_match("b..."):  # jump with offset
            if offset_jump_original:
                self.pc = self.nnn + self.registers[0]
            else:
                self.pc = ((self.x << 8) + self.nn) + self.vx
        elif hex_match("c..."):  # random
            self.registers[self.x] = randrange(256) & self.nn

        elif hex_match("d..."):  # draw
            self.registers[0xF] = 0
            for row in range(self.n):
                # byte from which we want to pull pixels (which are either on or off)
                to_draw = [
                    int(digit) for digit in "{0:08b}".format(self.mem[self.I + row])
                ]
                for column in range(8):  # looping through every bit in to_draw
                    pos = ((self.vx + column) % 64, (self.vy + row) % 32)
                    if pos[0] < 0 or pos[1] < 0:
                        raise ValueError("something has gone horribly wrong")
                    if pos[0] >= 64 or pos[1] >= 32:
                        break
                    if not to_draw[column]:
                        continue  # sprite pixel is off
                    # now we know that the sprite pixel is on
                    if self.display.screen.get_at(pos) == on:
                        self.registers[0xF] = 1  # pixel flip!
                        self.display.screen.set_at(pos, off)
                    else:
                        assert self.display.screen.get_at(pos) == off
                        self.display.screen.set_at(pos, on)
        elif hex_match("e.9e"):  # skip if correct key pressed
            if self.vx in get_keys_pressed():
                self.pc += 2
        elif hex_match("e.a1"):  # skip if correct key not pressed
            if self.vx not in get_keys_pressed():
                self.pc += 2
        elif hex_match("f..."):  # f opcode
            f_match = lambda pattern: re.match(pattern, self.hex[1:])
            if f_match(".07"):  # vx set to delay timer value
                self.registers[self.x] = self.delay_timer
            elif f_match(".15"):  # delay timer set to vx
                self.delay_timer = self.vx
            elif f_match(".18"):  # sound timer set to vx
                self.sound_timer = self.vx
            elif f_match(".1e"):  # add vx to I
                self.I += self.vx
                if self.I >= 65536:
                    self.registers[0xF] = 1
                    self.I -= 65536
                if self.I >= 4096:
                    self.registers[0xF] = 1
            elif f_match(".0a"):  # get key
                pressed = get_keys_pressed()
                if pressed:
                    self.registers[self.x] = pressed[0]
                    return
                self.pc -= 2
            elif f_match(".29"):  # font character
                if type(self.vx) is str:
                    print(f"\n\n\n\n\n\n\n\n{self.vx}\n\n\n\n\n\n\n")
                self.I = 0x50 + (5 * (self.vx & 0b1111))
            elif f_match(".33"):  # decimal conversion, store in memory
                string = "{0:03d}".format(self.vx)
                self.mem[self.I] = int(string[0])
                self.mem[self.I + 1] = int(string[1])
                self.mem[self.I + 2] = int(string[2])
            elif f_match(".55"):  # store register to memory
                for j in range(self.x + 1):
                    self.mem[self.I + j] = self.registers[j]
                    # self.mem[self.I + j] = "{0:02x}".format(self.registers[j])
                if store_and_load_memory_original:
                    self.I += self.x + 1
            elif f_match(".65"):  # store register to memory
                for j in range(self.x + 1):
                    self.registers[j] = self.mem[self.I + j]
                if store_and_load_memory_original:
                    self.I += self.x + 1
            else:
                print(f"Unknown instruction starting with f: {self.hex}")
                pygame.quit()
                exit()
        else:
            print(f"Unknown instruction with opcode 1: {self.hex}")
            pygame.quit()
            exit()

    def load_program(self, filename, start_index=0x200):
        # start_index is 0x200 by default because that is chip8 convention
        # 0x50 to 0x9f is used for fonts, so do not load a program into that chunk of memory!
        with open(filename, "rb") as f:
            for j, byte in enumerate(f.read()):
                self.mem[start_index + j] = byte
        self.pc = start_index

    def print_state(self):
        for key in self.registers:
            print(f"register {key}: {self.registers[key]}")
        print(f"I: {self.I}")
        print(f"pc: {self.pc}")
        print(f"last executed instruction: {self.hex}")
        print(f"stack: {self.stack}")


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
