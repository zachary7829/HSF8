#Thanks to https://www.freecodecamp.org/news/creating-your-very-own-chip-8-emulator/, great reference
#+, thanks to r/EmuDev discord, more specifically calc84maniac#7184, I spent 5 hours trying to figure out why sprite draw didn't work only to figure out it was a one line indentation error :P
#This emulator is only to be used as an example as 'Just Enough For IBM' - for a better full CHIP-8 emulator try my HSF8, https://github.com/zachary7829/HSF8/blob/main/emu.py
from tkinter import *
import math
import time
import random
import sys

#screen
cols = 64
rows = 32
scale = 4

screen = Tk()
screen.title('JEFIBM by zachary7829')
screen.geometry(str(cols*scale)+'x'+str(rows*scale))
screen.config(bg='#000000')

canvas = Canvas(screen,bg="#000000")

def drawPixel(x, y): #col is x row is y
  canvas.create_rectangle(
    x*scale, y*scale, (x*scale)+scale, (y*scale)+scale,
    fill="white",
    tag="squa"
    )
  canvas.pack()
  screen.update()

def cls():
  canvas.delete('all')
  
def excopcode(opcode):
  global pc
  global v
  global selfi
  pc += 2

  x = (opcode & 0x0F00) >> 8
  #x - A 4-bit value, the lower 4 bits of the high byte of the instruction
  y = (opcode & 0x00F0) >> 4
  #y - A 4-bit value, the upper 4 bits of the low byte of the instruction
  code = opcode & 0xF000
  #to check code without nnn
  kk = opcode & 0xFF
  #kk or byte - An 8-bit value, the lowest 8 bits of the instruction

  print("executing " + str(hex(opcode)))
  if code == 0x0000:
    if opcode == 0x00E0: #cls
      cls()
  elif code == 0x1000: #JP addr
    pc = opcode & 0xFFF

  elif code == 0x6000: #LD Vx, byte
    v[x] = kk
    
  elif code == 0x7000: #ADD Vx, byte
    v[x] += kk

  elif code == 0xA000:
    selfi = opcode & 0xFFF
    
  elif code == 0xD000: #DRW Vx, Vy, nibble
    width = 8
    height = opcode & 0xF
    v[0xF] = 0
    for row in range(height):
      sprite = memory[selfi+row]
      for col in range(width):
        if (sprite & 0x80) > 0:
          if drawPixel(v[x]+col, v[y]+row):
            v[0xF] = 1
        sprite <<= 1

  else:
    print("unknown opcode: "+ str(hex(opcode)))

memory = [0x0 for i in range(4096)]
filename = input("Input rom name: ") + ".ch8"
dafile = open(filename, 'rb')
program = dafile.read()
dafile.close()
pc = 0x200
v = [0x0 for i in range(16)] #16 8 bit registers selfii = 0 #Stores memory addresses. Set this to 0 since we aren't storing anything at initialization. cycle = True
for i in range(len(program)):
  memory[0x200+i] = program[i]
while True:
    daopcode = memory[pc] << 8 | memory[pc+1]
    print(pc) #useful for debugging to see where your program is
    excopcode(daopcode)